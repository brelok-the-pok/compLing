from nltk.tag import pos_tag
from nltk.stem.wordnet import WordNetLemmatizer
from nltk import FreqDist, classify, NaiveBayesClassifier
from nltk.corpus import stopwords, twitter_samples
from nltk.tokenize import word_tokenize
from nltk.tokenize import TweetTokenizer
import re, string,random
import pandas as pd
from nltk.stem import SnowballStemmer
import pickle
from pathlib import Path

#Устранение шума, нормализация
def remove_noise(stemmer, tweet_tokens,stop_words=()):
    cleaned_tokens=[]
    for token, tag in pos_tag(tweet_tokens, lang='rus'): #Определим теги
        #Удалим гиперссылки и пользователей
        token=re.sub('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+#]|[!*\(\),]|'\
        '(?:%[0-9a-fA-F][0-9a-fA-F]))+','', token)
        token=re.sub("(@[A-Za-z0-9_]+)","", token)
        token = re.sub("RT", "", token)
        if token not in string.punctuation:
            token=stemmer.stem(token)
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


if __name__ == "__main__":

    model_file = Path('classifier.pickle')

    if  not model_file.exists():
        # Загрузка данных их файла
        file_pos = pd.read_csv('positive.csv', sep=';')
        file_neg = pd.read_csv('negative.csv', sep=';')

        # Получим наборы данных для разных типов твитов
        positive_tweets = file_pos.iloc[:, 3].tolist().copy()
        negative_tweets = file_neg.iloc[:, 3].tolist().copy()

        # Разобьем на токены
        tknzr = TweetTokenizer()
        positive_tweet_tokens = [tknzr.tokenize(tweet) for tweet in positive_tweets]
        negative_tweet_tokens = [tknzr.tokenize(tweet) for tweet in negative_tweets]
        stop_words = stopwords.words("russian")  # Загрузим стоп слова
        print(positive_tweet_tokens[500])
        print(negative_tweet_tokens[500])

        # Уберем шум, нормализуем
        stemmer = SnowballStemmer('russian')
        positive_cleaned_tokens_list = []
        negative_cleaned_tokens_list = []
        for tokens in positive_tweet_tokens:
            positive_cleaned_tokens_list.append(remove_noise(stemmer, tokens, stop_words))
        for tokens in negative_tweet_tokens:
            negative_cleaned_tokens_list.append(remove_noise(stemmer, tokens, stop_words))
        print(positive_cleaned_tokens_list[500])
        print(negative_cleaned_tokens_list[500])

        # Получим частоту встречаемости
        all_pos_words = get_all_words(positive_cleaned_tokens_list)
        freq_dist_pos = FreqDist(all_pos_words)
        print(freq_dist_pos.most_common(10))

        # Создание словарей
        positive_tokens_for_model = get_tweets_for_model(positive_cleaned_tokens_list)
        negative_tokens_for_model = get_tweets_for_model(negative_cleaned_tokens_list)

        # Создание обучающей и тестовой выборки
        positive_dataset = [(tweet_dict, "Positive") for tweet_dict in positive_tokens_for_model]
        negative_dataset = [(tweet_dict, "Negative") for tweet_dict in negative_tokens_for_model]
        dataset = positive_dataset + negative_dataset
        random.shuffle(dataset)  # Смешиваем
        train_data = dataset[:150000]  # Разбиваем в отношении 70/30
        test_data = dataset[150000:]

        # Создание, обучение и тестирования модели
        classifier = NaiveBayesClassifier.train(train_data)
        print("Accuracy is:", classify.accuracy(classifier, test_data))
        print(classifier.show_most_informative_features(10))

        f = open('classifier.pickle', 'wb')
        pickle.dump(classifier, f)
        f.close()
    else:
        f = open('classifier.pickle', 'rb')
        classifier = pickle.load(f)
        f.close()

    # Проверка работы на отдельном предложении
    tknzr = TweetTokenizer()
    stop_words = stopwords.words("russian")
    stemmer = SnowballStemmer('russian')
    custom_tweets = []


    custom_tweets.append("Ура́ — восклицательное междометие, употребляющееся в качестве торжествующего восклицания")
    custom_tweets.append("Мы долго молча отступали, Досадно было, боя ждали, Ворчали старики")

    custom_tweets.append("Весенний день - сирень, сирень, Весёлые каникулы!")
    custom_tweets.append("И скучно и грустно, и некому руку подать В минуту душевной невзгоды")

    custom_tweets.append("За спором не заметили. Как село солнце красное, Как вечер наступил :(")
    custom_tweets.append("Ходит кошка в корридоре, У нее большое горе Злые люди бедной киске Не дают украсть сосиски")

    custom_tweets.append("Король вас может сделать Всесильным богачем, И все на этом свете Вам будет нипочем!")
    custom_tweets.append("Но только раздался звонок, Удрал из вагона щенок. Хватились на станции Дно: Потеряно место одно.")

    custom_tweets.append("Я сегодня лягу раньше :)) , Раньше лампу погашу, Но зато тебя пораньше Разбудить меня прошу.")
    custom_tweets.append("Ведь были ж схватки боевые, Да, говорят, еще какие! Недаром помнит вся Россия Про день Бородина!")


    custom_tweets_tokens = []
    for tokens in custom_tweets:
        custom_tweets_tokens.append(remove_noise(stemmer, tknzr.tokenize(tokens), stop_words))

    custom_tokens_mod = get_tweets_for_model(custom_tweets_tokens)
    positive_custom_tokens = [(tweet_dict, "Positive") for tweet_dict in custom_tokens_mod]
    print("Positive:", classify.accuracy(classifier, positive_custom_tokens))

    for tokens in custom_tweets_tokens:
        print("{}: {}".format(tokens,classifier.classify(dict([token, True] for token in tokens))))


