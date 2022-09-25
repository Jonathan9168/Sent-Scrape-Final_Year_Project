import eel
import time
import praw
import config
import reddit_config
import sentiment_analyser

st = time.perf_counter()


def get_comments(reddit):
    """Get comments from subreddits using PRAW"""
    global total_comments, roberta
    roberta = []

    for i, subreddit in enumerate(reddit_config.sub_reddit[reddit_config.category]):
        start = time.perf_counter()
        eel.update_text(f'CHECKING SUBREDDIT {i + 1} ({len(reddit_config.sub_reddit[reddit_config.category]) - i - 1} LEFT)')
        print(
            f'Checking subreddit: {i + 1}, {len(reddit_config.sub_reddit[reddit_config.category]) - i - 1} more to go...')
        current = reddit.subreddit(subreddit)
        submissions = current.search(config.search_term, sort='top', limit=int(reddit_config.thread_limit),
                                     time_filter="year")
        for sub in submissions:
            sub.comments.replace_more(limit=0, threshold=4)
            for comment in sub.comments.list():
                sanitised_comment = sentiment_analyser.pre_process(comment.body)
                total_comments += 1
                if reddit_config.comment_mode == "all":
                    if len(sanitised_comment) <= 350:
                        handle_options(sanitised_comment)
                elif reddit_config.comment_mode == "filtered":
                    if config.check_filter(sanitised_comment):
                        handle_options(sanitised_comment)
        print(f'Subreddit {i + 1} loop took {round(time.perf_counter() - start, 2)}s')

    if reddit_config.sentiment_mode == "roberta":
        sentiment_analyser.roberta_analyze_sentiment(roberta, config.sanitised_reddit)


def handle_options(sanitised_comment):
    if reddit_config.sentiment_mode == "vader":
        config.sanitised_reddit[sanitised_comment] = sentiment_analyser.vader_analyze_sentiment(sanitised_comment)
    elif reddit_config.sentiment_mode == "roberta":
        roberta.append(sanitised_comment)


@eel.expose
def run_reddit():
    eel.update_text("INITIALISING PRAW")
    reddit = praw.Reddit(client_id="VNk6MDOOEJ1gn5S0qj1jcg", client_secret="_OGmDMGYoEnkBnV8EbjmcO_3QbmvXA",
                         user_agent="redditScrape")
    print("Initialised PRAW")
    print("Scraping Reddit...\n")
    eel.update_text("RETRIEVING COMMENTS")
    get_comments(reddit)
    print(f'\nScraped {str(len(config.sanitised_reddit))}/{str(total_comments)} comments')
    print(f'\nTime Taken In Seconds: {str(round(time.perf_counter() - st, 2))}\n')
    config.generate_report(reddit_config.sentiment_mode, config.sanitised_reddit, "Reddit")


total_comments = 0
roberta = []
