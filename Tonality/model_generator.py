from nltk.tag import pos_tag
from nltk import FreqDist, classify, NaiveBayesClassifier
from nltk.corpus import stopwords
from nltk.tokenize import TweetTokenizer
import re, string,random
import pandas as pd
import pickle
import pymorphy2

#Устранение шума, нормализация
def remove_noise(stemmer, tweet_tokens,stop_words=()):
    cleaned_tokens=[]
    for token, tag in pos_tag(tweet_tokens, lang='rus'): #Определим теги
        #Удалим гиперссылки и пользователей
        token=re.sub('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+#]|[!*\(\),]|'\
        '(?:%[0-9a-zA-Z][0-9a-zA-Z]))+','', token)
        token=re.sub("(@[A-Za-z0-9_]+)","", token)
        token = re.sub("RT", "", token)
        token = re.sub("(\.{2,})", "", token)

        if token not in string.punctuation and tag!="NONLEX":
            if tag!="NONLEX":
                token=stemmer.parse(token)[0].normal_form
                token = re.sub("(^это$|^весь$|^ещё$)", "", token)
            #оставим только не пустые, не знак пунктуации и не стоп слово
            if len(token)>0  and token.lower() not in stop_words:
                cleaned_tokens.append(token.lower())#в нижнем регистре
    return cleaned_tokens



#Получение форматированного списка токенов
def get_all_words(cleaned_tokens_list):
    for tokens in cleaned_tokens_list:
        for token in tokens:
            yield token

#Создание словаря
def get_tweets_for_model(cleaned_tokens_list, word_features):
    for tweet_tokens in cleaned_tokens_list:
        yield dict([token,token in word_features]for token in tweet_tokens)




def __main__():
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
    stemmer = pymorphy2.MorphAnalyzer()
    positive_cleaned_tokens_list = []
    negative_cleaned_tokens_list = []
    for tokens in positive_tweet_tokens:
        positive_cleaned_tokens_list.append(remove_noise(stemmer, tokens, stop_words))
    print(positive_cleaned_tokens_list[500])
    for tokens in negative_tweet_tokens:
        negative_cleaned_tokens_list.append(remove_noise(stemmer, tokens, stop_words))
    print(negative_cleaned_tokens_list[500])

    # Получим частоту встречаемости
    all_pos_words = get_all_words(positive_cleaned_tokens_list)
    freq_dist_pos = FreqDist(all_pos_words)
    word_features_pos = list(freq_dist_pos)[:4000]
    print(list(freq_dist_pos)[:10])
    all_neg_words = get_all_words(negative_cleaned_tokens_list)
    freq_dist_neg = FreqDist(all_neg_words)
    word_features_neg = list(freq_dist_neg)[:4000]
    print(list(freq_dist_neg)[:10])

    # Создание словарей
    positive_tokens_for_model = get_tweets_for_model(positive_cleaned_tokens_list, word_features_pos)
    negative_tokens_for_model = get_tweets_for_model(negative_cleaned_tokens_list, word_features_neg)

    # Создание обучающей и тестовой выборки
    positive_dataset = [(tweet_dict, "Positive") for tweet_dict in positive_tokens_for_model]
    negative_dataset = [(tweet_dict, "Negative") for tweet_dict in negative_tokens_for_model]
    dataset = positive_dataset + negative_dataset
    random.shuffle(dataset)  # Смешиваем
    knife= int((len(dataset)*7)/10)
    train_data = dataset[:knife]  # Разбиваем в отношении 70/30
    test_data = dataset[knife:]

    # Создание, обучение и тестирования модели
    classifier = NaiveBayesClassifier.train(train_data)
    print("Accuracy is:", classify.accuracy(classifier, test_data))
    print(classifier.show_most_informative_features(10))

    f = open('classifier.pickle', 'wb')
    pickle.dump(classifier, f)
    f.close()

    # errors = []
    # for (name, tag) in test_data:
    #     guess = classifier.classify(name)
    #     if guess != tag:
    #         errors.append((tag, guess, name))
    # for err in errors:
    #     print(err)

if __name__ == "__main__":
    __main__()



