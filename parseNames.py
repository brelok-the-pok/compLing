def parse():
    from bs4 import BeautifulSoup
    import requests as req

    url = 'https://global-volgograd.ru/person/id/'

    names = []

    for i in range(1, 190):
        site_url = url + str(i)
        resp = req.get(site_url)
        soup = BeautifulSoup(resp.text, 'lxml')
        for tag in soup.find_all('h1'):
            tag_str = str(tag)
            FIO = tag_str.replace('<h1 class="full_name">', '').replace('</h1>', '').replace('<br/>', ' ')
            print(FIO)
            names.append(FIO)

    print(names)

    file = open('names.txt', 'w')

    for name in names:
        file.write(name + "\n")
    file.close()