from bs4 import BeautifulSoup as bs
import requests
import os
import platform
import subprocess
import urllib.request as downloader

base_url  = 'http://indicators.miccedu.ru/monitoring/2019/'


def GetFederalDistrictsLinks():
    url = 'http://indicators.miccedu.ru/monitoring/2019/index.php?m=vpo'
    page = requests.get(url)
    page.encoding = "windows-1251"
    #Parse page with list of federal districts
    soup  = bs(page.text, "lxml")
    #Parse all links to federal districts page
    federalDistrictsLinks = []
    for paragraph in soup.find_all('p', class_ = 'MsoListParagraph'):
        for a in paragraph("a"):
            federalDistrictsLinks.append(base_url + a.get('href'))

    return federalDistrictsLinks

def GetUniversitiesPages(federalDistrictLinks):
    uni_pages=[]

    for link in federalDistrictLinks:
        page = requests.get(link)
        page.encoding = "windows-1251"
        soup = bs(page.text, "lxml")
        for td in soup.find_all('td', class_ = 'inst'):
            for a in td("a"):
                uni_pages.append(base_url+'_vpo/' + a.get('href'))

    return uni_pages

def GetUniversitiesLinks(universitiesPages):
    universitiesLinks = {}
    private = False
    for link in universitiesPages:    
        page = requests.get(link)
        page.encoding = "windows-1251"
        soup = bs(page.text,"lxml")
        count = 0
        for table in soup.find_all('table', id = 'info'):
            private = False
            uni_branch = False
            name = ""
            for td in table("td"):                
                count = count + 1
                if(count == 2):
                    name = td.get_text()
                
                if(name.find('филиал') > -1 or name.find('Филиал') > -1):
                    uni_branch = True

                if(count == 6 and td.get_text() == 'Частные образовательные организации'):
                    private = True

                if(count == 8 and private == False and uni_branch == False):
                    link = td.get_text()
                    # Normalize links Example: uni-dubna.ru
                    if (link.find('https://') != -1):
                        link = link.replace('https://','')
                    if(link.find('http://') != -1):
                        link = link.replace('http://', '')
                    if(link.find('www.') != -1):
                        link = link.replace('www.','')
                    if(link.find('www ') > -1):
                        link = link.replace('www ','')
                    if(link.find('mtuci.ru') > -1):
                        link = 'mtuci.ru'
                    if(link.find('academy.andriaka.ru') > -1):
                        link = 'academy.andriaka.ru'
                    if(link.find('sgap.ru') > -1): # cuz .ru domen belong Arkhangelsk branch of CГЮА
                        link = 'сгюа.рф'
                    if(link.find('bigpi.biysk.ru/wwwsite') > -1):
                        link = 'bigpi.biysk.ru'
                    if(link.find('astracons.ru') > -1):
                        link = 'astracons.ru'                    
                    if(link.find('http:\\')> -1):
                        link = link.replace('http:\\','')
                    if(link.find('/') > -1):
                        link = link.replace('/', '')
                    universitiesLinks[name]=link
                    break

    return universitiesLinks

def PrintUniversitiesLinksInFile(universitiesLinks):
    f = open('unisLinks.txt', 'w', encoding='windows-1251')
    for k,v in universitiesLinks.items():
        f.write(v + '\n')
    f.close()

def ping(host):
    """
    Returns True if host (str) responds to a ping request.
    Remember that a host may not respond to a ping (ICMP) request even if the host name is valid.
    """

    # Option for the number of packets as a function of
    param = '-n' if platform.system().lower()=='windows' else '-c'

    # Building the command. Ex: "ping -c 1 google.com"
    #command = ['ping', param, '1', host]
    response = os.system("ping "+param+" 1 "+host)

    return response

def DownloadTest():
    link  = 'https://xn--d1aixi.xn--p1ai/sveden/document/%D0%9F%D1%80%20%E2%84%96%20403-%D0%A2%20%D0%BE%D1%82%2028.08.20.%20%D0%9E%20%D1%81%D1%82%D0%BE%D0%B8%D0%BC%D0%BE%D1%81%D1%82%D0%B8%201%20%D0%BA%D1%83%D1%80%D1%81%D0%B0%20%D0%92%D0%9E%20%D0%B8%20%D0%A1%D0%9F%D0%9E%20%D0%BE%D1%87%D0%BD%D0%BE%D0%B9%20%D1%84%D0%BE%D1%80%D0%BC%D1%8B%20%D0%BE%D0%B1%D1%83%D1%87%D0%B5%D0%BD%D0%B8%D1%8F.pdf'
    downloader.urlretrieve(link, './pizdec.pdf')


def main():
    # res = ping('asdfasdf.asdf')
    # print(res)

    if os.path.exists('test.txt'):
        f = open('test.txt','r')
        r = open('res.txt','w')
        for line in f:
            res = ping(line)
            if (res != 0):
                r.write(line)
        r.close()
        f.close()

    else:
        federalDistrictLinks = GetFederalDistrictsLinks()
        universitiesPages = GetUniversitiesPages(federalDistrictLinks)
        universitiesLinks = GetUniversitiesLinks(universitiesPages)
        PrintUniversitiesLinksInFile(universitiesLinks)
    # DownloadTest()

if __name__ == '__main__' :
    main()
