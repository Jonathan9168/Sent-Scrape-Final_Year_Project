import re
import eel
import config

# vader or roberta
sentiment_mode = ""

# defines how many pages of review comments to be parsed.
pagination_depth = 20


@eel.expose
def set_amazon_vars(term, mode, depth):
    global sentiment_mode, pagination_depth
    config.sanitised_amazon = {}
    config.reset_scores()
    config.search_term = term
    sentiment_mode = mode
    pagination_depth = depth
    config.term_substrings_by_delimiters = re.split(r'\s|-', config.search_term)
    config.term_substrings_spaced = config.search_term.split(" ")
