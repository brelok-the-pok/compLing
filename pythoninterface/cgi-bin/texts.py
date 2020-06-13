#!/usr/bin/python

# Импорт модулей для обработки CGI
import cgi, cgitb 
from pymongo import MongoClient
from bson.objectid import ObjectId

client = MongoClient("mongodb+srv://pok:123@pisosteamcluster-sivo7.mongodb.net/NewsV102?retryWrites=true&w=majority")
db = client.NewsV102
news = db.NamesSynonyms
# Создание экземпляра FieldStorage 
form = cgi.FieldStorage() 

# Получение данных из полей
first_name = form.getvalue('name')
print("Content-type: text/html")
print()

text = news.find({'_id': ObjectId(first_name)})
for new in text:
    for i in new['news']:
        print('<p>{}</p>'.format(i))

