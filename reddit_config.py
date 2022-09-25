import re
import eel
import config

# Reddit categories to get info from relevant subreddits
# categories: cpu,gpu,ram,ssd,monitor,psu
category = "gpu"

sub_reddit = {
    'cpu': ["buildapc", "hardware", "nvidia", "amd", "intel"],
    'gpu': ["buildapc", "hardware", "nvidia", "amd", "intel"],
    'ram': ["buildapc", "pcgaming", "hardware"],
    'storage': ["buildapc", "hardware", "DataHoarder"],
    'psu': ["buildapc", "hardware"],
    'monitor': ["buildapc", "hardware", "buildapcmonitors", "Monitors"]
}

# vader or roberta
sentiment_mode = ""

# all or filtered
comment_mode = ""

# 1-5
thread_limit = 0


@eel.expose
def set_reddit_vars(search_term, com_mode, model, segment, limit):
    global comment_mode, sentiment_mode, category, thread_limit
    config.sanitised_reddit = {}
    config.reset_scores()
    config.search_term = search_term
    comment_mode = com_mode
    sentiment_mode = model
    category = segment
    thread_limit = limit
    config.term_substrings_by_delimiters = re.split(r'\s|-', config.search_term)
    config.term_substrings_spaced = config.search_term.split(" ")
