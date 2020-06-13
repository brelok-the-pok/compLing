from subprocess import Popen, PIPE, STDOUT
from pymongo import MongoClient
from tqdm.auto import trange, tqdm
import sys, re
from multiprocessing.dummy import Pool as ThreadPool
from nltk.corpus import stopwords

from pyspark.sql import SparkSession
from pyspark.sql.functions import format_number as fmt
from pyspark.ml.feature import Word2Vec, Word2VecModel
from pyspark.sql import Row

delimiter = '<end of news>'


def take_parse_save_persons():
    lastNum = 0
    # Берём данные из БД
    client = MongoClient(
        "mongodb+srv://pok:123@pisosteamcluster-sivo7.mongodb.net/NewsV102?retryWrites=true&w=majority")
    db = client.NewsV102
    news = db.AllOfAllNews  # Это все записи с новостями на данный момент

    # Вытаскиваем из новостей только тексты и скидываем их в файлик
    allNews = news.find()

    news_count = allNews.count()
    n = news_count
    # Открываем файл куда будем кидать отпаршеные томитой тексты
    write_file = open('newsTexts/allNewsRaw.txt', 'w')
    path_to_tomita = '/home/pok/sem/tomita-parser/build/bin'

    for i in trange(lastNum, news_count, file=sys.stdout, desc='outer loop'):
        current_text = allNews[i]['text']
        command = 'echo "{0}" | {1}/tomita-parser {1}/config.proto'.format(current_text, path_to_tomita)
        p = Popen(command, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT,
                  close_fds=True)
        p.wait()

        read_file = open('./TomitaOut/facts.txt', 'r')
        write_file.write(read_file.read() + delimiter)
        write_file.write(current_text + delimiter)
        read_file.close()
    write_file.close()

    # Парсим через томиту получая имена в текстах


def take_parse_save_places():
    lastNum = 0
    # Берём данные из БД
    client = MongoClient(
        "mongodb+srv://pok:123@pisosteamcluster-sivo7.mongodb.net/NewsV102?retryWrites=true&w=majority")
    db = client.NewsV102
    news = db.AllOfAllNews  # Это все записи с новостями на данный момент

    # Вытаскиваем из новостей только тексты и скидываем их в файлик
    allNews = news.find()

    news_count = allNews.count()
    n = news_count

    def parse_plz(params: list):
        allNews = params[0]
        start = params[1]
        end = params[2]
        whereToWrite = params[3]

        some_file = open('newsTexts/{}.txt'.format(whereToWrite), 'w')
        for i in trange(start, end, file=sys.stdout, desc='outer loop'):
            current_text = allNews[i]['text']
            some_file.write(current_text + delimiter)
        some_file.close()

    start_list = [0, int(n / 8) + 1, int(n / 4) + 1, int(n / 2) + 1, int(n * 1.6) + 1, int(n * 3 / 4) + 1,
                  int(n * 0.875) + 1]
    end_list = [int(n / 8), int(n / 4), int(n / 2), int(n * 1.6), int(n * 3 / 4), int(n * 0.875), n]
    files_list = ['try/1', 'try/2', 'try/3', 'try/4', 'try/5', 'try/6', 'try/7']
    params = [allNews, start_list, end_list, files_list]
    parama_params = [
        [allNews, start_list[0], end_list[0], files_list[0]],
        [allNews, start_list[1], end_list[1], files_list[1]],
        [allNews, start_list[2], end_list[2], files_list[2]],
        [allNews, start_list[3], end_list[3], files_list[3]],
        [allNews, start_list[4], end_list[4], files_list[4]],
        [allNews, start_list[5], end_list[5], files_list[5]],
        [allNews, start_list[6], end_list[6], files_list[6]],
    ]
    Pool = ThreadPool(7)
    Pool.map(parse_plz, parama_params)


def clear_tomita_output():
    file = open('newsTexts/tomitaOutPlaces.txt')
    fullData = file.read()
    file.close()

    fullData = fullData \
        .replace('\n\n', '') \
        .replace('\r', '') \
        .replace('\\x', '') \
        .replace('\t', '')

    file = open('newsTexts/clearedPlaces.txt', 'w')
    file.write(fullData)
    file.close()


