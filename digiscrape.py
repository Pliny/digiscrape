from bs4 import BeautifulSoup as bsoup
import requests as rq
import re
import csv
import os
from digikey_orm import DigikeyOrm

output_dir = "./output"
results_csv = open('digikey-scrape-results.csv', 'w');

index_html = "<html><head><title>Navdy's DigiScrape</title>"
index_html += '<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.6/css/bootstrap.min.css">'
index_html += '</head><body><table class="table table-hover"><thead></thead><tbody></tbody></table></body></html>'
outsoup = bsoup(index_html, 'html.parser')


def main():
    col_titles = "Navdy PN, Digikey Search String, Digikey PN, min price, min quantity, max price, max quantity, image URL, datasheet URLS".split(',')
    results_csv.write(",".join(col_titles) + "\n")

    header_row = outsoup.new_tag("tr")
    for idx,title in enumerate(col_titles):
        if(idx != 1):
            col = outsoup.new_tag("th")
            col.string = title
            header_row.append(col)
    outsoup.html.body.table.thead.append(header_row)

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

    with open("digikey-scrape-results.html", "w") as html:
        html.write(outsoup.prettify())
    results_csv.close()


def process_pn(navdy_name, digikey_part_number):
    print(navdy_name + ": FETCHING: " + digikey_part_number)

    item = DigikeyOrm(digikey_part_number)

    if(item.part_found()):

        if(item.has_image_url()):
            get_file_from_url_maybe(item['image_url'])

        if(item.has_datasheets()):
            for datasheet in item['datasheets']:
                get_file_from_url_maybe(datasheet)

        contents = [ "\"" + navdy_name + "\"", 
                     "\"" +  item['search_url'] + "\"",
                     "\"" + digikey_part_number + "\"",
                     "\"" + item['pricing']['min']['price'] + "\"",
                     "\"" + item['pricing']['min']['unit'] + "\"",
                     "\"" + item['pricing']['max']['price'] + "\"",
                     "\"" + item['pricing']['max']['unit'] + "\"",
                     "\"" + item['image_url'] + "\"",
                     "\"" + "; ".join(item['datasheets']) + "\"" ]
        results_csv.write(",".join(contents))

        row = outsoup.new_tag("tr")
        for idx,ele in enumerate(contents):
            ele = ele[1:-1]
            if(idx == 1):
                part_search_url = ele
                continue

            col = outsoup.new_tag("td")
            if(idx == 2):
                search_link = outsoup.new_tag("a", href=part_search_url, target="_blank")
                search_link.string = ele
                col.append(search_link)
            elif(idx == 7 and ele != "N/A"):
                img_title = outsoup.new_tag("div")
                img_title.string = "NAME: " + get_basename_from_url(ele)
                col.append(img_title)
                img_link = outsoup.new_tag("a", href=ele, target="_blank")
                img_tag = outsoup.new_tag("img", border="0", width="100", src=ele)
                img_link.append(img_tag)
                col.append(img_link)
            elif(idx == 8 and ele != "N/A"):
                urls = ele.split(';')
                for url in urls:
                    link = outsoup.new_tag("a", href=url, target="_blank")
                    link.string = get_basename_from_url(url)
                    col.append(link)
            else:
                col.string = ele
            row.append(col)
        outsoup.find(class_="table").append(row)

    else:
        contents = [ "\"" + navdy_name + "\"",
                     "\"" +  item['search_url'] + "\"",
                     "\"" + digikey_part_number + "\"",
                     "UNKNOWN", "UNKNOWN",
                     "UNKNOWN", "UNKNOWN",
                     "UNKNOWN", "UNKNOWN" ]
        results_csv.write(','.join(contents) + "\n")

        row = outsoup.new_tag("tr")
        for idx,ele in enumerate(contents):
            if(idx == 1):
                part_search_url = ele[1:-1]
                continue

            col = outsoup.new_tag("td")
            if(idx == 2):
                search_link = outsoup.new_tag("a", href=part_search_url, target="_blank")
                search_link.string = ele[1:-1]
                col.append(search_link)
            else:
                col.string = ele
            row.append(col)
        outsoup.find(class_="table").append(row)

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
