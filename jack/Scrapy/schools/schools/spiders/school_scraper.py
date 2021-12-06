import scrapy 
import re
import json

class SchoolSpider(scrapy.Spider):
    name = "school_scraper"
    start_urls = ['https://www.greatschools.org/search/search.zipcode?sort=rating&zip=20852']

    def parse(self, response):
        # dict_text = response.xpath("//script").extract_first()
        # print(dict_text)
        # print("-"*55)
        # match = re.search(r'gon.search=', dict_text)
        # print("HEYYY")
        # print(dict_text[match.end():])
        res = response.xpath("//script").extract_first()
        x = json.loads(re.search(r'gon.search=(.*?);', res).group(1))
        schools = x['schools']
        print(len(schools))

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