def make_persons_and_texts():
    file = open('newsTexts/clearedPersons.txt')
    texts = file.read().split(delimiter)
    file.close()
    pattern1 = '(.*) \. ((\nPerson\n{\nName = ([а-яА-Я ]*)\n}){1,})'
    pattern2 = 'Person\n{\nName = ([а-яА-Я ]*)\n}'

    news_texts = []
    persons_names = []
    texts_count = len(texts)
    for i in trange(texts_count, file=sys.stdout, desc='outer loop'):
        while len(texts[i]) > 0:
            res1 = re.search(pattern1, texts[i])
            if res1 is None:
                break
            texts[i] = texts[i].replace(res1.group(0), '')
            res2 = re.findall(pattern2, res1.group(2))
            news_texts.append(res1.group(1))
            persons_names.append(res2)
    file = open('newsTexts/personsAndTexts.txt', 'w')
    news_count = len(news_texts)
    for i in trange(news_count, file=sys.stdout, desc='outer loop'):
        for j in range(0, len(persons_names[i])):
            file.write('{0}\n{1}{2}\n'.format(persons_names[i][j], news_texts[i], delimiter))
    file.close()


def make_places_and_texts():
    file = open('newsTexts/clearedPlaces.txt')
    texts = file.read().split(delimiter)
    file.close()
    pattern1 = '(.*) \. ((\nPlace\n{\nName = ([а-яА-Я -]*)\n}){1,})'
    pattern2 = 'Place\n{\nName = ([а-яА-Я -]*)\n}'

    news_texts = []
    places_names = []
    texts_count = len(texts)
    for i in trange(texts_count, file=sys.stdout, desc='outer loop'):
        while len(texts[i]) > 0:
            res1 = re.search(pattern1, texts[i])
            if res1 is None:
                break
            texts[i] = texts[i].replace(res1.group(0), '')
            res2 = re.findall(pattern2, res1.group(2))
            news_texts.append(res1.group(1))
            places_names.append(res2)
    file = open('newsTexts/placesAndTexts.txt', 'w')
    news_count = len(news_texts)
    for i in trange(news_count, file=sys.stdout, desc='outer loop'):
        for j in range(0, len(places_names[i])):
            file.write('{0}\t{1}{2}'.format(places_names[i][j], news_texts[i], delimiter))
    file.close()


def compare_persons():
    file = open('newsTexts/personsAndTexts.txt')
    persons_from_news = file.read().split(delimiter)
    file.close()

    file = open('names.txt')
    known_persons = file.read().split('\n')
    file.close()

    news_to_person = []  # Имя и новость

    for person in persons_from_news:
        news_to_person.append(person.split('\n'))

    for i in range(1, len(news_to_person)):
        news_to_person[i].remove(news_to_person[i][0])

    all_news_for_person = {}  # Словарь в котором для каждой персоны прописаны все новости

    n = len(known_persons)
    k = len(news_to_person)
    # в news_to_person[i][0] теперь лежит имя, а в news_to_person[i][1] новость в которой он упоминается
    for i in trange(n, file=sys.stdout, desc='outer loop'):
        all_news_for_person[known_persons[i]] = ''
        for j in trange(k - 1, file=sys.stdout):
            if news_to_person[j][0].lower() in known_persons[i].lower():
                all_news_for_person[known_persons[i]] += news_to_person[j][1] + delimiter
                # persons_from_news.remove(persons_from_news[j])

    print(persons_from_news)

    file = open('newsTexts/allNewsForEachPerson.txt', 'w')

    for key in all_news_for_person:
        file.write(key + '\t' + all_news_for_person[key] + '\n')


