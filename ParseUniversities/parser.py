from bs4 import BeautifulSoup as bs
import requests

url = 'http://indicators.miccedu.ru/monitoring/2019/index.php?m=vpo'
page = requests.get(url)
page.encoding = "windows-1251"
soup  = bs(page.text, "lxml")

Federal_districts = soup.findAll('p', class_ = 'MsoListParagraph')
Federal_districts_links = []
for dist_ in Federal_districts:
    d = bs(dist_, "lxml")
    print(d.findAll('href'))
#print(Federal_districts)