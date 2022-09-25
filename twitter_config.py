import re
import eel
import config

# vader or roberta
sentiment_mode = ""

# determines how deep into comment pool to scrape. Higher = Longer especially if there are not enough comment to fulfill
comment_depth = 0


@eel.expose
def set_twitter_vars(term, mode, depth):
    global sentiment_mode, comment_depth
    config.sanitised_twitter = {}
    config.reset_scores()
    config.search_term = term
    sentiment_mode = mode
    comment_depth = depth
    config.term_substrings_by_delimiters = re.split(r'\s|-', config.search_term)
    config.term_substrings_spaced = config.search_term.split(" ")
