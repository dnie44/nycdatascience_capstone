from scrapy import Spider, Request
from redfin.items import RedfinItem

base_redfin_url = 'https://www.redfin.com'
zip_list = ['20001']
RF_item = RedfinItem() #initate items

class RedfinSpider(Spider):
    name = 'redfin_spider'
    allowed_urls = ['https://redfin.com']

    start_urls = [f'{base_redfin_url}/zipcode/{zip_code}' for zip_code in zip_list]

    def parse(self, response):
        house_urls = response.xpath('//a[@class="slider-item "]/@href').extract()
        result_urls = [f'{base_redfin_url}{house}' for house in house_urls]

        for url in result_urls:
            yield Request(url=url, callback=self.parse_results_page)

    def parse_results_page(self, response):
        # extracts property address from title
        RF_item['Prop_Addr'] = response.xpath('//h1/div[@class="street-address"]/@title').extract()[0]
        # extracts major stats of house from //div/class="statsValue": Listing_Price, tot_beds, tot_baths
        RF_item['Listing_Price'] = response.xpath("//div[@class='statsValue']/text()").extract()[0]
        try:
            RF_item['Tot_beds'] = response.xpath("//div[@class='statsValue']/text()").extract()[1]
        except:
            RF_item['Tot_beds'] = 0
        try:
            RF_item['Tot_baths'] = response.xpath("//div[@class='statsValue']/text()").extract()[2]
        except:
            RF_item['Tot_baths'] = 0
        # extracts SQFT of house from //div/class="stat-block sqft-section"/span
        RF_item['Sqft'] = response.xpath("//div[@class='stat-block sqft-section']/span/text()").extract()[0]
        # extracts property desc from //p/class="text-base"/span
        RF_item['Text_base'] = response.xpath("//p[@class='text-base']/span/text()").extract()[0]
        
        yield RF_item
