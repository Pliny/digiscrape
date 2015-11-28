from bs4 import BeautifulSoup as bsoup
import requests as rq
import re
import csv
import os
from digikey_orm import DigikeyOrm
from webview import WebView

output_dir = "./output"
results_csv = open('digikey-scrape-results.csv', 'w');

html_page = WebView('digikey-scrape-results.html')

def main():
    col_titles = "Navdy PN, Digikey Search String, Digikey PN, min price, min quantity, max price, max quantity, image URL, datasheet URLS".split(',')

    results_csv.write(",".join(col_titles) + "\n")

    with open('testdb.csv', 'rb') as f:
        reader = csv.reader(f)
        for row in reader:
            navdy_name = row[0]
            primary_source_from_digikey   = row[31].lower() == "digikey"
            secondary_source_from_digikey = row[34].lower() == 'digikey'

            if(primary_source_from_digikey):
                digikey_part_number = row[32]
                process_pn(navdy_name, digikey_part_number)

            if(secondary_source_from_digikey):
                digikey_part_number = row[35]
                process_pn(navdy_name, digikey_part_number)

    html_page.write()
    results_csv.close()


def process_pn(navdy_name, digikey_part_number):

    item = DigikeyOrm(digikey_part_number)

    print(navdy_name + ": FETCHING: " + item['search_url'])

    if(item.has_image_url()):
        get_file_from_url_maybe(item['image_url'])

    if(item.has_datasheet_urls()):
        for datasheet in item['datasheet_urls']:
            get_file_from_url_maybe(datasheet)

    contents = [ "\"" + navdy_name + "\"", 
                 "\"" +  item['search_url'] + "\"",
                 "\"" + digikey_part_number + "\"",
                 "\"" + item['pricing']['min']['price'] + "\"",
                 "\"" + item['pricing']['min']['unit'] + "\"",
                 "\"" + item['pricing']['max']['price'] + "\"",
                 "\"" + item['pricing']['max']['unit'] + "\"",
                 "\"" + item['image_url'] + "\"",
                 "\"" + "; ".join(item['datasheet_urls']) + "\"" ]
    results_csv.write(",".join(contents) + "\n")

    html_page.add_row(navdy_name, item)


def get_file_from_url_maybe(url):
    response = rq.get(url)
    filename = get_basename_from_url(url)
    file_path = output_dir + "/" + filename
    if(not os.path.isfile(file_path)):
        with open(file_path, 'wb') as f:
            f.write(response.content)

def get_basename_from_url(url):
    filename = url.split('?')[0]
    filename = re.sub("/$", "", filename)
    return os.path.basename(filename)

if __name__ == '__main__':
    main()
