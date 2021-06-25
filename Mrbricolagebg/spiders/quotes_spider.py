import scrapy
from scrapy import Request
from itemloaders import ItemLoader
from itemloaders.processors import TakeFirst, MapCompose, Join
import json


class Product(scrapy.Item):
    title = scrapy.Field()
    price = scrapy.Field()
    availability = scrapy.Field()
    article_id = scrapy.Field()
    ean = scrapy.Field()
    url = scrapy.Field()
    images = scrapy.Field()
    specs_table = scrapy.Field()
    store_availability = scrapy.Field()


class ProductLoader(ItemLoader):
    default_output_processor = TakeFirst()

    name_in = MapCompose(str.title)
    name_out = Join()


class Mrbricolagebg_spider(scrapy.Spider):
    name = "Mrbricolagebg"

    start_urls = ['https://mr-bricolage.bg/instrumenti/veloaksesoari/c/006014']

    def parse(self, response):
        products_links = response.css('a.name::attr(href)')
        yield from response.follow_all(products_links, self.parse_request)
        all_pages = response.css('li.pagination-next a')
        yield from response.follow_all(all_pages, self.parse)

    def parse_request(self, response):
        request_url = {}
        article_text = response.css('div.col-md-12.bricolage-code::text').get().strip()
        if article_text:
            article_id = article_text.replace('Код Bricolage: ', '')
            request_url = f"https://mr-bricolage.bg/store-pickup/{article_id}/pointOfServices"

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
            callback=self.parse_product_info,
            meta={'page_response': response},
            body=body
        )

    def parse_product_info(self, response):
        page = response.meta.get('page_response')

        loader = ItemLoader(Product(), page)

        loader.add_value('url', page.url)
        loader.add_css('title', 'h1.js-product-name::text')
        loader.add_css('ean', 'div[id="home"] span::text', re='[^\s]+')
        loader.add_css('article_id', 'div.col-md-12.bricolage-code::text', re='\w+$')
        loader.add_value('availability', page.css('div.col-md-12.bricolage-availability::text').get().strip())
        loader.add_css('images', 'div.owl-thumb-item img::attr(src)')

        specs_table = [{'key': row.css('td:nth-child(1)::text').get().strip(),
                        'value': row.css('td:nth-child(2)::text').get().strip()} for row
                       in page.css('table.table tr')]
        loader.add_value('specs_table', specs_table)

        r = json.loads(response.text)
        store_availability = [{"store": key['displayName'], "Availability": key['stockPickup']} for key in r['data']]

        loader.add_value('store_availability', store_availability)
        return loader.load_item()
