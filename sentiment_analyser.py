import re
import eel
import torch
import config
import string
import cpuinfo
import pandas as pd
from operator import getitem
from string import punctuation
from scipy.special import softmax
from collections import OrderedDict
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from transformers import AutoTokenizer, AutoModelForSequenceClassification

"""Regular expression patterns to be applied to text for sanitising"""
emotes_punctuation = re.compile("["
                                u"\U0001F600-\U0001F64F"  # emotes
                                u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                                u"\U0001F680-\U0001F6FF"  # transport & map symbols
                                u"\U0001F1E0-\U0001F1FF"
                                u"\U00002702-\U000027B0"
                                u"\U000024C2-\U0001F251"
                                u"\U0001f926-\U0001f937"
                                u"\U0001F1F2"
                                u"\U0001F1F4"
                                u"\U0001F620"
                                U"\u201D"
                                U"\u2019"
                                U"\u2018"
                                U"\u2014"
                                U"\u2013"
                                U"\u2080-\u2089"
                                u"\u200d"
                                u"\u2640-\u2642"
                                u"\u2600-\u2B55"
                                u"\u23cf"
                                u"\u2026"
                                u"\u23e9"
                                u"\u231a"
                                u"\ufe0f"
                                u"\u3030"
                                u"\U00002500-\U00002BEF"
                                u"\U00010000-\U0010ffff"
                                U"\u201C"
                                U"\u00B7"
                                "]+", flags=re.UNICODE)


def pre_process(comment: str) -> str:
    """Text pre-processing for other platforms"""
    comment = comment.lower()
    comment = re.sub('https?://\S+|www\.\S+', ' ', comment)  # Remove links
    comment = re.sub('@[a-zA-Z0-9]+', ' ', comment)  # Remove @username
    comment = re.sub('#[a-zA-Z0-9]+', ' ', comment)  # Remove hashtag
    comment = comment.translate(str.maketrans('', '', string.punctuation))  # Remove Punctuation
    comment = re.sub('\n +', ' ', comment)  # Remove new lines
    comment = comment.replace("\n", " ")
    comment = re.sub("\s +", "", comment)
    comment = emotes_punctuation.sub('', comment)
    comment = re.sub(' \s+', ' ', comment)
    comment.strip()
    # stop_words = set(stopwords.words('english'))
    # tokenized = word_tokenize(comment)
    # comment = ' '.join(w for w in tokenized if w not in stop_words)
    return comment


def pre_process_twitter(comment: str) -> str:
    """Text pre-processing for Twitter"""
    comment = comment.lower()
    comment = re.sub('https?://\S+|www\.\S+', ' ', comment)  # Remove links
    comment = re.sub(r'@[a-zA-Z0-9]+', ' ', comment)  # Remove @username
    comment = comment.translate(str.maketrans('', '', punctuation.replace("#", "")))  # Remove Punctuation
    comment = re.sub('\n', ' ', comment)  # Remove new lines
    comment = re.sub('\n ', ' ', comment)
    comment = emotes_punctuation.sub('', comment)
    comment = re.sub(' +', ' ', comment)
    comment.strip()
    return comment


def vader_analyze_sentiment(comment):
    """Calculates sentiment of comment passed through and returns a dict {neg:val, neu:val, pos:val, compound:val} : compound(-1 <= val <= 1)
    neg,neu,pos(0 <= val <= 1)
    Using VADER 'bag of words' lexicon-based approach
    tokenizes and assigns ratings to each word individually, aggregates neg,neu,pos to give a compound score"""
    return SentimentIntensityAnalyzer().polarity_scores(comment)


def chunkify(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def roberta_analyze_sentiment(comments: list, sent_dict: dict):
    """Adapted: https://huggingface.co/cardiffnlp/twitter-roberta-base-sentiment-latest
    using RoBERTa pretrained model to make predictions can be more accurate than vader but can be time-consuming if gpu hardware
    leverage isn't present must use CPU instead"""
    config.sent_mode = "rob"
    device = "cuda:0" if torch.cuda.is_available() else "cpu"
    # MODEL = f"cardiffnlp/twitter-roberta-base-sentiment"
    MODEL = f"cardiffnlp/twitter-roberta-base-sentiment-latest"
    tokenizer = AutoTokenizer.from_pretrained(MODEL)
    model = AutoModelForSequenceClassification.from_pretrained(MODEL)
    model = model.to(device)

    chunk_size = 50
    comment_chunks = list(chunkify(comments, chunk_size))  # [[c00,c01,...,c0n],[c10,c11,...,c1n],[c21,c21,...,c2n]]
    device_model = torch.cuda.get_device_name(0) if torch.cuda.is_available() else cpuinfo.get_cpu_info()["brand_raw"]

    eel.update_text(f"ANALYSING SENTIMENT USING {device_model}")
    print(f'\nDevice: {device_model}')
    print(f'No. Chunks [chunk_size = {chunk_size}]: {len(comment_chunks)}')

    with torch.inference_mode():
        for chunk in comment_chunks:
            # Encoding comments batch
            encoded_comments = tokenizer(chunk, padding=True, truncation=True, max_length=350, return_tensors='pt').to(
                device)
            # Passing encoded comments to model to receive tensor scores
            output = model(**encoded_comments)
            # Detach tensor logits to store values locally using numpy 2D Array
            scores = output.logits.cpu().detach().numpy()

            for i, v in enumerate(chunk):
                # confining scores for a given comment between 0-1 using softmax
                score = softmax(scores[i])
                # storing comment and respective sentiment values into dict
                sent_dict[v] = {
                    'neg': float(round(score[0], 3)),
                    'neu': float(round(score[1], 3)),
                    'pos': float(round(score[2], 3))
                }
            torch.cuda.empty_cache()


def generate_sentiment_report_vader(sent_dict, platform_name):
    """Generate Pandas DataFrame where df headers = comment, neg, neu, pos, compounds"""
    config.sent_mode = "vad"
    eel.update_text("GENERATING REPORT")
    """Generate Pandas DataFrame where df headers = comment, neg, neu, pos, compound"""
    sent_dict = OrderedDict(sorted(sent_dict.items(), key=lambda x: getitem(x[1], 'compound'), reverse=True))
    df = pd.DataFrame.from_dict(sent_dict, orient='index', columns=['neg', 'neu', 'pos', 'compound'])
    df.columns.name = 'comment'
    config.current_dataframe = df

    draw_df(df)
    config.data_title = f"'{config.search_term.upper()}' on {platform_name} analyzed using NLTK's Vader"


def generate_sentiment_report_roberta(sent_dict, platform_name):
    """Generate Pandas DataFrame where df headers = comment, neg, neu, pos"""
    eel.update_text("GENERATING REPORT")
    sent_dict = OrderedDict(sorted(sent_dict.items(), key=lambda x: getitem(x[1], 'pos'), reverse=True))
    df = pd.DataFrame.from_dict(sent_dict, orient='index', columns=['neg', 'neu', 'pos'])
    df.columns.name = 'comment'
    config.current_dataframe = df

    draw_df(df)
    config.data_title = f'"{config.search_term.upper()}" on {platform_name} analyzed using roBERTa'


def draw_df(df):
    """Draws current pandas dataframe"""
    with pd.option_context('display.max_rows', None, 'display.max_columns', None, 'display.max_colwidth', 153,
                           'expand_frame_repr', False, 'colheader_justify', 'center'):
        print("\n")
        print(df)
        print(df.shape)
