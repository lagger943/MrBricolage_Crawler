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
        def extract_with_css(query):
            return response.css(query).get(default='').strip()

        product = {}
        product.update({'Title': extract_with_css('h1.js-product-name::text')})
        
        raw_price = response.css('p.price.js-product-price::text').re('[^\t\n\xa0]+')[0]
        price =  ''.join(raw_price)
        price = price.replace(',','.')
        product.update({'Price': price})
        
        availability = extract_with_css('div.col-md-12.bricolage-availability::text')
        availability = availability.replace('\xa0','')
        product.update({'Availability': availability})
        
        article_text = extract_with_css('div.col-md-12.bricolage-code::text')
        article_id= article_text.replace('Код Bricolage: ', '')
        product.update({'ArticleID': article_id})
        
        
        EAN =  response.css('div[id="home"] span::text').re('[^\t\n\xa0]+')[0]
        product.update({'EAN': EAN})
        product.update({'URL': response.url})
        product.update({'images': response.css('div.owl-thumb-item img::attr(src)').getall()})
        
        table = response.xpath('//*[@class="table"]//tbody//td//text()').re('[^\t\n\xa0]+')
        
        if "Марка" in table:
            index = table.index('Марка')
            brand = table[index+1]
            table.pop(index)
            table.pop(index)
            product.update({'Brand': brand})
        if "Модел" in table:
            index = table.index('Модел')
            model = table[index+1]
            table.pop(index)
            table.pop(index)
            product.update({'Model': model})
        if "Наименование" in table:
            index = table.index('Наименование')
            name = table[index+1]
            table.pop(index)
            table.pop(index)
            product.update({'Name': name})
        if "Произход" in table:    
            index = table.index('Произход')
            origin = table[index+1]
            table.pop(index)
            table.pop(index)
            product.update({'Origin': origin})
        if "Гаранция" in table:    
            index = table.index('Гаранция')
            origin = table[index+1]
            table.pop(index)
            table.pop(index)
            table.pop(index)
            product.update({'Warranty': origin + " Години"})
        if len(table) > 0:
            product.update({"Other Atributes:": table})
        yield product