def compare_places():
    file = open('newsTexts/placesAndTexts.txt')
    places_from_news = file.read().split(delimiter)
    file.close()

    file = open('place_names.txt')
    known_places = file.read().split('\n')
    file.close()

    news_to_places = []  # Имя и новость

    for place in places_from_news:
        news_to_places.append(place.split('\t'))

    all_news_for_places = {}  # Словарь в котором для каждой персоны прописаны все новости

    n = len(known_places)
    k = len(news_to_places)
    # в news_to_places[i][0] теперь лежит имя, а в news_to_places[i][1] новость в которой он упоминается
    for i in trange(n, file=sys.stdout, desc='outer loop'):
        all_news_for_places[known_places[i]] = ''
        for j in trange(k - 1, file=sys.stdout):
            place_news = news_to_places[j][0].lower().replace('"', '')
            place_known = known_places[i].lower()

            def complicated_in(text1: str, text2: str):
                text1_splited = text1.split()
                text2_splited = text2.split()
                count_of_in = 0
                for word1 in text1_splited:
                    for word2 in text2_splited:
                        if len(word1) > 5:
                            if word1.replace(word1[len(word1) - 3: len(word1)], '') in word2.replace(
                                    word2[len(word2) - 3: len(word2)], ''):
                                return True
                return False

            if complicated_in(place_news, place_known):
                all_news_for_places[known_places[i]] += news_to_places[j][1] + delimiter
            # if place_news in place_known:
            #    all_news_for_places[known_places[i]] += news_to_places[j][1] + delimiter
            # places_from_news.remove(places_from_news[j])

    print(places_from_news)

    file = open('newsTexts/allNewsForEachPlace.txt', 'w')

    for key in all_news_for_places:
        file.write(key + '\t' + all_news_for_places[key] + '\n')


def save_persons_to_db():
    def save_persons(persons):
        for name, news in tqdm(persons.items()):
            db_entity = {"name": name, "news": news}
            persons_news.insert_one(db_entity)

    client = MongoClient(
        "mongodb+srv://pok:123@pisosteamcluster-sivo7.mongodb.net/NewsV102?retryWrites=true&w=majority")
    db = client.NewsV102  # Имя базы данных
    persons_news = db.PersonsToNews  # Имя коллекции

    file = open('newsTexts/allNewsForEachPerson.txt')
    data = file.read().split('\n')
    file.close()

    listOfPersons = []
    persons = {}
    for i in trange(len(data) - 2):
        listOfPersons.append(data[i])
        listOfPersons[i] = listOfPersons[i].split('\t')
        listOfPersons[i][1] = listOfPersons[i][1].split(delimiter)

        persons[listOfPersons[i][0]] = listOfPersons[i][1]

    return persons
    # save_persons(persons)


def save_places_to_db():
    def save_places(places):
        for name, news in tqdm(places.items()):
            if len(news) > 1:
                db_entity = {"name": name, "news": news}
                places_news.insert_one(db_entity)

    client = MongoClient(
        "mongodb+srv://pok:123@pisosteamcluster-sivo7.mongodb.net/NewsV102?retryWrites=true&w=majority")
    db = client.NewsV102  # Имя базы данных
    places_news = db.PlaceToNews  # Имя коллекции

    file = open('newsTexts/allNewsForEachPlace.txt')
    data = file.read().split('\n')
    file.close()

    listOfPlaces = []
    places = {}
    for i in trange(len(data) - 2):
        listOfPlaces.append(data[i])
        listOfPlaces[i] = listOfPlaces[i].split('\t')
        listOfPlaces[i][1] = listOfPlaces[i][1].split(delimiter)

        places[listOfPlaces[i][0]] = listOfPlaces[i][1]

    # save_places(places)
    return places


def replace_persons_with_unigrams():
    persons = save_persons_to_db()

    for name, news in tqdm(persons.items()):
        FIO = name.split(' ')
        pattern = '{0}[а-я]* {1}[а-я]*|{1}[а-я]* {0}[а-я]*|{1}[а-я]*' \
            .format(FIO[1].capitalize(), FIO[0].capitalize())
        for i in range(len(persons[name])):
            res = re.findall(pattern, persons[name][i])
            for some_res in res:
                persons[name][i] = persons[name][i].replace(some_res, FIO[0].capitalize() + '_' + FIO[1].capitalize())

    file = open('newsTexts/forPersonModel.txt', 'w')
    for name, news in tqdm(persons.items()):
        file.write(name + '\t')
        for i in range(len(persons[name])):
            file.write(persons[name][i] + delimiter)
        file.write('\n')
    file.close()


