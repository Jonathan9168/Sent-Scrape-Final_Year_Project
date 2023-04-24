import re
import eel
import time
import config
import selenium
import twitter_config
import sentiment_analyser
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

roberta = []
query = f'{config.search_term} "{config.search_term}" until:2022-12-12 since:2016-01-01 lang:en -filter:links -filter:retweets'


def generate_search_url():
    """Generating Twitter search URL"""
    URL = "https://twitter.com/search?q=%22"
    for word in config.term_substrings_spaced:
        if word is config.term_substrings_spaced[-1]:
            URL += word + '%22%20lang%3Aen%20-filter%3Alinks%20-filter%3Aretweets&src=recent_search_click'
        else:
            URL += word + "%20"
    if "#" in URL:
        URL = URL.replace("#", "%23")
    return URL


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


def accept_cookies(driver):
    """Clicking Accept cookies box on Twitter search page"""
    try:
        cookie_class = 'css-18t94o4 css-1dbjc4n r-42olwf r-sdzlij r-1phboty r-rs99b7 r-18kxxzh r-1q142lx r-eu3ka r-5oul0u r-2yi16 r-1qi8awa r-1ny4l3l r-ymttw5 r-o7ynqc r-6416eg r-lrvibr r-lif3th'
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.CLASS_NAME, cookie_class.replace(' ', '.')))).click()
    except TimeoutException:
        print("Wasn't able to accept cookies...")
        driver.quit()


def get_comments(driver):
    """Gets Twitter cards in between scrolling as once scrolled past, tweets are lost."""

    tweet_cards = driver.find_elements(By.CSS_SELECTOR, '[data-testid="tweetText"]')
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

    print(f'Scraping Twitter for: {query}')

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
    st = time.perf_counter()
    global query, roberta
    roberta = []
    eel.update_text("GENERATING DRIVER")
    browser = generate_driver()
    eel.update_text("BUILDING SEARCH URL")
    search_URL = generate_search_url()
    print(search_URL)
    browser.get(search_URL)
    eel.update_text("ACCEPTING COOKIES")
    accept_cookies(browser)
    eel.update_text("SCRAPING TWEETS")
    query = f'{config.search_term} "{config.search_term}" until:2022-12-12 since:2016-01-01 lang:en -filter:links -filter:retweets'
    scroll(twitter_config.comment_depth, browser)
    browser.quit()
    print(f'\nTime Taken In Seconds: {str(round(time.perf_counter() - st, 2))}\n')

    if twitter_config.sentiment_mode == "roberta":
        sentiment_analyser.roberta_analyze_sentiment(roberta, config.sanitised_twitter)

    config.generate_report(twitter_config.sentiment_mode, config.sanitised_twitter, "Twitter")
