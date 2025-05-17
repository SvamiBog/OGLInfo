import scrapy

class MakeModelItem(scrapy.Item):
    make_name   = scrapy.Field()
    make_slug   = scrapy.Field()
    model_name  = scrapy.Field()
    model_slug  = scrapy.Field()
