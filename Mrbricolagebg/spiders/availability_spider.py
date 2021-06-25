import scrapy
from scrapy import Request
import json


class MrbricolageAvailabilitySpider(scrapy.Spider):
    name = "Mrbricolagebg_availability"

    product = {}

    start_urls = ['https://mr-bricolage.bg/instrumenti/veloaksesoari/c/006014']

    def parse(self, response):
        products_links = response.css('a.name::attr(href)')
        yield from response.follow_all(products_links, self.parse_product)
        all_pages = response.css('li.pagination-next a')
        yield from response.follow_all(all_pages, self.parse)

    def parse_product(self, response):
        request_url = ""

        article_text = self.get_and_strip('div.col-md-12.bricolage-code::text', response)
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

        return Request(
            url=request_url,
            method='POST',
            dont_filter=True,
            cookies=cookies,
            headers=headers,
            callback=self.parse_availability_info,
            body=body,
            meta={'page_response': response}
        )

    def get_and_strip(self, path, response):
        return response.css(path).get().strip()

    def parse_availability_info(self, response):
        page = response.meta.get('page_response')
        r = json.loads(response.text)
        self.product.update({'Request url': page.url})
        store_availability = [{"store": key['displayName'], "Availability": key['stockPickup']} for key in r['data']]
        self.product.update({"Availability": store_availability})
        yield self.product
