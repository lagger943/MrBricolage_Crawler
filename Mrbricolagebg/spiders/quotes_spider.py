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
      
        def table_atributes_extract(table):     
            if "Марка" in table:
                index = table.index('Марка')
                brand = table[index+1]
                table.pop(index)
                table.pop(index)
                product.update({'brand': brand})
            if "Модел" in table:
                index = table.index('Модел')
                model = table[index+1]
                table.pop(index)
                table.pop(index)
                product.update({'model': model})
            if "Наименование" in table:
                index = table.index('Наименование')
                name = table[index+1]
                table.pop(index)
                table.pop(index)
                product.update({'name': name})
            if "Произход" in table:    
                index = table.index('Произход')
                origin = table[index+1]
                table.pop(index)
                table.pop(index)
                product.update({'origin': origin})
            if "Гаранция" in table:    
                index = table.index('Гаранция')
                warranty = "{} {}".format(table[index+1],table[index+2])
                table.pop(index)
                table.pop(index)
                table.pop(index)
                product.update({'warranty': warranty})
            if len(table) > 0:
                other_attributes = " ".join(table)
                product.update({"other attributes:": other_attributes})
            
        
        product = {}
        
        product.update({'title': response.css('h1.js-product-name::text').get().strip()})
        
        raw_price = response.css('p.price.js-product-price::text').re('[^\sлв.]+')[0]
        if raw_price:
            price = raw_price.replace(',','.')
            product.update({'price': price})
        
        
        availability = response.css('div.col-md-12.bricolage-availability::text').get().strip()
        if availability:
            product.update({'availability': availability})
        
        article_text = response.css('div.col-md-12.bricolage-code::text').get().strip()
        if article_text:
            article_id= article_text.replace('Код Bricolage: ', '')
            product.update({'article_id': article_id})
        
        ean = response.css('div[id="home"] span::text').re('[^\s]+')[0]
        if ean:
            product.update({'ean': ean})
        
        product.update({'url': response.url})
        
        images = response.css('div.owl-thumb-item img::attr(src)').getall()
        if images:
            product.update({'images': images})
        
        table = response.xpath('//*[@class="table"]//tbody//td//text()').re('[^\s]+')
        if table:
            table_atributes_extract(table)
        
        yield product
        
    
