import re
import string
from collections import Counter
from unicodedata import normalize

import matplotlib.pyplot as plt
import nltk
import pandas as pd
from nltk.corpus import stopwords, wordnet
from wordcloud import WordCloud

import html
import icu
from polyglot.detect import Detector

resources = ["wordnet", "stopwords", "punkt", \
             "averaged_perceptron_tagger", "maxent_treebank_pos_tagger","wordnet"]

for resource in resources:
    try:
        nltk.data.find("tokenizers/" + resource)
    except LookupError:
        nltk.download(resource)


def reformat_reviews_df(df,product_id,scraping_checklist_df):
    # Drop rows which are actually headers
    df = df[df.ASIN != 'ASIN']

    # Fill in missing ASIN
    df['ASIN'] = df['ASIN'].fillna(value=product_id)

    # Reformat profile link for profile crawling
    df['new_profile_link'] = "https://www.amazon.com" + df['profile_link'].astype(str)

    # Check if stars column is correctly named:
    if 'ï»¿stars' in df.columns.values.tolist() and 'stars' not in df.columns.values.tolist():
        df = df.rename(columns={'ï»¿stars':'stars'})

    # Assign Product Name
    df = pd.merge(df,scraping_checklist_df,left_on=['ASIN'], right_on = ['Product ASIN'], how = 'left')

    # Lowercase title text
    df['clean_title'] = df['title'].str.lower()

    # Decode & lowercase comment text
    df['decoded_comment'] = df.comment.astype(str)
    df['decoded_comment'] = df.decoded_comment.apply(lambda x: html.unescape(x))
    df['decoded_comment'] = df.decoded_comment.apply(lambda text: ''.join(x for x in text if x.isprintable()))
    df["decoded_comment"] = df["decoded_comment"].apply(lambda text: normalize("NFKD", text).encode("ascii", "ignore").decode("utf-8", "ignore"))
    df['decoded_comment']= df['decoded_comment'].str.lower()

    # Cleaning stars
    df['ratings'] = df.stars.astype(str)
    df['ratings'] = df.ratings.apply(lambda x: x.split())
    df['ratings'] = df.ratings.apply(lambda x: float(x[0])/float(x[3]))

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
    df['location'] = df.date.astype(str)
    df['date_posted'] = df.date.astype(str)
    df['location'] = df.location.apply(lambda x: (' '.join(x.split(' ')[3:])).split('on')[0].strip())
    df['date_posted'] = df.date_posted.apply(lambda x: (' '.join(x.split(' ')[3:])).split('on')[1].strip())

    # Identifying opinion's language
    df['poly_obj'] = df.decoded_comment.apply(lambda x: Detector(x, quiet=True))
    df['language'] = df['poly_obj'].apply(lambda x: icu.Locale.getDisplayName(x.language.locale))
    df['language_confidence'] = df['poly_obj'].apply( lambda x: x.language.confidence)

    # Lowercase product name
    df['clean_product_name'] = df['Product name'].str.lower()

    # Remove unnecessary columns
    for column in ['poly_obj','Product ASIN']:
        del df[column]

    # return dataframe
    return df


def reformat_profile_df(df):
    # Decode & lowercase comment text
    df['decoded_comment'] = df.text.astype(str)
    df['decoded_comment'] = df.decoded_comment.apply(lambda x: html.unescape(x))
    df['decoded_comment'] = df.decoded_comment.apply(lambda text: ''.join(x for x in text if x.isprintable()))
    df["decoded_comment"] = df["decoded_comment"].apply(lambda text: normalize("NFKD", text).encode("ascii", "ignore").decode("utf-8", "ignore"))
    df['decoded_comment']= df['decoded_comment'].str.lower()

    # Lowercase product name
    df['clean_product_name'] = df['product'].str.lower()

    # convert ranking string to integer
    df['ranking'] = df['ranking'].str.replace(',', '')
    df['ranking'] = df['ranking'].fillna(value=0)
    df['ranking'] = df['ranking'].astype(int)

    # return dataframe
    return df


def remove_links(text):
    text = re.sub(r'http\S+', '', text) # remove http links
    text = re.sub(r'bit.ly/\S+', '', text) # remove bitly links
    text = re.sub(r'www\S+', '', text) # remove www links
    text = re.sub(r'.*\.com', '', text)
    return text


def removeEmoticons(text):
    """ Removes emoticons from text """
    text = re.sub(':\)|;\)|:-\)|\(-:|:-D|=D|:P|xD|X-p|\^\^|:-*|\^\.\^|\^\-\^|\^\_\^|\,-\)|\)-:|:\'\(|:\(|:-\(|:\S|T\.T|\.\_\.|:<|:-\S|:-<|\*\-\*|:O|=O|=\-O|O\.o|XO|O\_O|:-\@|=/|:/|X\-\(|>\.<|>=\(|D:', '', text)
    return text


def remove_symbols(text):
    """ Removes all symbols and keep alphanumerics """
    whitelist = []
    return [re.sub(r'([^a-zA-Z0-9\s]+?)',' ',word) for word in text if word not in whitelist]


def keep_alphanum(text):
    """ Keep Alphanumeric characters """
    return [word for word in text if word.isalnum()]


def remove_stopwords(text):
    """ Remove Stopwords """
    stop_list = stopwords.words('english')
    stop_list += string.punctuation
    stop_list += [] #any other stop words
    return [word for word in text if word not in stop_list]


def remove_apostrophes(text):
    """ Remove words which have 's with a space """
    return [re.sub(r"'s", "",word) for word in text]


