import re
import eel
import time
import config
import selenium
import amazon_config
import sentiment_analyser
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common import TimeoutException
from selenium.webdriver import Keys, ActionChains
from selenium.webdriver.chrome.options import Options


def generate_driver():
    """Generating driver instances"""
    chromeOption = Options()
    chromeOption.add_argument("--headless")
    chromeOption.add_argument("--window-size=1600,1200")
    chromeOption.add_argument("--mute-audio")
    chromeOption.add_argument("--log-level=3")
    chromeOption.add_argument("--silent")
    chromeOption.add_argument("--disable-blink-features=AutomationControlled")
    chromeOption.add_experimental_option(
        "excludeSwitches", ['enable-automation'])
    driver = webdriver.Chrome(options=chromeOption)
    return driver


def accept_cookies(driver):
    """Clicking Accept cookies box on Amazon Page"""
    try:
        time.sleep(1)
        ActionChains(driver).move_to_element(
            driver.find_element(By.CSS_SELECTOR, "input[id='sp-cc-accept']")).click().perform()
        print('\nCookies accepted')
        time.sleep(1)
    except selenium.common.exceptions.NoSuchElementException:
        try:
            eel.update_text("RETRYING COOKIE CLICK")
            driver.refresh()
            time.sleep(1)
            ActionChains(driver).move_to_element(
                driver.find_element(By.CSS_SELECTOR, "input[id='sp-cc-accept']")).click().perform()
        except selenium.common.exceptions.NoSuchElementException:
            eel.update_text("SOMETHING WENT WRONG")
            print("Couldn't accept cookies")
            driver.quit()


def generate_class(raw_class):
    """Adds '.' to a give class string and returns it"""
    return raw_class.replace(' ', '.')


def search_item(driver):
    """Inserts search item into Amazon search bar"""
    search_box = driver.find_element(By.ID, 'twotabsearchtextbox')
    search_box.click()
    time.sleep(0.5)
    search_box.send_keys(config.search_term)
    search_box.send_keys(Keys.ENTER)


def title_filtering(title):
    """Conditions that a title must meet to pass filtration"""
    a = re.search(config.search_term, title, re.IGNORECASE)
    b = all(substring.lower() in title.lower() for substring in config.term_substrings_by_delimiters)
    c = all(substring.lower() in title.lower() for substring in config.term_substrings_spaced)
    return a or b or c


def get_product_info(driver):
    """Retrieves product: listing title,number of reviews and product link"""
    # click one star and up button to show reviews that have a review number count
    time.sleep(1)
    driver.find_element(By.CSS_SELECTOR, "section[aria-label='1 Star & Up']").click()
    time.sleep(1)

    # get web elements of item listings titles
    # get web elements of review number counts
    # get parent element for each title listing element which will be the element that holds the listing link
    titles = driver.find_elements(By.CLASS_NAME, generate_class('a-size-medium a-color-base a-text-normal'))[:5]
    number_of_reviews = [item for item in driver.find_elements(By.CSS_SELECTOR, ".a-size-base.s-underline-text") if
                         item.tag_name == "span"][:5]
    links = [item.find_element(By.XPATH, './..') for item in titles][:5]

    # extracting raw text from elements
    titles = [item.text for item in titles]
    number_of_reviews = [item.text for item in number_of_reviews]

    try:
        number_of_reviews = [int(value.replace(",", "")) if "," in value else int(value) for value in number_of_reviews]
    except ValueError:
        number_of_reviews = []

    links = [item.get_attribute("href") for item in links]

    # prints initial state of elements
    print(f'\nInitial - {len(titles)} : {len(number_of_reviews)} : {len(links)}')
    for t, nr, l in zip(titles, number_of_reviews, links):
        print(f'{t:<150}:{nr:<6}: {l}')

    # method of obtaining review numbers above known to be inconsistent but faster if it fails try longer but consistent approach
    if len(number_of_reviews) == 0:
        print("\nFailed to obtain number of ratings. Trying alternative approach...")
        number_of_reviews = review_number_failsafe(number_of_reviews, links)

    # find indexes of titles that don't contain search term
    indexes = []
    for i, title in enumerate(titles):
        if not title_filtering(title):
            indexes.append(i)

    # synchronize lists by removing items that correspond to a title that doesn't contain search term
    for index in sorted(indexes, reverse=True):
        try:
            del titles[index]
            del number_of_reviews[index]
            del links[index]
        except IndexError:
            eel.update_text("NO LISTINGS FOUND")

    # prints state of elements after filtering for irrelevant titles
    print(f'\nFiltered - {len(titles)} : {len(number_of_reviews)} : {len(links)}')
    for title, review_number, link in sorted(zip(titles, number_of_reviews, links), key=lambda x: x[1], reverse=True):
        print(f'{title:<150}:{review_number:<6}: {link}')

    # return sorted dict of (no. reviews : product link) in descending order
    return {k: v for k, v in sorted(dict(zip(number_of_reviews, links)).items(), reverse=True)}


def review_number_failsafe(review_numbers, product_links):
    """Alternative method of getting number of ratings if initial method fails.
    Will instead load each product page individually and scrape number of ratings from there rather than product results page."""
    for link in product_links:
        driver = generate_driver()
        try:
            driver.get(link)
            review_numbers.append(
                driver.find_element(By.ID, "acrCustomerReviewText").text.split(" ")[0].replace(",", ""))
            driver.quit()
        except (selenium.common.exceptions.InvalidArgumentException, selenium.common.exceptions.NoSuchElementException):
            eel.update_text("INVALID ITEM. PRESS F5 TO RETURN")
            driver.quit()

    if len(review_numbers) > 0:
        print("Alternate approach successful")
    else:
        print("Both approaches failed.")
    return review_numbers


