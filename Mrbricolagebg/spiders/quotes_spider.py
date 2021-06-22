import scrapy
from scrapy import Request
import json


class MrbricolageSpider(scrapy.Spider):
    name = "Mrbricolagebg"

    start_urls = ['https://mr-bricolage.bg/instrumenti/veloaksesoari/c/006014']

    def parse(self, response):
        products_links = response.css('a.name::attr(href)')
        yield from response.follow_all(products_links, self.parse_product)
        all_pages = response.css('li.pagination-next a')
        yield from response.follow_all(all_pages, self.parse)

    def parse_product(self, response):
        def get_and_strip(path):
            return response.css(path).get().strip()

        def parse_availability_info():
            pass
        def store_availability_request(response):
            headers = {
                "Connection": "keep-alive",
                "sec-ch-ua": "\" Not;A Brand\";v=\"99\", \"Google Chrome\";v=\"91\", \"Chromium\";v=\"91\"",
                "Accept": "*/*",
                "X-Requested-With": "XMLHttpRequest",
                "sec-ch-ua-mobile": "?0",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.106 Safari/537.36",
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "Origin": "https://mr-bricolage.bg",
                "Sec-Fetch-Site": "same-origin",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Dest": "empty",
                "Referer": response.url,
                "Accept-Language": "bg-BG,bg;q=0.9"
            }

            cookies = {
                "JSESSIONID": response.headers.getlist('Set-Cookie')[0].decode("utf-8").split(";")[0].split("=")[1],
                "bricolage-customerLocation": "\"|42.6641056,23.3233149\"",
                "ROUTEID": "B8834011C5DFE8855B11150F71AF01DF",
                "__utma": "149670890.1557527530.1624294132.1624294132.1624294132.1",
                "__utmc": "149670890",
                "__utmz": "149670890.1624294132.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none)",
                "__utmt": "1",
                "__utmb": "149670890.1.10.1624294132",
                "_fbp": "fb.1.1624294131731.59759582",
                "_ym_uid": "1624294132506831981",
                "_ym_d": "1624294132",
                "_ga_2E6XGN78KC": "GS1.1.1624294131.1.0.1624294131.0",
                "_ga": "GA1.1.493738342.1624294132",
                "_gcl_au": "1.1.214298219.1624294132",
                "_ym_visorc": "w",
                "cb-enabled": "enabled",
                "_ym_isad": "2",
                "__utmb": "149670890.3.10.1624294132",
                "_ga_2E6XGN78KC": "GS1.1.1624294131.1.1.1624294899.0"
            }

            body = 'locationQuery=&cartPage=false&entryNumber=0&latitude=42.6641056&longitude=23.3233149&CSRFToken=5bed69e0-9f36-4c5b-a5c3-88bc8f1da949'
            Request(
                url=url,
                method='POST',
                dont_filter=True,
                cookies=cookies,
                headers=headers,
                callback=parse_availability_info(),
                body=body
            )

        def spec_table_attributes_extract():

            [product.update({'brand': key['value']}) for key in specs_table if "Марка" in key['key']]

            [product.update({'model': key['value']}) for key in specs_table if "Модел" in key['key']]

            [product.update({'origin': key['value']}) for key in specs_table if "Произход" in key['key']]

            [product.update({'warranty': key['value']}) for key in specs_table if "Гаранция" in key['key']]

        product = {}
        url = ""
        product.update({'title': get_and_strip('h1.js-product-name::text')})

        raw_price = get_and_strip('p.price.js-product-price::text')
        if raw_price:
            price = raw_price.replace(',', '.')
            product.update({'price': price})

        availability = get_and_strip('div.col-md-12.bricolage-availability::text')
        if availability:
            product.update({'availability': availability})

        article_text = get_and_strip('div.col-md-12.bricolage-code::text')
        if article_text:
            article_id = article_text.replace('Код Bricolage: ', '')
            product.update({'article_id': article_id})
            url = f"https://mr-bricolage.bg/store-pickup/{article_id}/pointOfServices"

        ean = response.css('div[id="home"] span::text').re('[^\s]+')[0]
        if ean:
            product.update({'ean': ean})

        product.update({'url': response.url})

        images = response.css('div.owl-thumb-item img::attr(src)').getall()
        if images:
            product.update({'images': images})

        specs_table = [{'key': row.css('td:nth-child(1)::text').get().strip(),
                        'value': row.css('td:nth-child(2)::text').get().strip()} for row
                       in response.css('table.table tr')]

        spec_table_attributes_extract()
        store_availability_request(response)
        product.update({"specs_table": specs_table})

        yield product




