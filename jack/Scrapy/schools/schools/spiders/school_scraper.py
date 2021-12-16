import scrapy 
from scrapy import Spider, Request
import re
import pandas as pd
import json

zips = pd.read_csv('smh_zips.txt')
zip_codes = zips['ZipCode']
zip_codes =zip_codes.tolist()
    
class SchoolSpider(scrapy.Spider):

    name = "school_scraper"

    start_urls = [f'https://www.greatschools.org/search/search.zipcode?page=1&sort=rating&zip=20852']

    def parse(self, response):
        res = response.xpath("//script").extract_first()
        x = json.loads(re.search(r'gon.search=(.*?);', res).group(1))
        num_pages = x['totalPages'] 
        num_pages += 1

        page_urls = ['https://www.greatschools.org/search/search.zipcode?page=' + str(i) + '&sort=rating&zip=' + str(z) for i in range(1, num_pages) for z in zip_codes]

        print('pageurls =', page_urls)

        for url in page_urls:
            yield Request(url = url, callback = self.parse_results)

    def parse_results(self, response):

        res_2 = response.xpath("//script").extract_first()
        y = json.loads(re.search(r'gon.search=(.*?);', res_2).group(1))
        schools = y['schools']

        dict_list = []

        dict = {}
        for i in range(0, len(schools)):
            temp = schools[i]
            dict['name'] = temp['name']
            dict['street'] = temp['address']['street1']
            dict['city'] = temp['address']['city']
            dict['zip'] = temp['address']['zip']
            dict['state'] = temp['state']
            dict['lat'] = temp['lat']
            dict['long'] = temp['lon']
            dict['districtID'] = temp['districtId']
            dict['districtName'] = temp['districtName']
            dict['gradeLevels'] = temp['gradeLevels']
            dict['ratingScale'] =  temp['ratingScale']
            dict['enrollment'] = temp['enrollment']
            dict['schoolType'] = temp['schoolType']
            dict['pctLowIncome']= temp['percentLowIncome']
            dict['overallRating']  = temp['rating']
            yield dict