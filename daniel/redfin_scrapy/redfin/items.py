# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class RedfinItem(scrapy.Item):
    # define the fields for your item here like:
    Prop_Addr = scrapy.Field()
    Listing_Price = scrapy.Field()
    Tot_beds = scrapy.Field()
    Tot_baths = scrapy.Field()
    Sqft = scrapy.Field()
    Text_base = scrapy.Field()
