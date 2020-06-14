import requests
from pymongo import MongoClient
from bs4 import BeautifulSoup
from multiprocessing import Pool
from datetime import datetime
from tqdm import trange
import sys

from pymongo import MongoClient

client = MongoClient("mongodb+srv://pok:123@pisosteamcluster-sivo7.mongodb.net/NewsV102?retryWrites=true&w=majority")

db = client.NewsV102
news = db.somesome

mainurl = 'https://v102.ru'
mainpage = requests.get(mainurl).text
ainsoup = BeautifulSoup(mainpage, 'html.parser')
lastarticle = ainsoup.find("a", {"class": "detail-link"}).get('href')
numarticle = ""
for char in lastarticle:
    if char.isdigit():
        numarticle += char

all_links = []

while int(numarticle) > 77908:
    all_links.append(mainurl + "/news/" + str(numarticle) + ".html")
    numarticle = int(numarticle) - 1


# ищем данные
def findcontent(url, soup):
    maincontent = soup.find("div", {"class": "main-top-new"})
    if maincontent != None:
        header = maincontent.find("h1", {"itemprop": "headline"}).text
        date = maincontent.find("span", {"class": "date-new"}).text
        comments = maincontent.find("span", {"class": "attr-comment"}).text
        texts = maincontent.find("div", {"class": "n-text"}).text
        # link = maincontent.find("div", {"class":"n-text"})
        new = {
            "header": header,
            "date": date,
            "countOfComments": comments,
            "text": texts,
            "linkOfNew": url
        }
        # print(url)
        news.insert_one(new)
    else:
        pass


def make_all(url):
    page = requests.get(url).text
    soup = BeautifulSoup(page, 'html.parser')
    findcontent(url, soup)


def main():
    start = datetime.now()

    n = len(all_links)
    listOfList = []

    count_of_thread = 10

    for i in range(0, count_of_thread):
        listOfList.append(all_links[int(i*n/count_of_thread):int((i+1)*n/count_of_thread)])

    for i in trange(count_of_thread, file=sys.stdout, desc='outer loop'):
        with Pool(count_of_thread) as p:
            p.map(make_all, listOfList[i])



    end = datetime.now()
    total = end - start
    print(total)


if __name__ == '__main__':
    main()
