#!/usr/bin/env python3
from pymongo import MongoClient
from bson.objectid import ObjectId
client = MongoClient("mongodb+srv://pok:123@pisosteamcluster-sivo7.mongodb.net/NewsV102?retryWrites=true&w=majority")
db = client.NewsV102
news = db.NamesSynonyms
listnames = news.find()

print("Content-type: text/html")
print()
print('<style type="text/css">')
print('.new{')
print('overflow: auto; ')
print('max-height: 100px; ')
print('font-family: Verdana, Arial, Helvetica, sans-serif; ')
print('color: #333366;')
print(' }')
print('</style>')

for new in listnames:
    name = new['name']
    listnews = new['news']
    idnew = new['_id']
    text1 = '<h3><a href="texts.py?name={}">{}</a></h3>'.format(idnew, name)

    print(text1)



   
    
    
    
  
