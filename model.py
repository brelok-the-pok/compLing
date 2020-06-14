# from pyspark.sql import SparkSession
# from pyspark.ml.feature import Word2VecModel
# import os
#
# spark = SparkSession \
#     .builder \
#     .appName("SimpleApplication") \
#     .getOrCreate()
#
# path = os.getcwd()
# word2VecPath = path + '/word2vec'
# modelPath = path + "/word2vec-model"
#
# model = Word2VecModel.load(modelPath)
#
# model.getVectors().show()
#
# word = 'data'
# synonyms_count = 5
# print(model.findSynonymsArray(word, synonyms_count))
#
# spark.stop()
