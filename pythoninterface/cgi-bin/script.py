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

print('a{')

print('text-decoration: none; ')
print('color: white;')
print(' }')

print('.new{')
print('padding-top: 4px; ')
print('margin-bottom: 8px; ')
print('border-bottom: 1px solid; ')
print('text-align: center; ')
print('background-image: linear-gradient(145deg, #ee82ee, slateblue, #ffd86a, purple);')
print('color: white;')
print(' }')

print('</style>')

for new in listnames:
    name = new['name']
    listnews = new['news']
    ton = new['ton']
    idnew = new['_id']
    text1 = '<div class="new"><h3><a href="texts.py?name={}">{}</a></h3>'.format(idnew, name)
    text2 = '<p>{}</p></div>'.format(ton)
    print(text1+text2)



   
    
    
    
  
