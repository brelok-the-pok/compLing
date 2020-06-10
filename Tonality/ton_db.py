from nltk.tag import pos_tag
from nltk import classify
from nltk.corpus import stopwords
from nltk.tokenize import TweetTokenizer
import string
import pickle
from pathlib import Path
import pymorphy2
from pymongo import MongoClient


# Устранение шума, нормализация
def remove_noise(stemmer, tweet_tokens, stop_words=()):
    cleaned_tokens = []
    for token, tag in pos_tag(tweet_tokens, lang='rus'):  # Определим теги
        if token not in string.punctuation:
            token = stemmer.parse(token)[0].normal_form
            # оставим только не пустые, не знак пунктуации и не стоп слово
            if len(token) > 0 and token.lower() not in stop_words:
                cleaned_tokens.append(token.lower())  # в нижнем регистре
    return cleaned_tokens


# Приведение к структуре
def get_for_model(cleaned_tokens_list):
    for tweet_tokens in cleaned_tokens_list:
        yield dict([token, True] for token in tweet_tokens)


def get_ton(classifier, tknzr, stop_words, stemmer, text):
    tokens = []
    for texti in text:
        tokens.append(remove_noise(stemmer, tknzr.tokenize(texti), stop_words))
    tokens_mod = get_for_model(tokens)
    positive_tokens = [(dict, "Positive") for dict in tokens_mod]  # Считаем, что все предложения положительны
    tonperson = classify.accuracy(classifier, positive_tokens)  # Получаем на сколько положительны

    textton = []

    for tokensi in tokens:
        textton.append(classifier.classify(dict([token, True] for token in tokensi)))
    return tonperson, textton



def __main__():
    model_file = Path('classifier.pickle')
    if not model_file.exists():
        print("Необходимо создать модель.")
    else:
        # Подключаемся к базе данных
        client = MongoClient('mongodb+srv://vsevo:1234@pisosteamcluster-sivo7.mongodb.net/NewsV102?retryWrites=true&w=majority')
        db = client.NewsV102
        # in_bd(db)

        # Подключае модель и необходимые элементы анализа
        f = open('classifier.pickle', 'rb')
        classifier = pickle.load(f)
        f.close()
        tknzr = TweetTokenizer()
        stop_words = stopwords.words("russian")
        stemmer = pymorphy2.MorphAnalyzer()

        # Обработка персон
        personTon = db.PersonsTon #новая таблица тональностей персон и предложений
        personNews = db.PersonsToNews
        for personNewsi in personNews.find():
            ton, textton = get_ton(classifier, tknzr, stop_words, stemmer, personNewsi["news"])
            if personTon.find({"_id": personNewsi["_id"]}).count()==0:#если нет
                personTon.insert_one({"_id": personNewsi["_id"], "textton": textton, "ton": ton})
            else:
                personTon.update_one({"_id": personNewsi["_id"]}, {"$set": {"textton": textton, "ton": ton}})

if __name__ == "__main__":
    __main__()