def replaceSlang(text):
    """ Creates a dictionary with slangs and their equivalents and replaces them """
    with open('/content/drive/My Drive/FYP/FYP Y4S1/preprocessing_resources/slangs.txt',encoding="ISO-8859-1") as file:
        slang_map = dict(map(str.strip, line.partition('\t')[::2]) for line in file if line.strip())
    return [slang_map[word] if word in slang_map.keys() else word for word in text]


def replaceContraction(text):
    """ Creates a dictionary with contractions and their equivalents and replaces them """
    with open('/content/drive/My Drive/FYP/FYP Y4S1/preprocessing_resources/contractions.txt',encoding="ISO-8859-1") as file:
        contraction_map = dict(map(str.strip, line.partition('\t')[::2]) for line in file if line.strip())
    return [contraction_map[word] if word in contraction_map.keys() else word for word in text]


def nltk_tag_to_wordnet_tag(nltk_tag):
    """ function to convert nltk tag to wordnet tag """
    if nltk_tag.startswith('J'):
        return wordnet.ADJ
    elif nltk_tag.startswith('V'):
        return wordnet.VERB
    elif nltk_tag.startswith('N'):
        return wordnet.NOUN
    elif nltk_tag.startswith('R'):
        return wordnet.ADV
    else:
        return None


def replaceElongated(word):
    """ Replaces an elongated word with its basic form, unless the word exists in the lexicon """
    repeat_regexp = re.compile(r'(\w*)(\w)\2(\w*)')
    repl = r'\1\2\3'
    if wordnet.synsets(word):
        return word
    repl_word = repeat_regexp.sub(repl, word)
    if repl_word != word:
        return replaceElongated(repl_word)
    else:
        return repl_word


def replaceElongatedText(text):
    return [replaceElongated(word) for word in text]


def remove_multispaces(text):
    """ Replace multiple spaces with only 1 space """
    return [re.sub(r' +', " ",word) for word in text]


def normalize_word(text):
    """ Own mapping function """
    replacement_dict = {"l'oreal": 'loreal', "l'oreals":'loreal','b/c': 'because','amazon.com':'amazon', \
                        'cake-y':'cakey', 'build-able':'buildable', 'wal-mart':'walmart', \
                        'q-tip':'cotton swab','l"oreal': 'loreal', 'l"oreals':'loreal', \
                        "a/c":"air conditioning", "co-workers":"colleague", "co-worker":"colleague", \
                        "y'all":"you all"}

    text = [replacement_dict[word] if word in replacement_dict.keys() else word for word in text]

    return text


def lemmatize_words(feedback):
    lemmatizer = nltk.stem.WordNetLemmatizer()
    # Pos tagging
    nltk_tagged = nltk.pos_tag(feedback)

    #tuple of (token, wordnet_tag)
    wordnet_tagged = map(lambda x: (x[0], nltk_tag_to_wordnet_tag(x[1])), nltk_tagged)

    # lemmatizing
    lemmatized_sentence = []
    for word, tag in wordnet_tagged:
        if tag is not None and word not in stopwords.words('english'):
            lemmatized_sentence.append(lemmatizer.lemmatize(word, tag))
        else:
            lemmatized_sentence.append(lemmatizer.lemmatize(word))

    return (lemmatized_sentence)


def clean_text(texts):
    new_texts = [nltk.word_tokenize(str(text)) for text in texts]
    new_texts = [normalize_word((text)) for text in new_texts]
    new_texts = [' '.join(text) for text in new_texts]
    new_texts = [remove_links(text) for text in new_texts]
    new_texts = [removeEmoticons(text) for text in new_texts]
    new_texts = [nltk.word_tokenize(str(text)) for text in new_texts]
    new_texts = [replaceSlang(text) for text in new_texts]
    new_texts = [replaceContraction(text) for text in new_texts]
    new_texts = [normalize_word((text)) for text in new_texts]
    new_texts = [remove_apostrophes((text)) for text in new_texts]
    new_texts = [replaceElongatedText((text)) for text in new_texts]
    # new_texts = [remove_symbols((text)) for text in new_texts]
    new_texts = [keep_alphanum(text) for text in new_texts]
    new_texts = [lemmatize_words(text) for text in new_texts]
    new_texts = [remove_stopwords(text) for text in new_texts]
    new_texts = [remove_multispaces(text) for text in new_texts]
    new_texts = [normalize_word((text)) for text in new_texts]
    new_texts = [' '.join(text) for text in new_texts]

    return new_texts


def generate_wordclouds(df,column,usecase):
    ans = []
    for text in df[column].str.replace('\n', ' ').str.replace('\t', ' ').str.lower().str.strip():
        text = str(text)
        text = nltk.word_tokenize(text)
        if usecase == "symbols":
            for word in text:
                if re.findall('\W\S',word) != []:
                    ans.append(word)
        elif usecase == 'digits':
            for word in text:
                if re.findall(r'\d+',word) != []:
                    ans.append(word)
        elif usecase == "consective":
            for word in text:
                if re.findall(r'([a-z])\1\1+',word) != []:
                    ans.append(word)
    try:
        word_cloud_dict=Counter(ans)
        wordcloud = WordCloud(width = 1000, height = 500).generate_from_frequencies(word_cloud_dict)

        plt.figure(figsize=(15,8))
        plt.imshow(wordcloud)
        plt.axis("off")
        plt.show()
    except:
        print("Data is cleaned")
