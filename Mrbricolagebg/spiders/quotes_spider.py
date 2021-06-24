import scrapy
from scrapy import Request
import json


class MrbricolageSpider(scrapy.Spider):
    name = "Mrbricolagebg"

    start_urls = ['https://mr-bricolage.bg/instrumenti/veloaksesoari/c/006014']

    product = {}

    def parse(self, response):
        products_links = response.css('a.name::attr(href)')
        yield from response.follow_all(products_links, self.parse_product)
        all_pages = response.css('li.pagination-next a')
        yield from response.follow_all(all_pages, self.parse)

    def get_and_strip(self, path, response):
        return response.css(path).get().strip()

    def parse_product(self, response):
        def spec_table_attributes_extract():

            [self.product.update({'brand': key['value']}) for key in specs_table if "Марка" in key['key']]

            [self.product.update({'model': key['value']}) for key in specs_table if "Модел" in key['key']]

            [self.product.update({'origin': key['value']}) for key in specs_table if "Произход" in key['key']]

            [self.product.update({'warranty': key['value']}) for key in specs_table if "Гаранция" in key['key']]

        request_url = ""
        self.product.update({'title': self.get_and_strip('h1.js-product-name::text', response)})

        raw_price = self.get_and_strip('p.price.js-product-price::text', response)
        if raw_price:
            price = raw_price.replace(',', '.')
            self.product.update({'price': price})

        availability = self.get_and_strip('div.col-md-12.bricolage-availability::text', response)
        if availability:
            self.product.update({'availability': availability})

        article_text = self.get_and_strip('div.col-md-12.bricolage-code::text', response)
        if article_text:
            article_id = article_text.replace('Код Bricolage: ', '')
            self.product.update({'article_id': article_id})

            request_url = f"https://mr-bricolage.bg/store-pickup/{article_id}/pointOfServices"

        ean = response.css('div[id="home"] span::text').re('[^\s]+')[0]
        if ean:
            self.product.update({'ean': ean})

        self.product.update({'url': response.url})

        images = response.css('div.owl-thumb-item img::attr(src)').getall()
        if images:
            self.product.update({'images': images})

        specs_table = [{'key': row.css('td:nth-child(1)::text').get().strip(),
                        'value': row.css('td:nth-child(2)::text').get().strip()} for row
                       in response.css('table.table tr')]

        spec_table_attributes_extract()

        self.product.update({"specs_table": specs_table})

        headers = {
            "Connection": "keep-alive",
            "sec-ch-ua": "\" Not;A Brand\";v=\"99\", \"Google Chrome\";v=\"91\", \"Chromium\";v=\"91\"",
            "Accept": "*/*",
            "X-Requested-With": "XMLHttpRequest",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Origin": "https://mr-bricolage.bg",
            "Sec-Fetch-Dest": "empty",
            "Referer": response.url,
            "Accept-Language": "bg-BG,bg;q=0.9,en;q=0.8"
        }

        cookies = {
            "bricolage-customerLocation": "\"|42.6641056,23.3233149\"",
            "__utmz": "149670890.1624529510.9.3.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=(not%20provided)",
            "JSESSIONID": response.headers.getlist('Set-Cookie')[0].decode("utf-8").split(";")[0].split("=")[1],
        }

        token = response.css('[name="CSRFToken"]::attr(value)').get()

        body = f'locationQuery=&cartPage=false&entryNumber=0&latitude=42.6641056&longitude=23.3233149&CSRFToken={token}'

        yield Request(
            url=request_url,
            method='POST',
            dont_filter=True,
            cookies=cookies,
            headers=headers,
            callback=self.parse_availability_info,
            body=body
        )

    def parse_availability_info(self, response):
        r = json.loads(response.text)
        store_availability = [{"store": key['displayName'], "Availability": key['stockPickup']} for key in r['data']]
        self.product.update({"Availability": store_availability})
        yield self.product


class MrbricolageAvailabilitySpider(scrapy.Spider):
    name = "Availability"

    product = {}

    start_urls = ['https://mr-bricolage.bg/instrumenti/veloaksesoari/c/006014']

    def parse(self, response):
        products_links = response.css('a.name::attr(href)')
        yield from response.follow_all(products_links, self.parse_product)
        all_pages = response.css('li.pagination-next a')
        yield from response.follow_all(all_pages, self.parse)


    def parse_product(self, response):
        article_text = self.get_and_strip('div.col-md-12.bricolage-code::text', response)
        if article_text:
            article_id = article_text.replace('Код Bricolage: ', '')
            request_url = f"https://mr-bricolage.bg/store-pickup/{article_id}/pointOfServices"
            self.product.update({'URL': request_url})
        headers = {
            "Connection": "keep-alive",
            "sec-ch-ua": "\" Not;A Brand\";v=\"99\", \"Google Chrome\";v=\"91\", \"Chromium\";v=\"91\"",
            "Accept": "*/*",
            "X-Requested-With": "XMLHttpRequest",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Origin": "https://mr-bricolage.bg",
            "Sec-Fetch-Dest": "empty",
            "Referer": response.url,
            "Accept-Language": "bg-BG,bg;q=0.9,en;q=0.8"
        }

        cookies = {
            "bricolage-customerLocation": "\"|42.6641056,23.3233149\"",
            "__utmz": "149670890.1624529510.9.3.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=(not%20provided)",
            "JSESSIONID": response.headers.getlist('Set-Cookie')[0].decode("utf-8").split(";")[0].split("=")[1],
        }
        token = response.css('[name="CSRFToken"]::attr(value)').get()

        body = f'locationQuery=&cartPage=false&entryNumber=0&latitude=42.6641056&longitude=23.3233149&CSRFToken={token}'

        yield Request(
            url=request_url,
            method='POST',
            dont_filter=True,
            cookies=cookies,
            headers=headers,
            callback=self.parse_availability_info,
            body=body
        )

    def get_and_strip(self, path, response):
        return response.css(path).get().strip()

    def parse_availability_info(self, response):
        r =json.loads(response.text)
        store_availability =[{"store": key['displayName'],"Availability": key['stockPickup']} for key in r['data']]
        self.product.update({"Availability": store_availability})
        yield self.product
