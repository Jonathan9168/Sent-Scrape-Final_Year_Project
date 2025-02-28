import os
import re
import eel
import json
import pandas as pd
import sentiment_analyser
from datetime import datetime
import chromedriver_autoinstaller

chromedriver_autoinstaller.install()

search_term_view, search_term = "", ""
term_substrings_by_delimiters = re.split(r'\s|-', search_term)
term_substrings_spaced = search_term.split(" ")

# Final dictionaries that hold (comment : scores) mapping for respective social media platforms
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

comparison_data_frames, comparison_value_counts = [], []
dataset_names = []


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
    """Calls sentiment report generator depending on methodology selected by user"""
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
    b = all(substring.lower() in comment for substring in term_substrings_by_delimiters)
    c = all(substring.lower() in comment for substring in term_substrings_spaced)
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
    """Returns file names of searches in each local search storage directory sorted by newest which allows the front end
     history page to construct table with correct data"""
    rob_filenames = os.listdir("CSVs/rob_searches/")
    vad_filenames = os.listdir("CSVs/vad_searches/")
    rob_filenames.sort(key=lambda x: os.path.getmtime(os.path.join("CSVs/rob_searches/", x)), reverse=True)
    vad_filenames.sort(key=lambda x: os.path.getmtime(os.path.join("CSVs/vad_searches/", x)), reverse=True)
    return rob_filenames, vad_filenames


@eel.expose
def apply_view_data_rob(search, platform, date, time):
    global view_dataframe, view_title, search_term_view
    search_term_view = search
    view_dataframe = pd.read_csv(
        f"CSVs/rob_searches/{search},{platform},{date.replace('/', '.')},{time.replace(':', '.')}.csv", index_col=0)
    view_title = f'"{search.upper()}" {platform} data analyzed using RoBERTa'


@eel.expose
def apply_view_data_vad(search, platform, date, time):
    global view_dataframe, view_title, search_term_view
    search_term_view = search
    view_dataframe = pd.read_csv(
        f"CSVs/vad_searches/{search},{platform},{date.replace('/', '.')},{time.replace(':', '.')}.csv", index_col=0)
    view_title = f'"{search.upper()}" {platform} data analyzed using VADER'


@eel.expose
def apply_comparisons_rob(selected_searches_2D):
    """Recieves data set names list from front end, reads data frames of these files into memory, extends name of files
    with their overall scoring and store their full datasets in memory"""
    global comparison_data_frames, comparison_value_counts, dataset_names
    comparison_data_frames, comparison_value_counts, dataset_names = [], [], []
    # selected_searches_2D = [[<search_term>,<platform>,<date>,<time>]]
    # comparison_data_frames = [data_frame_0,...,data_frame_n]
    for i, v in enumerate(selected_searches_2D):
        comparison_data_frames.append(pd.read_csv(
            f"CSVs/rob_searches/{v[0]},{v[1]},{v[2].replace('/', '.')},{v[3].replace(':', '.')}.csv",
            index_col=0))

    # selected_searches_2D = [[<search_term>,<platform>,<date>,<time>,<neg_mean>,<neu_mean>,<pos_mean>]...,]
    # comparison_value_counts = [(neg_dict, neu_dict, pos_dict)...,]
    for i, df in enumerate(comparison_data_frames):
        neg_dict = json.dumps(df["neg"].value_counts().sort_index().to_dict())
        neu_dict = json.dumps(df["neu"].value_counts().sort_index().to_dict())
        pos_dict = json.dumps(df["pos"].value_counts().sort_index().to_dict())

        selected_searches_2D[i].extend(
            [round(df['neg'].mean(), 3), round(df['neu'].mean(), 3), round(df['pos'].mean(), 3)])
        comparison_value_counts.append((neg_dict, neu_dict, pos_dict))

    print(selected_searches_2D)
    dataset_names = selected_searches_2D


@eel.expose
def apply_comparisons_vad(selected_searches_2D):
    """Recieves data set names list from front end, reads data frames of these files into memory, extends name of files
    with their overall scoring and store their full datasets in memory"""
    global comparison_data_frames, comparison_value_counts, dataset_names
    comparison_data_frames, comparison_value_counts, dataset_names = [], [], []
    # selected_searches_2D = [[<search_term>,<platform>,<date>,<time>]]
    # comparison_data_frames = [data_frame_0,...,data_frame_n]
    for i, v in enumerate(selected_searches_2D):
        comparison_data_frames.append(pd.read_csv(
            f"CSVs/vad_searches/{v[0]},{v[1]},{v[2].replace('/', '.')},{v[3].replace(':', '.')}.csv",
            index_col=0))

    # selected_searches_2D = [[<search_term>,<platform>,<date>,<time>,<neg_mean>,<neu_mean>,<pos_mean>,<compound_mean>]...,]
    # comparison_value_counts = [(neg_dict, neu_dict, pos_dict, compound_dict)...,]
    for i, df in enumerate(comparison_data_frames):
        neg_dict = json.dumps(df["neg"].value_counts().sort_index().to_dict())
        neu_dict = json.dumps(df["neu"].value_counts().sort_index().to_dict())
        pos_dict = json.dumps(df["pos"].value_counts().sort_index().to_dict())
        compound_dict = json.dumps(df["compound"].value_counts().sort_index().to_dict())
        comparison_value_counts.append((neg_dict, neu_dict, pos_dict, compound_dict))

        selected_searches_2D[i].extend(
            [round(df['neg'].mean(), 3), round(df['neu'].mean(), 3), round(df['pos'].mean(), 3),
             round(df['compound'].mean(), 3)])

    print(selected_searches_2D)
    dataset_names = selected_searches_2D


