import re
import eel
import time
import config
import selenium
import twitter_config
import sentiment_analyser
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.common import TimeoutException
from selenium.webdriver.chrome.options import Options

roberta = []


def generate_search_query():
    """Generating Nitter search query"""
    return f'{config.search_term} "{config.search_term}" lang:en -filter:links -filter:retweets'


def generate_driver():
    """Generating driver instances"""
    chromeOption = Options()
    chromeOption.add_argument("--headless")
    chromeOption.add_argument("--window-size=1920,1080")
    chromeOption.add_argument("--mute-audio")
    chromeOption.add_argument("--log-level=3")
    chromeOption.add_argument("--silent")
    driver = webdriver.Chrome(options=chromeOption)
    return driver


def apply_scroll_cookie(driver):
    """Applies the infinite scroll cookie on Nitter"""

    # Set the desired cookie
    cookie = {'name': 'infiniteScroll', 'value': 'on', 'domain': 'nitter.net'}
    driver.get('https://nitter.net')

    # Add the cookie to the browser
    driver.add_cookie(cookie)
    driver.refresh()

    time.sleep(0.5)
    return driver


def search_for_query(driver, query):
    driver.get('https://nitter.net/search')
    search_box = driver.find_element(By.NAME, 'q')
    search_box.send_keys(query)
    search_box.send_keys(Keys.ENTER)
    time.sleep(0.5)
    return driver


def get_comments(driver):
    """Gets Twitter cards in between scrolling as once scrolled past, tweets are lost."""

    tweet_cards = driver.find_elements(By.CSS_SELECTOR, '[class="tweet-content media-body"]')
    for card in tweet_cards:
        try:
            sanitised_comment = sentiment_analyser.pre_process_twitter(card.text)
            if check_conditions(sanitised_comment):
                if twitter_config.sentiment_mode == "vader":
                    config.sanitised_twitter[sanitised_comment] = sentiment_analyser.vader_analyze_sentiment(
                        sanitised_comment)
                elif twitter_config.sentiment_mode == "roberta":
                    roberta.append(sanitised_comment)
        except selenium.common.exceptions.StaleElementReferenceException:
            pass


def check_conditions(comment):
    """Conditions that a comment must meet to pass filtration"""
    a = re.search(config.search_term, comment, re.IGNORECASE)
    b = any(substring in comment for substring in config.term_substrings_by_delimiters)
    c = any(substring in comment for substring in config.term_substrings_spaced)
    return a or b or c


def scroll(scrolls, driver):
    """Scrolls down a given amount of times for a webdriver to load comments
    Scrolls --> Number of scrolls to do (More scrolls = longer runtime)
    browser --> Webdriver instance"""

    print(f'Scraping Twitter for: {config.search_term}')

    for _ in range(int(scrolls)):
        print(f'PASS [{_ + 1}/{twitter_config.comment_depth}]')
        eel.update_text(f'PASS [{_ + 1}/{twitter_config.comment_depth}]')
        get_comments(driver)
        scroll_height = 1600
        document_height_before = driver.execute_script("return document.documentElement.scrollHeight")
        driver.execute_script(f"window.scrollTo(0, {document_height_before + scroll_height});")
        time.sleep(1)


@eel.expose
def run_twitter():
    """Method that begins scraping process"""
    st = time.perf_counter()
    global roberta
    roberta = []

    eel.update_text("GENERATING DRIVER")
    driver = generate_driver()

    eel.update_text("SETTING INFINITE SCROLL COOKIE")
    driver = apply_scroll_cookie(driver)

    eel.update_text("BUILDING SEARCH QUERY")
    search_query = generate_search_query()
    print(search_query)

    eel.update_text(f"SEARCHING FOR {config.search_term.upper()}")
    driver = search_for_query(driver, search_query)

    eel.update_text("SCRAPING TWEETS")
    scroll(twitter_config.comment_depth, driver)
    driver.quit()

    print(f'\nTime Taken In Seconds: {str(round(time.perf_counter() - st, 2))}\n')

    if twitter_config.sentiment_mode == "roberta":
        sentiment_analyser.roberta_analyze_sentiment(roberta, config.sanitised_twitter)

    config.generate_report(twitter_config.sentiment_mode, config.sanitised_twitter, "Twitter")
