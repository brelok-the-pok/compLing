from nltk.tag import pos_tag
from nltk import classify
from nltk.corpus import stopwords
from nltk.tokenize import TweetTokenizer
import string
import pickle
from pathlib import Path
import pymorphy2
from pymongo import MongoClient
from nltk.probability import ProbabilisticMixIn

#Устранение шума, нормализация
def remove_noise(stemmer, tweet_tokens,stop_words=()):
    cleaned_tokens=[]
    for token, tag in pos_tag(tweet_tokens, lang='rus'): #Определим теги
        if token not in string.punctuation:
            token=stemmer.parse(token)[0].normal_form
            #оставим только не пустые, не знак пунктуации и не стоп слово
            if len(token)>0  and token.lower() not in stop_words:
                cleaned_tokens.append(token.lower())#в нижнем регистре
    return cleaned_tokens



#Генератор токенов из списка
def get_all_words(cleaned_tokens_list):
    for tokens in cleaned_tokens_list:
        for token in tokens:
            yield token

#Создание словаря
def get_tweets_for_model(cleaned_tokens_list):
    for tweet_tokens in cleaned_tokens_list:
        yield dict([token,True]for token in tweet_tokens)

def in_bd(db):
    db.list_collection_names()
    person = db.person
    new_person = [{"person": "ЛЯХОВА НАТАЛЬЯ",
                  "text": ["В администрации Волгоградской области опубликовали среднюю зарплату за 2019 год главных врачей , главных бухгалтеров и заместителей главных врачей медицинских организаций региона – больниц , поликлиник , центров и диспансеров .",
                           "Как сообщает ИА Высота 102 со ссылкой на эти данные , самым высокооплачиваемым главным врачом среди медучреждений региона стала Наталья Ляхова . "],
                  "textton": [],
                  "ton": 0
                  },
                 {"author": "КУШНИРУК НАТАЛЬЯ",
                  "text": ["Среднемесячная зарплата главного врача городской клинической больницы скорой медицинской помощи № 25 за прошлый год составила 135 тысяч 422 рубля .",
                           "Немногим меньше получала главный врач областной клинической больницы № 1 Наталья Кушнирук – 124 тысячи 832 рубля . "],
                  "textton": [],
                  "ton": 0
                  },
                 {"author": "ВЕРОВСКАЯ ТАТЬЯНА",
                  "text": ["Главный врач Волгоградского клинического перинатального центра № 2 Татьяна Веровская зарабатывала в прошлом году в среднем 114 тысяч 344 рубля в месяц ."],
                  "textton":[],
                  "ton": 0
                  }
                 ]
    person = person.insert_many(new_person)

def get_ton(classifier,tknzr,stop_words,stemmer, text):
    tokens = []
    for texti in text:
        tokens.append(remove_noise(stemmer, tknzr.tokenize(texti[0]), stop_words))
    tokens_mod = get_tweets_for_model(tokens)
    positive_tokens = [(dict, "Positive") for dict in tokens_mod] #Считаем, что все предложения положительны
    tonperson = classify.accuracy(classifier, positive_tokens) #Получаем на сколько положительны


    textton=[]

    for tokensi in tokens:
        textton.append(classifier.classify(dict([token, True] for token in tokensi)))
    print(textton)
    return tonperson,textton


if __name__ == "__main__":

    model_file = Path('classifier.pickle')
    if not model_file.exists():
        print("Необходимо создать модель.")
    else:
        #Подключаемся к базе данных
        client = MongoClient('mongodb://localhost:27017/')
        db = client.test_database
        #in_bd(db)

        #Подключае модель и необходимые элементы анализа
        f = open('classifier.pickle', 'rb')
        classifier = pickle.load(f)
        f.close()
        tknzr = TweetTokenizer()
        stop_words = stopwords.words("russian")
        stemmer = pymorphy2.MorphAnalyzer()


        #Обработка персон
        person = db.person
        for personi in person.find():
            ton,textton = get_ton(classifier,tknzr,stop_words,stemmer, personi["text"])
            person.update_one({"_id": personi["_id"]},  {"$set":{"ton": ton}})
            person.update_one({"_id": personi["_id"]}, {"$set": {"textton": textton}})