@eel.expose
def get_dataset_names():
    return dataset_names


@eel.expose
def get_comparision_value_counts():
    return comparison_value_counts


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
           json.dumps(view_dataframe["pos"].
                      value_counts().sort_index().to_dict())


@eel.expose
def delete_row(search, platform, date, time, mode):
    os.remove(
        f"CSVs/{'rob_searches' if mode == 'rob' else 'vad_searches'}/{search},{platform},{date.replace('/', '.')},{time.replace(':', '.')}.csv")


def save_to_csv():
    date_time = datetime.now().strftime("%d/%m/%Y,%H:%M:%S").split(',')
    destination_folder = "rob_searches" if sent_mode == "rob" else "vad_searches"
    try:
        current_dataframe.to_csv(
            f"CSVs/{destination_folder}/{search_term},{platform_name},{date_time[0].replace('/', '.')},{date_time[1].replace(':', '.')}.csv",
            encoding='utf-8')
    except OSError:
        eel.update_text("INVALID CHARACTER IN FILENAME")


@eel.expose
def generate_verdict_rob(final: float, term: str):
    """Returns a verdict for searches analysed using RoBERTa model"""
    if -0.1 <= final <= 0.1:
        return f"Inconclusive - [{final}]", f"A final score of {final}, indicates that the data doesn't seem to strongly favour one direction. You might want to consider checking how the scoring of <span style='color: lightblue'>'{term.upper()}'</span> fares on other platforms."
    elif -0.4 <= final <= -0.1:
        return f'<span style="color: #f98686">Relatively Unpopular</span> - [{final}]', f"A score of <span style='color: #f98686'>{final}</span> reflects a noticeable amount of negativity around <span style='color: #f98686'>'{term.upper()}'</span>, see if this trend follows on other platforms and take a look at the dataset snapshot to see what's being discussed."
    elif -1 <= final <= -0.4:
        return f'<span style="color: #f98686">Highly Unpopular</span> - [{final}]', f"A score of <span style='color: #f98686'>{final}</span> indicates a significant amount of negativity surrounding <span style='color: #f98686'>'{term.upper()}'</span>. Is there a specific event that might have caused this?"
    elif 0.1 <= final <= 0.4:
        return f'<span style="color: lightgreen">Relatively Popular</span> - [{final}]', f"A score of <span style='color: lightgreen'>{final}</span> suggests notable positivity. You may want to explore if this trend persists on other platforms. Click the button below to view talking points about <span style='color: lightgreen'>'{term.upper()}'</span>."
    elif 0.4 <= final <= 1:
        return f'<span style="color: lightgreen">Highly Popular</span> - [{final}]', f" A score of <span style='color: lightgreen'>{final}</span> reflects an overwhelming amount of positivity around <span style='color: lightgreen'>'{term.upper()}'</span>. Can you identify any specific factors or events that might have contributed to this positive sentiment?"


@eel.expose
def generate_verdict_vad(final: float, term: str):
    """Returns a verdict for searches analysed using VADER model"""
    if -0.1 <= final <= 0.1:
        return f"Inconclusive - [{final}]", f"A final compound score of {final}, indicates that the data doesn't seem to strongly favour one direction. You might want to consider checking how the scoring of <span style='color: lightblue'>'{term.upper()}'</span> fares on other platforms."
    elif -0.4 <= final <= -0.1:
        return f'<span style="color: #f98686">Relatively Unpopular</span> - [{final}]', f"A compound score of <span style='color: #f98686'>{final}</span> reflects a noticeable amount of negativity around <span style='color: #f98686'>'{term.upper()}'</span>, see if this trend follows on other platforms and take a look at the dataset snapshot to see what's being discussed."
    elif -1 <= final <= -0.4:
        return f'<span style="color: #f98686">Highly Unpopular</span> - [{final}]', f"A compound score of <span style='color: #f98686'>{final}</span> indicates a significant amount of negativity surrounding <span style='color: #f98686'>'{term.upper()}'</span>. Is there a specific event that might have caused this?"
    elif 0.1 <= final <= 0.4:
        return f'<span style="color: lightgreen">Relatively Popular</span> - [{final}]', f"A compound score of <span style='color: lightgreen'>{final}</span> suggests notable positivity. You may want to explore if this trend persists on other platforms. Click the button below to view talking points about <span style='color: lightgreen'>'{term.upper()}'</span>."
    elif 0.4 <= final <= 1:
        return f'<span style="color: lightgreen">Highly Popular</span> - [{final}]', f"A compound score of <span style='color: lightgreen'>{final}</span> reflects an overwhelming amount of positivity around <span style='color: lightgreen'>'{term.upper()}'</span>. Can you identify any specific factors or events that might have contributed to this positive sentiment?"