def replace_places_with_unigrams():
    places = save_places_to_db()

    for name, news in tqdm(places.items()):
        NAME = name.split(' ')
        pattern = ''
        for word in NAME:
            pattern += '[{0}{1}]'.format(word[0].lower(), word[0].capitalize())
            pattern += word[1: len(word) - 3] + '[а-я-]* '
        pattern = pattern[0:len(pattern) - 1]
        for i in range(len(places[name])):
            res = re.findall(pattern, places[name][i])
            for some_res in res:
                places[name][i] = places[name][i].replace(some_res, '_'.join(NAME))

    file = open('newsTexts/forPlacesModel.txt', 'w')
    for name, news in tqdm(places.items()):
        file.write(name + '\t')
        for i in range(len(places[name])):
            file.write(places[name][i] + delimiter)
        file.write('\n')
    file.close()


def read_data_for_mode(file):
    file = open('newsTexts/{}.txt'.format(file))
    data = file.read().split('\n')
    model_data = []
    for i in range(len(data) - 1):
        model_data.append(data[i])
        model_data[i] = model_data[i].split('\t')
        model_data[i][1] = model_data[i][1].split(delimiter)
    return model_data


def make_person_model():
    spark = SparkSession \
        .builder \
        .appName("SimpleApplication") \
        .getOrCreate()

    data = read_data_for_mode('forPersonModel')

    persons = []
    text = []

    for person in data:
        FIO = person[0].split(' ')
        persons.append(FIO[0].capitalize() + '_' + FIO[1].capitalize())
        text += person[1]

    def remove_punctuation(text):
        return re.sub(r'[^\w\s]', '', text)

    for i in range(len(text)):
        text[i] = remove_punctuation(text[i])

    def remove_stop_words(text: list):
        ru_stop = stopwords.words('russian')
        tokens = []
        for line in text:
            line_tokenized = line.split()
            for token in line_tokenized:
                if not token in ru_stop:
                    tokens.append(token)
        return tokens

    tokens = remove_stop_words(text)

    def get_only_words(tokens):
        return list(filter(lambda x: re.match('[а-яА-Я]+', x), tokens))

    tokens = get_only_words(tokens)

    full_text = ' '.join(tokens)

    documentDF = spark.createDataFrame([(full_text.split(" "),)], ["text"])

    model = Word2Vec(vectorSize=3, minCount=5, inputCol="text", outputCol="result")
    model_fitted = model.fit(documentDF)
    model_transformed = model_fitted.transform(documentDF)

    model.save('/home/pok/sem/project/models/person/model5mincount/model')
    model_fitted.save('/home/pok/sem/project/models/person/model5mincount/fitted')
    # model_transformed.save('/home/pok/sem/project/models/model0mincount/transformed')

    spark.stop()


def make_places_model():
    spark = SparkSession \
        .builder \
        .appName("SimpleApplication") \
        .getOrCreate()

    data = read_data_for_mode('forPlacesModel')

    persons = []
    text = []

    for person in data:
        NAME = person[0].split(' ')
        persons.append('_'.join(NAME))
        text += person[1]

    def remove_punctuation(text):
        return re.sub(r'[^\w\s^-]', '', text)

    for i in range(len(text)):
        text[i] = remove_punctuation(text[i])

    def remove_stop_words(text: list):
        ru_stop = stopwords.words('russian')
        tokens = []
        for line in text:
            line_tokenized = line.split()
            for token in line_tokenized:
                if not token.lower() in ru_stop:
                    tokens.append(token)
        return tokens

    tokens = remove_stop_words(text)

    def get_only_words(tokens):
        return list(filter(lambda x: re.match('[а-яА-Я]+', x), tokens))

    tokens = get_only_words(tokens)

    full_text = ' '.join(tokens)

    documentDF = spark.createDataFrame([(full_text.split(" "),)], ["text"])

    model = Word2Vec(vectorSize=3, minCount=0, inputCol="text", outputCol="result")
    model_fitted = model.fit(documentDF)
    model_transformed = model_fitted.transform(documentDF)

    model.save('/home/pok/sem/project/models/places/model0mincount/model')
    model_fitted.save('/home/pok/sem/project/models/places/model0mincount/fitted')
    # model_transformed.save('/home/pok/sem/project/models/model0mincount/transformed')

    spark.stop()


