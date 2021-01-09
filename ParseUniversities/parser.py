from bs4 import BeautifulSoup as bs
import requests

base_url  = 'http://indicators.miccedu.ru/monitoring/2019/'


class ParseFederalDistricts():
    '''This class parses links to federal districts pages, which contains links to universities pages in district.'''
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
    
    def GetUniversitiesLinks():
        uni_pages=[]

        for link in federalDistrictLinks:
            page = requests.get(link)
            page.encoding = "windows-1251"
            soup = bs(page.text, "lxml")
            for td in soup.find_all('td', class_ = 'inst'):
                for a in td("a"):
                    uni_pages.append(base_url+'_vpo/' + a.get('href'))

        return uni_pages


if __name__ == '__main__' :
    federalDistrictLinks = ParseFederalDistricts.GetFederalDistrictsLinks()
    universitiesPages = ParseFederalDistricts.GetUniversitiesLinks()
    
    universityLinks = []

    for link in universitiesPages:    
        page = requests.get(link)
        page.encoding = "windows-1251"
        soup = bs(page.text,"lxml")
        count = 0
        for table in soup.find_all('table', id = 'info'):
            for td in table("td"):
                count = count + 1
                if(count == 8):
                   universityLinks.append(td.get_text())

    print(len(universityLinks))
    f = open('unis.txt', 'w')
    for i in universityLinks:
        f.write(i + '\n')
        