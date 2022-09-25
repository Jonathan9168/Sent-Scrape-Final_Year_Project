import eel
import time
import config
import threading
import youtube_config
import sentiment_analyser
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

"""browser = threadBrowser = driver"""

st = time.perf_counter()


def accept_cookies(driver):
    """Clicking Accept cookies box on YouTube Page"""
    try:
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, '//*[@id="content"]/div[2]/div[6]/div[1]/ytd-button-renderer[2]/a'))).click()
        time.sleep(1.5)
    except TimeoutException:
        eel.update_text("SOMETHING WENT WRONG")
        print("Comment section is probably private.")
        driver.quit()


def generate_link(link):
    """Generating search URL"""
    for i, term in enumerate(config.term_substrings_by_delimiters):
        if i != len(config.term_substrings_by_delimiters) - 1:
            link += term + "+"
        else:
            link += term + "+review"
    return link


def generate_driver():
    """Generating driver instances"""
    chromeOption = Options()
    chromeOption.add_argument("--headless")
    chromeOption.add_argument("--window-size=1600,1200")
    chromeOption.add_argument("--mute-audio")
    chromeOption.add_argument("--log-level=3")
    chromeOption.add_argument("--silent")
    driver = webdriver.Chrome(options=chromeOption)
    return driver


def get_video_links(browser):
    """Get the links to top 5 videos of product that appears on search"""
    links = browser.find_elements(By.ID, value="thumbnail")
    links = [links[x].get_attribute("href") for x in range(35) if
             links[x].get_attribute("href") is not None][:5]
    print("Links:", links)
    return links


def generate_threads():
    """Creating threads that will concurrently scrape n videos for comments"""
    print("Building Driver Thread Instances")
    eel.update_text("BUILDING THREAD INSTANCES")
    threads = []

    for i, v in enumerate(videoLinks):
        print(f'Starting Thread Instance [{str(i + 1)}]')
        eel.update_text(f"STARTING THREAD INSTANCES")
        thread = threading.Thread(target=scrape_comments, args=(v,))
        threads.append(thread)
        thread.start()

    eel.update_text(f"SCRAPING COMMENTS")

    for thread in threads:
        thread.join()


def scroll(scrolls, threadBrowser, link):
    """Scrolls down a given amount of times for a webdriver to load comments
    Scrolls --> Number of scrolls to do (More scrolls = longer runtime)
    threadBrowser --> Webdriver instance associated with a thread
    link --> Link of video being scraped on current thread"""
    for _ in range(int(scrolls)):
        with lock:
            print(f'Scraping comments for "{config.search_term.upper()}" video [{str(videoLinks.index(link) + 1)}]...')

        scroll_height = 2000
        document_height_before = threadBrowser.execute_script("return document.documentElement.scrollHeight")
        threadBrowser.execute_script(f"window.scrollTo(0, {document_height_before + scroll_height});")
        time.sleep(0.8)


def click_more(threadBrowser):
    """For a given Webdriver on a thread looking at a particular video, click the 'view more replies' buttons"""
    viewReplies = threadBrowser.find_elements(By.ID, value="more-replies")
    time.sleep(1)

    for button in viewReplies:
        threadBrowser.execute_script("arguments[0].click();", button)


def get_comments(threadBrowser):
    """For a given Webdriver running on a thread, collate the comments"""
    global total_comments
    comments = threadBrowser.find_elements(By.ID, value="content-text")
    with lock:
        total_comments += len(comments)
        print("Checking comments...")

    for comment in comments:
        with lock:
            sanitised_comment = sentiment_analyser.pre_process(comment.text)
        if youtube_config.comment_mode == "all":
            handle_options(sanitised_comment)
        elif youtube_config.comment_mode == "filtered":
            if config.check_filter(sanitised_comment):
                handle_options(sanitised_comment)


def handle_options(sanitised_comment):
    if youtube_config.sentiment_mode == "vader":
        config.sanitised_youtube[sanitised_comment] = sentiment_analyser.vader_analyze_sentiment(sanitised_comment)
    elif youtube_config.sentiment_mode == "roberta":
        roberta.append(sanitised_comment)


def scrape_comments(link):
    """Procedure each worker thread follows when scraping comments
    New Chrome instance per thread --> Get relevant URL --> Concurrently scrape comments"""
    threadBrowser = generate_driver()
    threadBrowser.get(link)
    accept_cookies(threadBrowser)

    scroll(youtube_config.comment_depth, threadBrowser, link)
    click_more(threadBrowser)

    time.sleep(2)
    get_comments(threadBrowser)
    threadBrowser.quit()


@eel.expose
def run_youtube():
    global videoLinks, roberta

    roberta = []
    print("\nInitialising Key Variables....")

    searchLink = "https://www.youtube.com/results?search_query="

    print("Variables Initialised....")
    eel.update_text("GENERATING DRIVER")
    browser = generate_driver()
    eel.update_text("BUILDING SEARCH URL")
    print("Building Search Link...")
    searchLink = generate_link(searchLink)
    print("Search Link: ", searchLink)
    browser.get(searchLink)
    eel.update_text("ACCEPTING COOKIES")
    print("Accepting Cookies...")
    accept_cookies(browser)
    print("Cookies Accepted...")
    time.sleep(2.5)
    browser.refresh()
    eel.update_text("FETCHING VIDEO LINKS")
    print("Fetching Video Links...")
    videoLinks = get_video_links(browser)
    browser.quit()
    generate_threads()

    if youtube_config.sentiment_mode == "roberta":
        sentiment_analyser.roberta_analyze_sentiment(roberta, config.sanitised_youtube)

    print(f'\nScraped {str(len(config.sanitised_youtube))}/{str(total_comments)} comments')
    print(f'Time Taken In Seconds: {str(round(time.perf_counter() - st, 2))}\n')

    config.generate_report(youtube_config.sentiment_mode, config.sanitised_youtube, "Youtube")


roberta = []
lock = threading.Lock()
total_comments = 0
videoLinks = []
