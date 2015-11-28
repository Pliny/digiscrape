import csv

class CsvView:

    def __init__(self, filename):
        self.__results_csv = open(filename, 'w')
        col_titles = "Navdy PN, Digikey Search String, Digikey PN, min price, min quantity, max price, max quantity, image URL, datasheet URLS".split(',')
        self.__results_csv.write(",".join(col_titles) + "\n")

    def close(self):
        self.__results_csv.close()

    def add_row(self, navdy_pn, item):
        contents = [ "\"" + navdy_pn + "\"", 
                     "\"" +  item['search_url'] + "\"",
                     "\"" + item['digikey_pn'] + "\"",
                     "\"" + item['pricing']['min']['price'] + "\"",
                     "\"" + item['pricing']['min']['unit'] + "\"",
                     "\"" + item['pricing']['max']['price'] + "\"",
                     "\"" + item['pricing']['max']['unit'] + "\"",
                     "\"" + item['image_url'] + "\"",
                     "\"" + "; ".join(item['datasheet_urls']) + "\"" ]

        self.__results_csv.write(",".join(contents) + "\n")

