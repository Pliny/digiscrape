from bs4 import BeautifulSoup as bsoup
import requests as rq
import re

class DigikeyOrm:

    search_url = "http://search.digikey.com/scripts/DkSearch/dksus.dll?Detail&name="

    def __init__(self, digikey_pn):
        self.pn = digikey_pn
        self.soup = None
        self.datasheets = None
        self.image = None
        self.pricing = None

    def __getitem__(self, func):
        func_name = '_DigikeyOrm__get_'+str(func)
        if(func_name in dir(self)):
            return eval('self.' + func_name + '()')
        else:
            return None

    def __setitem__(self, key, value):
        func_name = '_DigikeyOrm__set_'+str(key)
        if(func_name in dir(self)):
            return eval('self.__set_'+str(key)+'(self, value)')
        else:
            return None

    def __populate(self):
        response = rq.get(self.search_url + self.pn)
        self.soup = bsoup(response.text, 'html.parser')
        self.__part_found = (not re.search("404 \| DigiKey", self.soup.title.get_text()))

    def __get_search_url(self):
        return self.search_url + self.pn

    def __get_digikey_pn(self):
        return self.pn

    def __get_pricing(self):
        not self.soup and self.__populate()

        if(not self.pricing):
            self.pricing = { 'min': {}, 'max': {} }
            if(self.part_found()):
                pricing_cell = self.soup.find(id="pricing").find_all('tr')
                self.pricing['min']['unit']  = pricing_cell[1].find_all('td')[0].get_text()
                self.pricing['min']['price'] = pricing_cell[1].find_all('td')[1].get_text()
                self.pricing['max']['unit']  = pricing_cell[-1].find_all('td')[0].get_text()
                self.pricing['max']['price'] = pricing_cell[-1].find_all('td')[1].get_text()
            else:
                self.pricing['min'] = { 'unit': "UNKNOWN", 'price': "UNKNOWN" }
                self.pricing['max'] = { 'unit': "UNKNOWN", 'price': "UNKNOWN" }

        return self.pricing

    def has_image_url(self):
        return self.part_found() and self.__get_image_url() != "N/A"

    def __get_image_url(self):
        not self.soup and self.__populate()

        if(not self.image):
            self.image = "N/A"
            if(self.part_found()):
                image_link = self.soup.find(class_='image-table').a
                if(image_link):
                    self.image = image_link['href']

        return self.image

    def has_datasheet_urls(self):
        return self.part_found() and self.__get_datasheet_urls() != "N/A"

    def __get_datasheet_urls(self):
        not self.soup and self.__populate()

        if(not self.datasheets):
            self.datasheets = "N/A"
            ds_link_tags = self.soup.find_all(class_='lnkDatasheet')
            if(ds_link_tags):
                self.datasheets = map(lambda x: x['href'], ds_link_tags)

        return self.datasheets

    def part_found(self):
        not self.soup and self.__populate()
        return self.__part_found
