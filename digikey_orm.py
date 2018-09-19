from bs4 import BeautifulSoup as bsoup
import requests as rq
import re

class DigikeyOrm:

    search_url = "http://search.digikey.com/scripts/DkSearch/dksus.dll?Detail&name="
    mfgpn_search_url = "https://www.digikey.com/products/en?keywords="

    def __init__(self, **h):
        self.pn = h['digikey_pn'] if 'digikey_pn' in h.keys() else None
        self.mfgpn = h['mfg_pn'] if 'mfg_pn' in h.keys() else None
        self.soup = None
        self.datasheets = None
        self.image = None
        self.pricing = None
        self.url = None

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
        if(self.url):
            url = self.url
        if(self.pn):
            url = self.search_url + self.pn
        elif(self.mfgpn):
            url = self.mfgpn_search_url + self.mfgpn
        else:
            raise ValueError("Must have either digikey p/n or mfg p/n to use this script")

        # print "DEBUG: " + url
        response = rq.get(url)
        self.soup = bsoup(response.text, 'html.parser')
        self.__page_found = (not re.search("404 \| DigiKey", self.soup.title.get_text()))

    def __get_search_url(self):
        return self.search_url + self.__get_digikey_pn()

    def __get_mfgpn_search_url(self):
        return self.mfgpn_search_url + self.__get_mfg_pn()

    def has_digikey_pn(self):
        return self.page_found() and self.__get_digikey_pn() != "N/A"

    def __get_mfg_pn(self):
        not self.soup and self.__populate()

        if(not self.mfgpn):
            self.mfgpn = "N/A"
            if(self.page_found()):
                product_overview_cell = self.soup.find(id='product-overview')
                if(product_overview_cell):
                    print "mfg pn cell: " + str(product_overview_cell.find_all('tr'))

        return self.mfgpn

    def __get_digikey_pn(self):
        not self.soup and self.__populate()

        if(not self.pn):
            self.pn = "N/A"
            if(self.page_found()):
                digikey_pn_cell = self.soup.find(id='reportPartNumber')
                if(digikey_pn_cell):
                    self.pn = digikey_pn_cell.text.strip()
                else:
                    product_table_cell = self.soup.find(id='productTable')
                    if(product_table_cell):
                        dk_pn_cell = product_table_cell.find_all(class_='tr-dkPartNumber')[0]
                        self.url = dk_pn_cell.a['href']
                        if(self.url[0] == '/'):
                            self.url = "https://www.digikey.com" + self.url
                        self.pn = dk_pn_cell.a.text.strip()
                    elif(self.soup.find(id='noResults')):
                        print "Cannot find DigiKey P/N"
        return self.pn

    def __get_pricing(self):
        not self.soup and self.__populate()

        if(not self.pricing):
            self.pricing = { 'min': {}, 'max': {} }
            if(self.page_found()):
                pricing_cell = self.soup.find(class_="product-dollars")
                if(pricing_cell):
                    pricing_cell = pricing_cell.find_all('tr')
                    self.pricing['min']['unit']  = pricing_cell[1].find_all('td')[0].get_text()
                    self.pricing['min']['price'] = pricing_cell[1].find_all('td')[1].get_text()
                    self.pricing['max']['unit']  = pricing_cell[-1].find_all('td')[0].get_text()
                    self.pricing['max']['price'] = pricing_cell[-1].find_all('td')[1].get_text()

            if(len(self.pricing['min'].keys()) == 0):
                self.pricing['min'] = { 'unit': "UNKNOWN", 'price': "UNKNOWN" }
                self.pricing['max'] = { 'unit': "UNKNOWN", 'price': "UNKNOWN" }

        return self.pricing

    def has_image_url(self):
        return self.page_found() and self.__get_image_url() != "N/A"

    def __get_image_url(self):
        not self.soup and self.__populate()

        if(not self.image):
            self.image = "N/A"
            if(self.page_found()):
                image_link = self.soup.find(class_='product-photo-wrapper').a
                if(image_link):
                    self.image = image_link['href']
                    if(self.image[0] == '/'):
                        self.image = 'https:' + self.image

        return self.image

    def has_datasheet_urls(self):
        return self.page_found() and self.__get_datasheet_urls()[0] != "N/A"

    def __get_datasheet_urls(self):
        not self.soup and self.__populate()

        if(not self.datasheets):
            self.datasheets = [ "N/A" ]
            ds_link_tags = self.soup.find_all(class_='lnkDatasheet')
            if(ds_link_tags):
                self.datasheets = map(lambda x: x['href'], ds_link_tags)
                for i in range(len(self.datasheets)):
                    if(self.datasheets[i][0] == '/'):
                        self.datasheets[i] = "https:" + self.datasheets[i]

        return self.datasheets

    def page_found(self):
        not self.soup and self.__populate()
        return self.__page_found
