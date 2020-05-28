from pyspark.sql import SparkSession
from pyspark.ml.feature import Tokenizer
from pyspark.ml.feature import StopWordsRemover
from pyspark.ml.feature import CountVectorizer
from pyspark.ml.feature import IDF
from pyspark.sql.functions import format_number as fmt
from pyspark.ml.feature import Word2Vec, Word2VecModel
from lxml import etree
import re
import string
import os


def get_patent_name(patent_data):
    root = etree.fromstring(patent_data.encode('utf-8'))
    doc_numbers = root.findall(".//doc-number")
    countries = root.findall(".//country")
    patent_name = countries[0].text + doc_numbers[0].text
    return patent_name


def get_claims(patent_data):
    root = etree.fromstring(patent_data.encode('utf-8'))
    claims = root.findall(".//claim")
    if claims:
        claims_without_tags = [''.join(claim.itertext()) for claim in claims]
        return ''.join(claims_without_tags)
    return ''


def remove_punctuation(text):
    return text.translate(str.maketrans('', '', string.punctuation))


def remove_linebreaks(text):
    return text.strip()


def get_only_words(tokens):
    return list(filter(lambda x: re.match('[a-zA-Z]+', x), tokens))


def parseXML(path, start_index):
    file = open(path, 'r')
    i = start_index

    new_file = open(path + '/xml/' + str(-2) + '.xml', 'w')

    for line in file:
        if line == '<?xml version="1.0" encoding="UTF-8"?>\n':
            new_file.close()
            i += 1
            new_file = open(path + '/xml/' + str(i) + '.xml', 'w')
            new_file.write(line)
        else:
            new_file.write(line)

    print(path)


spark = SparkSession \
    .builder \
    .appName("SimpleApplication") \
    .getOrCreate()


path = os.getcwd()
word2VecPath = path + '/word2vec'
modelPath = path + "/word2vec-model"


input_file = spark.sparkContext.wholeTextFiles(path + '/xml/*.xml')


prepared_data = input_file.map(lambda x: (get_patent_name(x[1]), get_claims(x[1]))) \
    .map(lambda x: (x[0], remove_punctuation(x[1]))) \
    .map(lambda x: (x[0], remove_linebreaks(x[1])))

#print(prepared_data.take(10))

prepared_df = prepared_data.toDF().selectExpr('_1 as patent_name', '_2 as patent_claims')

# Разбить claims на токены
tokenizer = Tokenizer(inputCol="patent_claims", outputCol="words")
words_data = tokenizer.transform(prepared_df)

# Отфильтровать токены, оставив только слова
filtered_words_data = words_data.rdd.map(lambda x: (x[0], x[1],
get_only_words(x[2])))
filtered_df = filtered_words_data.toDF().selectExpr('_1 as patent_name', '_2 as patent_claims', '_3 as words')

# Удалить стоп-слова (союзы, предлоги, местоимения и т.д.)
remover = StopWordsRemover(inputCol='words', outputCol='filtered')
filtered = remover.transform(filtered_df)
vectorizer = CountVectorizer(inputCol='filtered', outputCol='raw_features').fit(filtered)
featurized_data = vectorizer.transform(filtered)
featurized_data.cache()
idf = IDF(inputCol='raw_features', outputCol='features')
idf_model = idf.fit(featurized_data)
rescaled_data = idf_model.transform(featurized_data)

# Вывести таблицу rescaled_data
rescaled_data.show()


word2Vec = Word2Vec(inputCol='filtered', outputCol='some_col')
model = word2Vec.fit(filtered)

#Сохраним модель
#word2Vec.save(word2VecPath)
#model.save(modelPath)

model.getVectors().show()
print(model.findSynonymsArray("house", 5))

spark.stop()
