# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class RedfinItem(scrapy.Item):
    # define the fields for your item here like:
    # These are the stats at the top of House page
    Prop_Addr = scrapy.Field()
    ListPrice = scrapy.Field()
    ZipCode = scrapy.Field()
    # This is the text description
    Text_base = scrapy.Field()

    # This is the Home Facts table information
    # Prop_status = scrapy.Field()
    # Prop_type = scrapy.Field()
    # Year_built = scrapy.Field()
    # Community = scrapy.Field()
    # Time_onRF = scrapy.Field()
    # HOA_dues = scrapy.Field()
    # Prop_style = scrapy.Field()
    MLS_num = scrapy.Field()

    # This is the Price Insights table information
    # ListPrice2 = scrapy.Field()
    # Price_perSF = scrapy.Field()
    # RF_PriceEst = scrapy.Field()
    # EstMo_pmt = scrapy.Field()
    # Buyers_comm = scrapy.Field()

    # This is the Public Facts table information
    # Tot_beds = scrapy.Field()
    # Tot_baths = scrapy.Field()
    # Fin_sqft = scrapy.Field()
    # Unf_sqft = scrapy.Field()
    # Tot_sqft = scrapy.Field()
    # Stories = scrapy.Field()
    # Lot_size = scrapy.Field()
    # Prop_style2 = scrapy.Field()
    # YearBuilt2 = scrapy.Field()
    # YearReno = scrapy.Field()
    # County = scrapy.Field()
    # APN_num = scrapy.Field()

    # Flood & Climate Risk
    #FC_risk = scrapy.Field()

    # Transit Information
    Walk_score = scrapy.Field()
    Transit_score = scrapy.Field()
    Bike_score = scrapy.Field()
