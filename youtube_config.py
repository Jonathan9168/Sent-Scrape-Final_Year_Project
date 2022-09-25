import re
import eel
import config

# vader or roberta
sentiment_mode = ""

# determines how deep into comment pool to scrape. Higher = Longer especially if there are not enough comment to fulfill
comment_depth = 0

# all or filtered
comment_mode = ""


@eel.expose
def set_youtube_vars(search_term, com_mode, model, depth):
    global comment_mode, sentiment_mode, comment_depth
    config.sanitised_youtube = {}
    config.reset_scores()
    config.search_term = search_term
    comment_mode = com_mode
    sentiment_mode = model
    comment_depth = depth
    config.term_substrings_by_delimiters = re.split(r'\s|-', config.search_term)
    config.term_substrings_spaced = config.search_term.split(" ")
