import requests as rq
import re
import csv
import os
import sys
from digikey_orm import DigikeyOrm
from webview import WebView
from csvview import CsvView

output_dir = "./output"

csv_page  = CsvView('digikey-scrape-results.csv')
html_page = WebView('digikey-scrape-results.html')

def main():

    if(len(sys.argv) != 2 or not sys.argv[1] or not os.path.isfile(sys.argv[1])):
        print("ERROR: Must provide an input csv file as argument. Exiting.")
        exit(1)

    with open(sys.argv[1], 'rb') as f:
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
    csv_page.close()


def process_pn(navdy_name, digikey_part_number):

    item = DigikeyOrm(digikey_part_number)

    print(navdy_name + ": FETCHING: " + item['search_url'])

    if(item.has_image_url()):
        download_file_from_url_maybe(item['image_url'])

    if(item.has_datasheet_urls()):
        for datasheet in item['datasheet_urls']:
            download_file_from_url_maybe(datasheet)

    csv_page.add_row(navdy_name, item)
    html_page.add_row(navdy_name, item)


def download_file_from_url_maybe(url):
    filename = get_basename_from_url(url)
    file_path = output_dir + "/" + filename
    if(not os.path.isfile(file_path)):
        response = rq.get(url)
        with open(file_path, 'wb') as f:
            f.write(response.content)

def get_basename_from_url(url):
    filename = url.split('?')[0]
    filename = re.sub("/$", "", filename)
    return os.path.basename(filename)

if __name__ == '__main__':
    main()
