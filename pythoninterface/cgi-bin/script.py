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

print('h3 a{')
print('color:black;')
print('text-decoration: none; ')
print('transition:.2s;')
print(' }')

print('h3 a:hover{')
print('color: rgb(32, 55, 160);')
print(' }')

print('.new{')
print('padding-top: 4px; ')
print('border-radius: 16px;')
print('border: 2px solid black;')
print('margin-bottom: 8px; ')
print('border-bottom: 1px solid; ')
print('text-align: center; ')
print('background-image: radial-gradient(#f0f0f0, #d8d8d8);')

print('font-size: 120%;')
print('transition:.2s;')
print(' }')

print('.new:hover{')
print('box-shadow: 2px -2px 15px 0px #464646; }')
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



   
    
    
    
  
