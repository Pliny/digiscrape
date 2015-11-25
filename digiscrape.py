from bs4 import BeautifulSoup as bsoup
import requests as rq
import re
import csv
import os

search_url = "http://search.digikey.com/scripts/DkSearch/dksus.dll?Detail&name="
output_dir = "./output"
results_csv = open('results.csv', 'w');

def main():
    results_csv.write("Digikey Search String, Navdy PN, Digikey PN, min price, min quantity, max price, max quantity, image URL, datasheet URLS\n")

    with open('Entire_Database151124.csv', 'rb') as f:
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

    results_csv.close()


def process_pn(navdy_name, digikey_part_number):
    print(navdy_name + ": FETCHING: " + search_url + digikey_part_number)
    response = rq.get(search_url + digikey_part_number)
    soup = bsoup(response.text, 'html.parser')

    if(not re.search("404 \| DigiKey", soup.title.get_text())):
        # PRICE
        pricing = get_pricing(soup)

        # IMAGE
        image_url = get_image(soup)
        if(image_url):
            get_file_from_url_maybe(image_url)
        else:
            image_url = "N/A"

        # DATASHEETS
        datasheet_urls = get_datasheet(soup)
        if(datasheet_urls):
            for datasheet_url in datasheet_urls:
                get_file_from_url_maybe(datasheet_url)
        else:
            datasheet_url = "N/A"

        results_csv.write(search_url + digikey_part_number + "," + navdy_name + "," + digikey_part_number + "," +
                pricing['min']['price'] + "," + pricing['min']['unit'] + "," +
                pricing['max']['price'] + "," + pricing['max']['unit'] + "," +
                image_url + ",\"" + "; ".join(datasheet_urls) + "\"\n")
    else:
        results_csv.write(search_url + digikey_part_number + "," + navdy_name + "," + digikey_part_number + "," +
                "UNKNOWN" + "," + "UNKNOWN" + "," +
                "UNKNOWN" + "," + "UNKNOWN" + "," +
                "UNKNOWN" + "," + "UNKNOWN" + "\n")

def get_file_from_url_maybe(url):
    response = rq.get(url)
    filename = url.split('?')[0]
    filename = re.sub("/$", "", filename)
    filename = os.path.basename(filename)
    file_path = output_dir + "/" + filename
    if(not os.path.isfile(file_path)):
        with open(file_path, 'wb') as f:
            f.write(response.content)


def get_pricing(soup):
    ret_val = { 'min': {}, 'max': {} }
    pricing_cell = soup.find(id="pricing").find_all('tr')
    ret_val['min']['unit']  = pricing_cell[1].find_all('td')[0].get_text()
    ret_val['min']['price'] = pricing_cell[1].find_all('td')[1].get_text()
    ret_val['max']['unit']  = pricing_cell[-1].find_all('td')[0].get_text()
    ret_val['max']['price'] = pricing_cell[-1].find_all('td')[1].get_text()
    return ret_val

def get_image(soup):
    image_link_tag = soup.find(class_='image-table').a
    return image_link_tag and  image_link_tag['href']

def get_datasheet(soup):
    ds_link_tags = soup.find_all(class_='lnkDatasheet')
    return ds_link_tags and map(lambda x: x['href'], ds_link_tags)

if __name__ == '__main__':
    main()
