# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html
from re import sub

import scrapy
from itemloaders.processors import MapCompose


def clear_price(value: str):
    if value.strip():
        return sub(r'[^0-9.]', '', value).strip()


class IcsV1Item(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class IcsV1SiteMapLinksItem(scrapy.Item):
    # USE THIS ITEM TO STORE THE LINKS COLLECTED USING THE SITEMAP

    vendor_id = scrapy.Field()
    vendor_name = scrapy.Field()
    product_urls = scrapy.Field()
    meta_data = scrapy.Field()


class IcsV1PDPItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    id = scrapy.Field()
    vendor_id = scrapy.Field()
    hash_key = scrapy.Field()
    vendor_name = scrapy.Field()
    sku = scrapy.Field()
    pdp_url = scrapy.Field()
    name = scrapy.Field()
    category = scrapy.Field()
    uom = scrapy.Field()
    sku_unit = scrapy.Field()
    sku_quantity = scrapy.Field()
    quantity_increment = scrapy.Field()
    pack_label = scrapy.Field()
    available_to_checkout = scrapy.Field()
    in_stock = scrapy.Field()
    estimated_lead_time = scrapy.Field()
    description = scrapy.Field()
    description_html = scrapy.Field()
    manufacturer = scrapy.Field()
    mpn = scrapy.Field()
    attributes = scrapy.Field()
    features = scrapy.Field()
    _scrape_metadata = scrapy.Field()
    status = scrapy.Field()


class IcsV1PricingItem(scrapy.Item):
    # USE THIS ITEM TO STORE THE PRICING COLLECTED BY THE SCRAPERS
    vendor_id = scrapy.Field()
    hash_key = scrapy.Field()
    sku = scrapy.Field()
    min_qty = scrapy.Field()
    price = scrapy.Field(input_processor=MapCompose(clear_price, float), )
    price_string = scrapy.Field()
    currency = scrapy.Field()


class IcsV1AssetItem(scrapy.Item):
    # USE THIS ITEM TO STORE THE PRICING COLLECTED BY THE SCRAPERS
    vendor_id = scrapy.Field()
    hash_key = scrapy.Field()
    sku = scrapy.Field()
    name = scrapy.Field()
    source = scrapy.Field()
    file_name = scrapy.Field()
    is_main_image = scrapy.Field()
    type = scrapy.Field()
