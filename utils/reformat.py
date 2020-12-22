import ast
import html
from unicodedata import normalize

import icu
import nltk
import numpy as np
from polyglot.detect import Detector

import re

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
    df['cleaned_profile_link'] = "https://www.amazon.com" + df['profile_link'].astype(str)

    # Check if stars column is correctly named:
    if 'ï»¿stars' in df.columns.values.tolist() and 'stars' not in df.columns.values.tolist():
        df = df.rename(columns={'ï»¿stars': 'stars'})

    # Lowercase title text
    df['cleaned_title'] = df['title'].str.lower()

    # Decode & lowercase comment text
    df['decoded_comment'] = df.comment.astype(str).apply(decode_comments)
    df['decoded_comment'] = df['decoded_comment'].str.replace('\n', ' ').str.replace('\t', ' ').str.lower().str.strip()

    # Cleaning stars
    df['cleaned_ratings'] = df.stars.astype(str).apply(normalize_ratings)

    # Data wrangling & Fill in blanks for Verified Puchase
    df['cleaned_verified'] = df.verified.astype(str)
    df.loc[df.cleaned_verified == 'Verified Purchase', 'cleaned_verified'] = 1
    df['cleaned_verified'] = df['cleaned_verified'].fillna(value=0)

    # Extract Account Number
    df['acc_num'] = df['profile_link'].astype(str).str.split('.').str[-1]

    # Data wrangling for voting columns
    df['cleaned_voting'] = df['voting'].fillna(value=0)
    df['cleaned_voting'] = df.cleaned_voting.astype(str).apply(lambda x: x.split(' ')[0])
    df.loc[df.cleaned_voting == 'One', 'cleaned_voting'] = 1
    df.loc[df.cleaned_voting == 'Helpful', 'cleaned_voting'] = 0
    df['cleaned_voting'] = df.cleaned_voting.astype(str).apply(lambda x: x.replace(',', '') if ',' in x else x)
    df['cleaned_voting'] = df.cleaned_voting.astype(int)

    # Extracting location & date posted into two different columns
    df['cleaned_location'], df['cleaned_date_posted'] = zip(*df.date.str.split('on'))
    df['cleaned_location'] = df['cleaned_location'].str.replace("Reviewed in the ", "").str.replace("Reviewed in ", "")

    # Identifying opinion's language
    df['poly_obj'] = df.decoded_comment.apply(lambda x: Detector(x, quiet=True))
    df['language'] = df['poly_obj'].apply(lambda x: icu.Locale.getDisplayName(x.language.locale))
    df['language_confidence'] = df['poly_obj'].apply(lambda x: x.language.confidence)

    # Keep english
    df = df[df['language'] == 'English']

    # return dataframe
    return df

def reformat_products_df(df):
    # Decode & lowercase comment text
    df['decoded_comment'] = df.description.fillna(value='')
    df["decoded_comment"] = df["decoded_comment"].apply(decode_comments)
    df['decoded_comment']= df['decoded_comment'].str.lower()

    # Cleaning stars
    df['cleaned_rating'] = df.rating.fillna(value='0 out of 5')
    df['cleaned_rating'] = df.cleaned_rating.apply(normalize_ratings)
    df.loc[df.cleaned_rating == 0, 'cleaned_rating'] = np.nan

    # extract price
    df['cleaned_price'] = df.price.fillna(value='$0.00')
    df['cleaned_price'] = df.cleaned_price.apply(lambda x: re.findall( r'\$([0-9]+\.?[0-9]+)', x))
    df['cleaned_price'] = df.cleaned_price.apply(lambda x: x[0])
    df.loc[df.cleaned_price == 0, 'cleaned_price'] = np.nan
    
    # return dataframe
    return df

def reformat_profiles_df(df):
    df = df.drop_duplicates()

    # Mark deleted accounts
    df['cleaned_deleted_status'] = df['json_data'].isnull()

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
    df['cleaned_ranking'] = df['ranking'].str.replace(',', '')
    df['cleaned_ranking'] = df['cleaned_ranking'].fillna(value=0)
    df['cleaned_ranking'] = df['cleaned_ranking'].astype(int)

    # return dataframe
    return df

def split_reviewer_data(json_data):
    decoded_data = ast.literal_eval(json_data)
    return decoded_data['contributions'], decoded_data['marketplaceId'], decoded_data['locale']

def normalize_ratings(ratings):
    s_ratings = ratings.split()
    return float(s_ratings[0])/float(s_ratings[3])

def decode_comments(text):
    text = normalize("NFKD", text).encode("ascii", "ignore").decode("utf-8", "ignore")
    text = html.unescape(text)
    return ''.join([x for x in text if x.isprintable()])