def make_model():
    spark = SparkSession \
        .builder \
        .appName("SimpleApplication") \
        .getOrCreate()

    data = read_data_for_mode('forPersonModel')

    text = []
    data_for_db = []

    for person in data:
        FIO = person[0].split(' ')
        unigram = FIO[0].capitalize() + '_' + FIO[1].capitalize()
        db_entity = {"name": person[0], "news": person[1], "unigram":unigram}
        data_for_db.append(db_entity)
        text += person[1]

    data = read_data_for_mode('forPlacesModel')

    for place in data:
        NAME = place[0].split(' ')
        unigram = '_'.join(NAME)
        db_entity = {"name": place[0], "news": place[1], "unigram": unigram}
        data_for_db.append(db_entity)
        text += place[1]

    def remove_punctuation(text):
        return re.sub(r'[^\w\s^-]', '', text)

    for i in range(len(text)):
        text[i] = remove_punctuation(text[i])

    def remove_stop_words(text: list):
        ru_stop = stopwords.words('russian')
        tokens = []
        for line in text:
            line_tokenized = line.split()
            for token in line_tokenized:
                if not token.lower() in ru_stop:
                    tokens.append(token)
        return tokens

    tokens = remove_stop_words(text)

    def get_only_words(tokens):
        return list(filter(lambda x: re.match('[а-яА-Я]+', x), tokens))

    tokens = get_only_words(tokens)

    full_text = ' '.join(tokens)

    documentDF = spark.createDataFrame([(full_text.split(" "),)], ["text"])

    model = Word2Vec(vectorSize=3, minCount=1, inputCol="text", outputCol="result")
    model_fitted = model.fit(documentDF)
    model_transformed = model_fitted.transform(documentDF)

    model.save('/home/pok/sem/project/models/model0mincount/model')
    model_fitted.save('/home/pok/sem/project/models/model0mincount/fitted')

    spark.stop()

def make_model2():
    spark = SparkSession \
        .builder \
        .appName("SimpleApplication") \
        .getOrCreate()

    data = read_data_for_mode('forPersonModel')

    text = []
    data_for_db = []

    for person in data:
        FIO = person[0].split(' ')
        unigram = FIO[0].capitalize() + '_' + FIO[1].capitalize()
        db_entity = {"name": person[0], "news": person[1], "unigram":unigram}
        data_for_db.append(db_entity)

        for news in person[1]:
            text.append(news)

    data = read_data_for_mode('forPlacesModel')

    for place in data:
        NAME = place[0].split(' ')
        unigram = '_'.join(NAME)
        db_entity = {"name": place[0], "news": place[1], "unigram": unigram}
        data_for_db.append(db_entity)
        for news in place[1]:
            text.append(news)

    def remove_punctuation(text):
        return re.sub(r'[^\w\s^-]', '', text)

    for i in range(len(text)):
        text[i] = remove_punctuation(text[i])

    def remove_stop_words(text: str):
        ru_stop = stopwords.words('russian')
        tokens = []
        line_tokenized = text.split()
        for token in line_tokenized:
            if not token.lower() in ru_stop:
                tokens.append(token)
        return tokens

    tokens_list = []
    for news in text:
        tokens_list.append(remove_stop_words(news))


    def get_only_words(tokens):
        return list(filter(lambda x: re.match('[а-яА-Я]+', x), tokens))

    tokens = []
    for some_tokens in tokens_list:
        tokens.append(get_only_words(some_tokens))

    R = Row('ID', 'news_words')
    documentDF = spark.createDataFrame([R(i, x) for i, x in enumerate(tokens)])
    documentDF.show()

    model = Word2Vec(vectorSize=3, minCount=1, inputCol="news_words", outputCol="result")
    model_fitted = model.fit(documentDF)
    model_transformed = model_fitted.transform(documentDF)

    model.save('/home/pok/sem/project/models/model0mincount/model')
    model_fitted.save('/home/pok/sem/project/models/model0mincount/fitted')

    spark.stop()

