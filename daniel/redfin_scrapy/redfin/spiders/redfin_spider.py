from scrapy import Spider, Request
from redfin.items import RedfinItem
import pandas as pd
import re

base_redfin_url = 'https://www.redfin.com'
ZIP_list = pd.read_csv('smh_zipcodes.csv', index_col='ZipCode').index #list of 6987 ZipCodes
RF_item = RedfinItem() #initate items

class RedfinSpider(Spider):
    name = 'redfin_spider'
    allowed_urls = ['https://redfin.com']

    start_urls = [f'{base_redfin_url}/zipcode/{zip_code}' for zip_code in ZIP_list]

    def parse(self, response):
        # obtain number of pages in ZIP search
        page_text = response.xpath("//div[@class='HomeViews']//span[@class='pageText']/text()").extract_first()
        total_pages = int(re.findall('\d+$',page_text)[0])
        
        page_urls = [f'{response.url}/page-{n}' for n in range(1,total_pages+1)]

        for url in page_urls:
            yield Request(url=url, callback=self.parse_results_page)
    
    def parse_results_page(self, response):
        # obtain house links for each page of search
        house_links = response.xpath('//a[@class="slider-item "]/@href').extract()
        result_urls = [f'{base_redfin_url}{house}' for house in house_links]

        for url in result_urls:
            yield Request(url=url, callback=self.parse_house_page)

    def parse_house_page(self, response):
        # extracts PROP ADDRESS from title
        RF_item['Prop_Addr'] = response.xpath('//h1/div[@class="street-address"]/@title').extract_first()
        # extracts LISTPRICE
        RF_item['ListPrice'] = response.xpath("//div[@class='statsValue']/text()").extract_first()
        # extracts PROP DESCRIPTION
        RF_item['Text_base'] = response.xpath("//p[@class='text-base']/span/text()").extract_first()
        # extracts ZipCode
        RF_item['ZipCode'] = response.xpath("//h1/div[@class='dp-subtext']/text()").re('\d+')[0]

        # Extracts MLS number
        MLS_loc = response.xpath("//div[@class='keyDetailsList']\
                                //span[@class='header font-color-gray-light inline-block']/text()").extract().index('MLS#')
        RF_item['MLS_num'] = response.xpath("//div[@class='keyDetailsList']//span[@class='content text-right']/text()").extract()[MLS_loc-1]

        # extracts HOME FACTS table information
        # home_facts = response.xpath("//div[@class='keyDetailsList']//span[@class='content text-right']/text()").extract()
        # RF_item['Time_onRF'] = home_facts[0]
        # RF_item['Prop_type'] = home_facts[1]
        # RF_item['HOA_dues'] = home_facts[2]
        # RF_item['Year_built'] = home_facts[3]
        # RF_item['Prop_style'] = home_facts[4]
        # RF_item['Community'] = home_facts[5]
        # RF_item['MLS_num'] = home_facts[6]
        # # extracts PRICE INSIGHTS table information
        # RF_item['ListPrice2'] = home_facts[7]
        # RF_item['EstMo_pmt'] = home_facts[8]
        # if len(home_facts) == 11:
        #     RF_item['RF_PriceEst'] = 'NaN'
        #     RF_item['Price_perSF'] = home_facts[9]
        #     RF_item['Buyers_comm'] = home_facts[10]
        # else:
        #     RF_item['RF_PriceEst'] = home_facts[9]
        #     RF_item['Price_perSF'] = home_facts[10]
        #     RF_item['Buyers_comm'] = home_facts[11]

        # extracts PUBLIC FACTS table information
        # public_facts = response.xpath("//div[@class='facts-table']//div[@class='table-value']/text()").extract()
        # RF_item['Tot_beds'] = public_facts[0]
        # RF_item['Tot_baths'] = public_facts[1]
        # RF_item['Fin_sqft'] = public_facts[2]
        # RF_item['Unf_sqft'] = public_facts[3]
        # RF_item['Tot_sqft'] = public_facts[4]
        # RF_item['Stories'] = public_facts[5]
        # RF_item['Lot_size'] = public_facts[6]
        # RF_item['Prop_style2'] = public_facts[7]
        # RF_item['YearBuilt2'] = public_facts[8]
        # RF_item['YearReno'] = public_facts[9]
        # RF_item['County'] = public_facts[10]
        # RF_item['APN_num'] = public_facts[11]

        # extracts TRANSPORTATION Info
        transportation = response.xpath("//div[@class='walk-score']//div[@class='percentage']/span/text()").re('\d+')
        RF_item['Walk_score'] = transportation[0]
        RF_item['Transit_score'] = transportation[2]
        RF_item['Bike_score'] = transportation[4]

        yield RF_item
