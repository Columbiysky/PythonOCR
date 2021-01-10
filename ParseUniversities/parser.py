from bs4 import BeautifulSoup as bs
import requests
import os
import platform
import subprocess

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
    universitiesLinks = []
    private = False
    for link in universitiesPages:    
        page = requests.get(link)
        page.encoding = "windows-1251"
        soup = bs(page.text,"lxml")
        count = 0
        for table in soup.find_all('table', id = 'info'):
            private = False
            for td in table("td"):
                count = count + 1
                if(count == 6 and td.get_text() == 'Частные образовательные организации'):
                    private = True

                if(count == 8 and private == False):
                    universitiesLinks.append(td.get_text())
                    break

    return universitiesLinks

def PrintUniversitiesLinksInFile(universitiesLinks):
    f = open('unisNoPrivate.txt', 'w')
    for i in universitiesLinks:
        f.write(i + '\n')
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

def check(): pass


def main():
    # res = ping('asdfasdf.asdf')
    # print(res)
    if os.path.exists('test.txt'):
        f = open('test.txt','r')
        r = open('res.txt','w')
        for line in f:
            res = ping(line)
            if (res != 0):
                r.write(line + '\n')
        r.close()
        f.close()

    else:
        federalDistrictLinks = GetFederalDistrictsLinks()
        universitiesPages = GetUniversitiesPages(federalDistrictLinks)
        universitiesLinks = GetUniversitiesLinks(universitiesPages)
        PrintUniversitiesLinksInFile(universitiesLinks)

if __name__ == '__main__' :
    main()
