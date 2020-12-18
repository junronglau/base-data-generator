import ast
import html
from unicodedata import normalize

import icu
import nltk
import numpy as np
from polyglot.detect import Detector

resources = ["wordnet", "stopwords", "punkt", \
             "averaged_perceptron_tagger", "maxent_treebank_pos_tagger", "wordnet"]

for resource in resources:
    try:
        nltk.data.find("tokenizers/" + resource)
    except LookupError:
        nltk.download(resource)


def reformat_reviews_df(df):
    # Drop rows which are actually headers
    df = df[df.ASIN != 'ASIN']

    # Reformat profile link for profile crawling
    df['new_profile_link'] = "https://www.amazon.com" + df['profile_link'].astype(str)

    # Check if stars column is correctly named:
    if 'ï»¿stars' in df.columns.values.tolist() and 'stars' not in df.columns.values.tolist():
        df = df.rename(columns={'ï»¿stars': 'stars'})

    # Lowercase title text
    df['clean_title'] = df['title'].str.lower()

    # Decode & lowercase comment text
    df['decoded_comment'] = df.comment.astype(str)
    df['decoded_comment'] = df.decoded_comment.apply(lambda x: html.unescape(x))
    df['decoded_comment'] = df.decoded_comment.apply(lambda text: ''.join(x for x in text if x.isprintable()))
    df["decoded_comment"] = df["decoded_comment"].apply(lambda text: normalize("NFKD", text)
                                                        .encode("ascii", "ignore")
                                                        .decode("utf-8", "ignore"))
    df['decoded_comment'] = df['decoded_comment'].str.replace('\n', ' ').str.replace('\t', ' ')
    df['decoded_comment'] = df['decoded_comment'].str.lower().str.strip()

    # Cleaning stars
    df['ratings'] = df.stars.astype(str)
    df['ratings'] = df.ratings.apply(lambda x: x.split())
    df['ratings'] = df.ratings.apply(lambda x: float(x[0]) / float(x[3]))

    # Data wrangling & Fill in blanks for Verified Puchase
    df['clean_verified'] = df.verified.astype(str)
    df.loc[df.clean_verified == 'Verified Purchase', 'clean_verified'] = 1
    df['clean_verified'] = df['clean_verified'].fillna(value=0)

    # Extract Account Number
    df['account_number'] = df['profile_link'].astype(str)
    df['account_number'] = df['account_number'].str.split('.').str[-1]

    # Data wrangling for voting columns
    df['clean_voting'] = df['voting']
    df['clean_voting'] = df['clean_voting'].fillna(value=0)
    df['clean_voting'] = df.clean_voting.astype(str)
    df['clean_voting'] = df.clean_voting.apply(lambda x: x.split(' ')[0])
    df.loc[df.clean_voting == 'One', 'clean_voting'] = 1
    df.loc[df.clean_voting == 'Helpful', 'clean_voting'] = 0
    df['clean_voting'] = df.clean_voting.astype(str)
    df['clean_voting'] = df.clean_voting.apply(lambda x: x.replace(',', '') if ',' in x else x)
    df['clean_voting'] = df.clean_voting.astype(int)

    # Extracting location & date posted into two different columns
    df['location'], df['date_posted'] = zip(*df.date.str.split('on'))
    df['location'] = df['location'].str.replace("Reviewed in the ", "")

    # Identifying opinion's language
    df['poly_obj'] = df.decoded_comment.apply(lambda x: Detector(x, quiet=True))
    df['language'] = df['poly_obj'].apply(lambda x: icu.Locale.getDisplayName(x.language.locale))
    df['language_confidence'] = df['poly_obj'].apply(lambda x: x.language.confidence)

    # Keep english
    df = df[df['language'] == 'English']

    # return dataframe
    return df


def reformat_profiles_df(df):
    df = df.drop_duplicates()

    # Mark deleted accounts
    df['deleted_status'] = df['json_data'].isnull()

    # Fill empty json strings with formatted json
    empty_json_format = {
        'contributions': '',
        'marketplaceId': '',
        'locale': ''
    }
    df['json_data'] = df['json_data'].fillna(value=str(empty_json_format))

    # Ignore depreciation error
    np.warnings.filterwarnings('ignore', category=np.VisibleDeprecationWarning)
    df['reviewer_contributions'], df['marketplace_id'], df['locale'] = zip(*df['json_data'].apply(split_reviewer_data))

    # convert ranking string to integer
    df['ranking'] = df['ranking'].str.replace(',', '')
    df['ranking'] = df['ranking'].fillna(value=0)
    df['ranking'] = df['ranking'].astype(int)

    # return dataframe
    return df


def split_reviewer_data(json_data):
    decoded_data = ast.literal_eval(json_data)
    return decoded_data['contributions'], decoded_data['marketplaceId'], decoded_data['locale']
