import scrapy


class MrbricolageSpider(scrapy.Spider):
    name = "Mrbricolagebg"

    start_urls = ['https://mr-bricolage.bg/instrumenti/veloaksesoari/c/006014']

    def parse(self, response):
        products_links = response.css('a.name::attr(href)')
        yield from response.follow_all(products_links, self.parse_product)
        all_pages = response.css('li.pagination-next a')
        yield from response.follow_all(all_pages, self.parse)

    def parse_product(self, response):
        def get_strip(path):
            return response.css(path).get().strip()

        def spec_table_attributes_extract():

            [product.update({'brand': key['value']}) for key in specs_table if "Марка" in key['key']]

            [product.update({'model': key['value']}) for key in specs_table if "Модел" in key['key']]

            [product.update({'origin': key['value']}) for key in specs_table if "Произход" in key['key']]

            [product.update({'warranty': key['value']}) for key in specs_table if "Гаранция" in key['key']]

        product = {}

        product.update({'title': get_strip('h1.js-product-name::text')})

        raw_price = get_strip('p.price.js-product-price::text')
        if raw_price:
            price = raw_price.replace(',', '.')
            product.update({'price': price})

        availability = get_strip('div.col-md-12.bricolage-availability::text')
        if availability:
            product.update({'availability': availability})

        article_text = get_strip('div.col-md-12.bricolage-code::text')
        if article_text:
            article_id = article_text.replace('Код Bricolage: ', '')
            product.update({'article_id': article_id})

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

        product.update({"specs_table": specs_table})

        yield product
