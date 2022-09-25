import re
import eel
import json
import pandas as pd
import sentiment_analyser

search_term = ""
term_substrings_by_delimiters = re.split(r'\s|-', search_term)
term_substrings_spaced = search_term.split(" ")

# Final dictionaries that hold (comment : score) mapping for respective social media platforms
sanitised_youtube, sanitised_reddit, sanitised_twitter, sanitised_amazon = {}, {}, {}, {}

current_dataframe = pd.DataFrame.from_dict({})

# score variables for vader
vad_neg, vad_neu, vad_pos, vad_comp = 0, 0, 0, 0

# score variables for roberta
rob_neg, rob_neu, rob_pos = 0, 0, 0

final_score = 0


def set_vader_scores():
    global vad_neg, vad_neu, vad_pos, vad_comp, final_score
    vad_neg = round(current_dataframe['neg'].mean(), 3)
    vad_neu = round(current_dataframe['neu'].mean(), 3)
    vad_pos = round(current_dataframe['pos'].mean(), 3)
    vad_comp = round(current_dataframe['compound'].mean(), 3)
    final_score = vad_comp


def set_roberta_scores():
    global rob_neg, rob_neu, rob_pos, final_score
    rob_neg = round(current_dataframe['neg'].mean(), 3)
    rob_neu = round(current_dataframe['neu'].mean(), 3)
    rob_pos = round(current_dataframe['pos'].mean(), 3)
    final_score = round(sum([rob_neg * -1, rob_pos]), 3)


@eel.expose
def get_vader_scores():
    return vad_neg, vad_neu, vad_pos, vad_comp


@eel.expose
def get_roberta_scores():
    return rob_neg, rob_neu, rob_pos


@eel.expose
def get_final_score():
    return final_score


@eel.expose
def get_search_term():
    return search_term


@eel.expose
def get_columns():
    return current_dataframe.shape[1]


def reset_scores():
    global vad_neg, vad_neu, vad_pos, vad_comp, rob_neg, rob_neu, rob_pos, final_score
    vad_neg, vad_neu, vad_pos, vad_comp = 0, 0, 0, 0
    rob_neg, rob_neu, rob_pos, final_score = 0, 0, 0, 0


def generate_report(sentiment_mode, sent_dict, platform):
    if sentiment_mode == "vader":
        sentiment_analyser.generate_sentiment_report_vader(sent_dict, platform)
        set_vader_scores()
    elif sentiment_mode == "roberta":
        sentiment_analyser.generate_sentiment_report_roberta(sent_dict, platform)
        set_roberta_scores()


def check_filter(comment):
    """Conditions that a comment must meet to pass filtration"""
    a = re.search(search_term, comment, re.IGNORECASE)
    b = any(substring.lower() in comment for substring in term_substrings_by_delimiters)
    c = any(substring.lower() in comment for substring in term_substrings_spaced)
    d = len(comment) <= 350
    return (a or b or c) and d


@eel.expose
def get_dict():
    return json.dumps(json.loads(current_dataframe.to_json(orient="index")))


@eel.expose
def save_to_csv():
    current_dataframe.to_csv(f"CSVs/{search_term}.csv", encoding='utf-8')