def get_synonyms(word: str, count: int):
    spark = SparkSession \
        .builder \
        .appName("SimpleApplication") \
        .getOrCreate()

    model = Word2Vec.load('/home/pok/sem/project/models/model0mincount/model')
    model_fitted = Word2VecModel.load('/home/pok/sem/project/models/model0mincount/fitted')
    synonyms = model_fitted.findSynonyms(word, count)
    synonyms.select("word", fmt("similarity", 5).alias("similarity")).show()

    spark.stop()

    return synonyms


def connect_files():
    path = 'newsTexts/try/'
    write_file = open('newsTexts/allNewsRaw.txt', 'w')

    for i in range(1, 8):
        file = open(path + str(i) + '.txt', 'r')
        data = file.read()
        file.close()
        write_file.write(data)

    write_file.close()


def NamesSynonyms():
    spark = SparkSession \
        .builder \
        .appName("SimpleApplication") \
        .getOrCreate()

    data = read_data_for_mode('forPersonModel')

    text = []
    data_for_db = []

    for person in data:
        FIO = person[0].split(' ')
        unigram = FIO[0].capitalize() + '_' + FIO[1].capitalize()
        db_entity = {"name": person[0], "news": person[1], "unigram": unigram}
        data_for_db.append(db_entity)
        text += person[1]

    data = read_data_for_mode('forPlacesModel')

    for place in data:
        NAME = place[0].split(' ')
        unigram = '_'.join(NAME)
        db_entity = {"name": place[0], "news": place[1], "unigram": unigram}
        data_for_db.append(db_entity)
        text += place[1]

    def remove_punctuation(text):
        return re.sub(r'[^\w\s^-]', '', text)

    for i in range(len(text)):
        text[i] = remove_punctuation(text[i])

    def remove_stop_words(text: list):
        ru_stop = stopwords.words('russian')
        tokens = []
        for line in text:
            line_tokenized = line.split()
            for token in line_tokenized:
                if not token.lower() in ru_stop:
                    tokens.append(token)
        return tokens

    tokens = remove_stop_words(text)

    def get_only_words(tokens):
        return list(filter(lambda x: re.match('[а-яА-Я]+', x), tokens))

    tokens = get_only_words(tokens)

    full_text = ' '.join(tokens)

    documentDF = spark.createDataFrame([(full_text.split(" "),)], ["text"])

    model = Word2Vec(vectorSize=3, minCount=1, inputCol="text", outputCol="result")
    model_fitted = model.fit(documentDF)
    spark.stop()


    def synonym(model, word, count):
        try:
            synonyms = model.findSynonymsArray(word, count)
        except:
            print('Нет синонимов')
            synonyms = None
        return synonyms

    for i in range(0, len(data_for_db)):
        synonyms = synonym(model_fitted, data_for_db[i]['unigram'], 20)
        syn_list = []
        if synonyms is not None:
            for syn in synonyms:
                syn_list.append(syn[0])
        data_for_db[i]['synonyms'] = syn_list

    spark.stop()

    client = MongoClient(
        "mongodb+srv://pok:123@pisosteamcluster-sivo7.mongodb.net/NewsV102?retryWrites=true&w=majority")
    db = client.NewsV102  # Имя базы данных
    persons_news = db.NamesSynonyms  # Имя коллекции

    for entity in data_for_db:
        persons_news.insert_one(entity)


def __main__():
    print('Main entered')

    word = "Бочаров_Андрей"
    count_of_synonyms = 10
    get_synonyms(word, count_of_synonyms)




if __name__ == "__main__":
    __main__()
