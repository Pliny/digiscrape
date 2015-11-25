from bs4 import BeautifulSoup as bsoup
import requests as rq
import re
import csv
import os

search_url = "http://search.digikey.com/scripts/DkSearch/dksus.dll?Detail&name="
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

        contents = [ "\"" + navdy_name + "\"", 
                     "\"" +  search_url + digikey_part_number + "\"",
                     "\"" + digikey_part_number + "\"",
                     "\"" + pricing['min']['price'] + "\"",
                     "\"" + pricing['min']['unit'] + "\"",
                     "\"" + pricing['max']['price'] + "\"",
                     "\"" + pricing['max']['unit'] + "\"",
                     "\"" + image_url + "\"",
                     "\"" + "; ".join(datasheet_urls) + "\"" ]
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
                     "\"" +  search_url + digikey_part_number + "\"",
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

def get_basename_from_url(url):
    filename = url.split('?')[0]
    filename = re.sub("/$", "", filename)
    return os.path.basename(filename)

if __name__ == '__main__':
    main()
