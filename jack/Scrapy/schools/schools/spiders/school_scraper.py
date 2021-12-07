import scrapy 
import re
import json

class SchoolSpider(scrapy.Spider):
    name = "school_scraper"
    num_pages = 1

    ## Need to get the links for zips and pages -- right now it only looks at the first page of one zip
    links = []
    for i in range(1,3):
        link = 'https://www.greatschools.org/search/search.zipcode?page=' + str(i) + '&sort=rating&zip=20852'
        links.append(link)
    start_urls = links

    def parse(self, response):

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

            yield dict