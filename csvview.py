import csv

class CsvView:

    def __init__(self, filename):
        self.__results_csv = open(filename, 'w')
        col_titles = "Local PN, Quantity, Digikey PN,price (x1), price (x1000), supplier price (x1), supplier price (x1000), datasheet URLS, image URL, Digikey Search String, min quantity, max quantity".split(',')
        self.__results_csv.write(",".join(col_titles) + "\n")

    def close(self):
        self.__results_csv.close()

    def add_row(self, local_pn, item, quantity):
        supplier_max_price = float(item['pricing']['max']['price']) * int(quantity)
        supplier_min_price = float(item['pricing']['min']['price']) * int(quantity)
        contents = [ "\"" + local_pn + "\"",
                     "\"" + quantity + "\"",
                     "\"" + item['digikey_pn'] + "\"",
                     "\"" + item['pricing']['min']['price'] + "\"",
                     "\"" + item['pricing']['max']['price'] + "\"",
                     "\"" + str(supplier_min_price) + "\"",
                     "\"" + str(supplier_max_price) + "\"",
                     "\"" + "; ".join(item['datasheet_urls']) + "\"",
                     "\"" + item['pricing']['min']['unit'] + "\"",
                     "\"" + item['pricing']['max']['unit'] + "\"",
                     "\"" + item['image_url'] + "\"",
                     "\"" +  item['search_url'] + "\"" ]

        self.__results_csv.write(",".join(contents) + "\n")

