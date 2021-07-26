import scrapy


class BitcoinabuseItem(scrapy.Item):
    address = scrapy.Field()
    abuse_type = scrapy.Field()
    abuser = scrapy.Field()
    description = scrapy.Field()
    timestamp = scrapy.Field()
    url = scrapy.Field()
    title = scrapy.Field()
    response = scrapy.Field()
