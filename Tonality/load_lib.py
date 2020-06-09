import nltk

#Загрузка твитов
nltk.download('twitter_samples')
#Загрузка модели токенизации
nltk.download('punkt')
#Лексическая база английского языка
nltk.download('wordnet')
#Определение контекста en, ru
nltk.download('averaged_perceptron_tagger')
nltk.download('averaged_perceptron_tagger_ru')
#Стоп слова
nltk.download('stopwords')