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
        headerrow = True
        for row in reader:
            if(headerrow):
                headerrow = False
                continue

            local_pn = row[0]
            supplier_from_digikey   = row[5].lower() == "digi-key"

            if(supplier_from_digikey):
                dk_pn = row[6]
            else:
                mfg_pn = row[3]
                if(mfg_pn):
                    dk_pn = find_digikey_pn(local_pn, mfg_pn)
                supplier_from_digikey = dk_pn and len(dk_pn) > 0

            if(supplier_from_digikey):
                digikey_part_number = dk_pn
                process_pn(local_pn, digikey_part_number, row[4])

    html_page.write()
    csv_page.close()


def process_pn(local_pn, digikey_part_number, quantity):

    item = DigikeyOrm(digikey_pn = digikey_part_number)

    print("%-32s: FETCHING: %s" % (local_pn, item['search_url']))

    if(item.has_image_url()):
        download_file_from_url_maybe(item['image_url'])

    if(item.has_datasheet_urls()):
        for datasheet in item['datasheet_urls']:
            download_file_from_url_maybe(datasheet)

    csv_page.add_row(local_pn, item, quantity)
    html_page.add_row(local_pn, item)

def find_digikey_pn(local_pn, mfg_part_number):
    item = DigikeyOrm(mfg_pn = mfg_part_number)

    print("%-32s: FETCHING: %s" % (local_pn, item['mfgpn_search_url']))

    if(item.has_digikey_pn()):
        return item['digikey_pn']



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
