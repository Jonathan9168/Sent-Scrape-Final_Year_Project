import os
import re
import eel
import json
import pandas as pd
import sentiment_analyser
from datetime import datetime

search_term_view, search_term = "", ""
term_substrings_by_delimiters = re.split(r'\s|-', search_term)
term_substrings_spaced = search_term.split(" ")

# Final dictionaries that hold (comment : score) mapping for respective social media platforms
sanitised_youtube, sanitised_reddit, sanitised_twitter, sanitised_amazon = {}, {}, {}, {}

current_dataframe = pd.DataFrame.from_dict({})
view_dataframe = pd.DataFrame.from_dict({})

sent_mode = ""
platform_name = ""

# score variables for vader
vad_neg, vad_neu, vad_pos, vad_comp = 0, 0, 0, 0,
# score variables for roberta
rob_neg, rob_neu, rob_pos = 0, 0, 0

final_score = 0

data_title, view_title = "", ""
rob_files, vad_files = [], []

rob_compare, rob_compare_vc = [], []


@eel.expose
def get_search_term():
    return search_term


@eel.expose
def get_search_term_view():
    return search_term_view


@eel.expose
def get_title():
    return data_title


@eel.expose
def get_title_view():
    return view_title


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
def get_roberta_scores_view():
    return round(view_dataframe['neg'].mean(), 3), round(view_dataframe['neu'].mean(), 3), round(
        view_dataframe['pos'].mean(), 3), round(
        sum([round(view_dataframe['neg'].mean(), 3) * -1, round(view_dataframe['pos'].mean(), 3)]), 3)


@eel.expose
def get_vader_scores_view():
    return round(view_dataframe['neg'].mean(), 3), round(view_dataframe['neu'].mean(), 3), round(
        view_dataframe['pos'].mean(), 3), round(
        view_dataframe['compound'].mean(), 3)


@eel.expose
def get_roberta_scores():
    return rob_neg, rob_neu, rob_pos


@eel.expose
def get_vader_scores():
    return vad_neg, vad_neu, vad_pos, vad_comp


@eel.expose
def get_final_score():
    return final_score


def reset_scores():
    global vad_neg, vad_neu, vad_pos, vad_comp, rob_neg, rob_neu, rob_pos, final_score
    vad_neg, vad_neu, vad_pos, vad_comp = 0, 0, 0, 0
    rob_neg, rob_neu, rob_pos, final_score = 0, 0, 0, 0


@eel.expose
def get_vader_dicts():
    return json.dumps(current_dataframe["neg"].value_counts().sort_index().to_dict()), \
           json.dumps(current_dataframe["neu"].value_counts().sort_index().to_dict()), \
           json.dumps(current_dataframe["pos"].value_counts().sort_index().to_dict()), \
           json.dumps(current_dataframe["compound"].value_counts().sort_index().to_dict())


@eel.expose
def get_roberta_dicts():
    return json.dumps(current_dataframe["neg"].value_counts().sort_index().to_dict()), \
           json.dumps(current_dataframe["neu"].value_counts().sort_index().to_dict()), \
           json.dumps(current_dataframe["pos"].value_counts().sort_index().to_dict())


@eel.expose
def get_columns():
    return current_dataframe.shape[1]


@eel.expose
def get_columns_view():
    return view_dataframe.shape[1]


def generate_report(sentiment_mode, sent_dict, platform):
    global platform_name
    if sentiment_mode == "vader":
        sentiment_analyser.generate_sentiment_report_vader(sent_dict, platform)
        set_vader_scores()
    elif sentiment_mode == "roberta":
        sentiment_analyser.generate_sentiment_report_roberta(sent_dict, platform)
        set_roberta_scores()
    platform_name = platform
    save_to_csv()


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
def get_dict_view():
    return json.dumps(json.loads(view_dataframe.to_json(orient="index")))


@eel.expose
def get_files():
    return os.listdir("CSVs/Rob Searches/"), os.listdir("CSVs/Vad Searches/")


@eel.expose
def apply_view_data_rob(search, platform, date, time):
    global view_dataframe, view_title, search_term_view
    search_term_view = search
    view_dataframe = pd.read_csv(
        f"CSVs/Rob Searches/{search},{platform},{date.replace('/', '.')},{time.replace(':', '.')}.csv", index_col=0)
    view_title = f'"{search.title()}" on {platform} analyzed using roBERTa'

names = ""
@eel.expose
def comparison_2D(selected_searches):
    global rob_compare, rob_compare_vc,names
    print(selected_searches)
    rob_compare, rob_compare_vc = [], []

    for i, v in enumerate(selected_searches):
        rob_compare.append(pd.read_csv(
            f"CSVs/Rob Searches/{v[0]},{v[1]},{v[2].replace('/', '.')},{v[3].replace(':', '.')}.csv",
            index_col=0))
    names = selected_searches

    for df in rob_compare:
        neg_dict = json.dumps(df["neg"].value_counts().sort_index().to_dict())
        neu_dict = json.dumps(df["neu"].value_counts().sort_index().to_dict())
        pos_dict = json.dumps(df["pos"].value_counts().sort_index().to_dict())
        rob_compare_vc.append((neu_dict, neg_dict, pos_dict))


@eel.expose
def get_comp():
    return names


@eel.expose
def get_comp_vc():
    return rob_compare_vc


@eel.expose
def apply_view_data_vad(search, platform, date, time):
    global view_dataframe, view_title, search_term_view
    search_term_view = search
    view_dataframe = pd.read_csv(
        f"CSVs/Vad Searches/{search},{platform},{date.replace('/', '.')},{time.replace(':', '.')}.csv", index_col=0)
    view_title = f"'{search.title()}' on {platform} analyzed using NLTK's Vader"


@eel.expose
def get_vader_dicts_view():
    return json.dumps(view_dataframe["neg"].value_counts().sort_index().to_dict()), \
           json.dumps(view_dataframe["neu"].value_counts().sort_index().to_dict()), \
           json.dumps(view_dataframe["pos"].value_counts().sort_index().to_dict()), \
           json.dumps(view_dataframe["compound"].value_counts().sort_index().to_dict())


@eel.expose
def get_roberta_dicts_view():
    return json.dumps(view_dataframe["neg"].value_counts().sort_index().to_dict()), \
           json.dumps(view_dataframe["neu"].value_counts().sort_index().to_dict()), \
           json.dumps(view_dataframe["pos"].value_counts().sort_index().to_dict())


@eel.expose
def get_view_title():
    return view_title


@eel.expose
def delete_row(search, platform, date, time, mode):
    os.remove(
        f"CSVs/{'Rob Searches' if mode == 'rob' else 'Vad Searches'}/{search},{platform},{date.replace('/', '.')},{time.replace(':', '.')}.csv")


def save_to_csv():
    date_time = datetime.now().strftime("%d/%m/%Y,%H:%M:%S").split(',')
    destination_folder = "Rob Searches" if sent_mode == "rob" else "Vad Searches"
    current_dataframe.to_csv(
        f"CSVs/{destination_folder}/{search_term},{platform_name},{date_time[0].replace('/', '.')},{date_time[1].replace(':', '.')}.csv",
        encoding='utf-8')