def scrape_reviews(link):
    """Review page scraper. Starting from the product page will look for see all reviews button; check if a product has styles to filter reviews and store the comments"""
    global scraped_reviews
    clicked_translate = False
    driver = generate_driver()
    driver.get(link)
    accept_cookies(driver)

    # clicks See all reviews at bottom of product page
    scroll_bottom(driver)
    try:
        ActionChains(driver).move_to_element(
            driver.find_element(By.CSS_SELECTOR, "a[data-hook = 'see-all-reviews-link-foot']")).click().perform()
    except selenium.common.exceptions.NoSuchElementException:
        eel.update_text("NO REVIEWS FOR ITEM. PRESS F5 TO RETURN")

    # focuses on region header so reviews are in DOM
    ActionChains(driver).move_to_element(
        driver.find_element(By.CSS_SELECTOR, "h3[data-hook='arp-local-reviews-header']")).click().perform()
    time.sleep(1)

    # If product has style selection I.e. ryzen cpu range, filter the reviews for the model specifically searched for
    if check_style(driver):
        time.sleep(1)
        driver.find_element(By.XPATH, '//*[@id="format-type-dropdown"]/option[2]').click()

    # Loop that performs scraping
    for _ in range(int(amazon_config.pagination_depth)):

        # check if translation button has already been clicked if not, check if translation button is present
        if clicked_translate is False:
            clicked_translate = attempt_translation(driver)
        time.sleep(1)

        # Extract reviews from page
        reviews = driver.find_elements(By.CSS_SELECTOR, "span[data-hook='review-body']")
        print(f"PAGE [{_ + 1}]")
        eel.update_text(f"SCRAPING PAGE {_ + 1}")
        for review in reviews:
            try:
                scraped_reviews.append(review.text)
            except selenium.common.exceptions.StaleElementReferenceException:
                pass

        # Process reviews
        for rev in scraped_reviews:
            sanitised_comment = sentiment_analyser.pre_process(rev)
            if len(sanitised_comment) <= 350:
                handle_mode(sanitised_comment)
        scraped_reviews = []

        # If last page of pagination has been reached, stop looping else keep scraping till pagination depth
        if len(driver.find_elements(By.CLASS_NAME, generate_class("a-disabled a-last"))) > 0:
            break
        elif len(driver.find_elements(By.CLASS_NAME, 'a-last')) == 0:
            break
        else:
            scroll_bottom(driver)
            driver.find_element(By.CLASS_NAME, 'a-last').click()
            time.sleep(1)
    driver.quit()


def handle_mode(sanitised_comment):
    """Handles comment processing after data has been collected depending on user sentiment analysis method chosen"""
    if amazon_config.sentiment_mode == "vader":
        config.sanitised_amazon[sanitised_comment] = sentiment_analyser.vader_analyze_sentiment(sanitised_comment)
    elif amazon_config.sentiment_mode == "roberta":
        roberta.append(sanitised_comment)


def check_style(driver):
    """Checks if product has style options and filters for relevant item"""
    try:
        handle_style = driver.find_element(By.ID, "format-type-dropdown")
        print("\nThis product uses style options...\n")
        print(handle_style.text)
        return True
    except selenium.common.exceptions.NoSuchElementException:
        print("\nThis product doesn't have style options...")
        return False


def attempt_translation(driver):
    """Attempts to translate reviews if page has non english comments"""
    try:
        driver.find_element(By.CSS_SELECTOR, "a[data-hook='cr-translate-these-reviews-link']").click()
        print("\nReviews will now be translated to English after first encounter of Non-English review...")
        time.sleep(1)
        return True
    except selenium.common.exceptions.NoSuchElementException:
        print('\nNo comments need translating on this page...\n')
        return False
    except selenium.common.exceptions.StaleElementReferenceException:
        return False


def scroll_custom(driver, height):
    """Scroll a certain amount down on a page"""
    driver.execute_script(f"window.scrollTo(0, {height});")
    time.sleep(1)


def scroll_bottom(driver):
    """Scroll to the bottom of a page"""
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(1)


@eel.expose
def run_amazon():
    """Method that begins scraping process"""
    st = time.perf_counter()

    eel.update_text("GENERATING DRIVER")
    browser = generate_driver()

    browser.get("https://www.amazon.co.uk/")

    eel.update_text("ACCEPTING COOKIES")
    accept_cookies(browser)

    eel.update_text(f"SEARCHING FOR '{config.search_term}' LISTINGS")
    search_item(browser)

    # List of links product links in descending order of number of ratings
    link_list = get_product_info(browser)
    browser.quit()

    eel.update_text("SCRAPING REVIEWS")

    try:
        time.sleep(1)
        scrape_reviews(list(link_list.values())[0])  # Passes link of listing with most reviews for scraping
    except IndexError:
        eel.update_text("INVALID ITEM. PRESS F5 TO RETURN")
    print(f'Time Taken In Seconds: {str(round(time.perf_counter() - st, 2))}\n')

    if amazon_config.sentiment_mode == "roberta":
        sentiment_analyser.roberta_analyze_sentiment(roberta, config.sanitised_amazon)

    config.generate_report(amazon_config.sentiment_mode, config.sanitised_amazon, "Amazon")


roberta = []
scraped_reviews = []
