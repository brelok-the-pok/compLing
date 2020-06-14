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

print('<style type="text/css">')

print('.new{')
print('margin: 10px;')
print('background-color: #f0f4f7;')
print('border-radius: 8px;')
print('padding: 8px;')
print('}')



print('.Negative{')
print('border: 4px solid red;')
print('}')

print('.Positive{')
print('border: 4px solid green;')
print('}')

print('</style>')

text = news.find({'_id': ObjectId(first_name)})
for new in text:
    for i in range(0, len(new['news'])):

        print('<div class="new {}"><p>{}. {} </p></div>'.format(new['textton'][i], i+1, new['news'][i]))

