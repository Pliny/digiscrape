from bs4 import BeautifulSoup as bsoup
import re
import os

class WebView:

    def __init__(self, filename):
        self.__filename = filename

        bootstrap_cdn_url = "https://maxcdn.bootstrapcdn.com/bootstrap/3.3.6/css/bootstrap.min.css"
        self.__index_html = ("<html><head><title>Navdy's DigiScrape</title>"
                            '<link rel="stylesheet" href="' + bootstrap_cdn_url + '">'
                            '</head><body><table class="table table-hover">'
                            '<thead></thead><tbody></tbody></table></body></html>')
        self.__outsoup = bsoup(self.__index_html, 'html.parser')

        header_row = self.__outsoup.new_tag("tr")

        titles = [ "Navdy PN", "Digikey PN", "Pricing",
                   "Image", "datasheet URLS" ]
        for idx,title in enumerate(titles):
            col = self.__outsoup.new_tag("th")
            col.string = title
            header_row.append(col)
        self.__outsoup.html.body.table.thead.append(header_row)

    def write(self):
        with open(self.__filename, "w") as f:
            f.write(self.__outsoup.prettify())

    def add_row(self, navdy_pn, item):
        row = self.__outsoup.new_tag("tr")

        # Navdy PN
        col = self.__outsoup.new_tag("td")
        col.string = navdy_pn
        row.append(col)

        # Digikey PN
        col = self.__outsoup.new_tag("td")
        search_link = self.__outsoup.new_tag("a", href=item['search_url'], target="_blank")
        search_link.string = item['digikey_pn']
        col.append(search_link)
        row.append(col)

        # Pricing information
        col = self.__outsoup.new_tag("td")
        table = ("<table class=\"table table-hover\"border=\"1\"><tbody><tr><th>Price Break</th>"
                "<th>Unit Price</th></tr></tbody></table>")
        table = bsoup(table, 'html.parser')

        table.tbody.append(self.__row_for(item['pricing']['min']))
        table.tbody.append(self.__row_for(item['pricing']['max']))
        col.append(table)
        row.append(col)

        # Image
        col = self.__outsoup.new_tag("td")
        if(item.has_image_url()):
            img_title = self.__outsoup.new_tag("div")
            img_title.string = "NAME: " + self.__get_basename_from_url(item['image_url'])
            col.append(img_title)
            img_div = self.__outsoup.new_tag("div")
            img_link = self.__outsoup.new_tag("a", href=item['image_url'], target="_blank")
            img_tag = self.__outsoup.new_tag("img", border="0", width="100", src=item['image_url'])
            img_link.append(img_tag)
            img_div.append(img_link)
            col.append(img_div)
        else:
            col.string = "N/A"
        row.append(col)

        # Datasheets
        col = self.__outsoup.new_tag("td")
        if(item.has_datasheet_urls()):
            for url in item['datasheet_urls']:
                link = self.__outsoup.new_tag("a", href=url, target="_blank")
                link.string = self.__get_basename_from_url(url)
                col.append(link)
        else:
            col.string = "N/A"
        row.append(col)

        self.__outsoup.find(class_="table").append(row)

    def __get_basename_from_url(self, url):
        filename = url.split('?')[0]
        filename = re.sub("/$", "", filename)
        return os.path.basename(filename)

    def __row_for(self, price_unit_dict):
        ptr = self.__outsoup.new_tag("tr")

        ptd = self.__outsoup.new_tag("td", **{'class':'text-center'})
        ptd.string = price_unit_dict['unit']
        ptr.append(ptd)

        ptd = self.__outsoup.new_tag("td")
        ptd.string = price_unit_dict['price']
        ptr.append(ptd)

        return ptr

