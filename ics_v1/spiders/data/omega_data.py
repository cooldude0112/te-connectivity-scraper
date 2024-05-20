import datetime
import json
import os.path
import re
import pymysql
import scrapy
from itemloaders import ItemLoader
from itemloaders.processors import TakeFirst, Join
from scrapy.cmdline import execute

import ics_v1.db_config as db
from ics_v1.items import IcsV1PDPItem, IcsV1PricingItem, IcsV1AssetItem


def check_status(x):
    return True if x and x[0].endswith('InStock') else False


class OmegaDataSpider(scrapy.Spider):
    name = 'omega_data'
    allowed_domains = ['omega.com']
    start_urls = ['http://omega.com/']
    VENDOR_ID = "ACT-B2-013"
    VENDOR_NAME = "TE connectivity"
    page_save = 'C:/Work/Actowiz/pages/ics/htmls/' + VENDOR_ID + "-" + VENDOR_NAME + "/"

    def __init__(self, name=None, **kwargs):
        super().__init__(name, **kwargs)
        # DATABASE CONNECTION
        self.con = pymysql.connect(host=db.db_host, user=db.db_user, password=db.db_password, db=db.db_name)
        self.cursor = self.con.cursor()
        if not os.path.exists(self.page_save):
            os.makedirs(self.page_save)

    def start_requests(self):
        select_query = [
            f"select id, product_urls from {db.sitemap_table} where",
            f"vendor_id = '{self.VENDOR_ID}'",
            f"and status = 'pending'",
            f"and id between 1 and 500"
        ]

        self.cursor.execute(" ".join(select_query))

        for data in self.cursor.fetchall():
            yield scrapy.Request(
                url=data[1],
                # url="https://www.omega.com/en-us/test-inspection/air-soil-liquid-and-gas/gas-analyzers/p/AQM-101-HCHO-Monitor",
                # url="https://www.omega.com/en-us/control-monitoring/process-switches/temperature-switches/p/TSW-TT",
                cb_kwargs={
                    "id": data[0]
                }
            )

    def parse(self, response, **kwargs):

        # open_in_browser(response)
        sku = response.xpath('//span[@itemprop="sku"]/text()').get('')
        id = kwargs['id']
        open(self.page_save + str(id) + ".html", "wb").write(response.body)

        # EXTRACTING PRODUCT DETAILS
        product_loader = ItemLoader(item=IcsV1PDPItem(), selector=response)
        product_loader.default_output_processor = TakeFirst()

        # SETTING VALUES
        product_loader.add_value('id', id)
        product_loader.add_value('vendor_id', self.VENDOR_ID)
        product_loader.add_value('vendor_name', self.VENDOR_NAME)
        product_loader.add_value('sku', sku)
        product_loader.add_value('mpn', sku)
        product_loader.add_value('pdp_url', response.url)

        product_loader.add_xpath('name', '//h1[@class="product-name"]//text()', Join())

        product_loader.add_xpath('category', '//li[@itemprop="itemListElement"]//span[@itemprop="name"]//text()')
        product_loader.replace_value('category', json.dumps(product_loader.get_collected_values('category')))

        # pending
        # product_loader.replace_value('available_to_checkout', json.dumps(product_loader.get_collected_values('category')))

        product_loader.add_xpath('in_stock', '//meta[@itemprop="availability"]/@content', check_status)

        product_loader.add_xpath('estimated_lead_time', '//div[contains(@class, "lead-time")]/span/text()')

        product_loader.add_xpath('description', '//div[@itemprop="description" and @class="tab-details"]//text()')
        product_loader.replace_value(
            'description', " ".join(product_loader.get_collected_values('description')).strip()
        )

        product_loader.add_xpath('description_html', '//div[@itemprop="description" and @class="tab-details"]')
        product_loader.replace_value(
            'description_html', " ".join(product_loader.get_collected_values('description_html')).strip()
        )


        attributes = list()
        for attribute in response.xpath('//div[@class="variant-form-container"]'):
            attributes.append({
                'name': attribute.xpath('.//div[@class="variant-name"]//text()').get('').strip(),
                'value': attribute.xpath('.//option[@selected="selected"]/text()').get('').strip(),
                'group': None,
            })
        product_loader.add_value('attributes', json.dumps(attributes))

        scrape_metadata = dict()
        scrape_metadata['url'] = response.url
        scrape_metadata['date_visited'] = str(datetime.datetime.now()).replace(" ", "T")[:-3] + "Z"
        breadcrumbs = [{"name":"Home","url":"https://www.te.com/usa-en/home.html"}]

        for breadcrumb in response.xpath('//ol[@class="breadcrumb"]//li')[:-1]:
            breadcrumbs.append({
                "name": breadcrumb.xpath('.//a//text()')[-1].get(),
                "url": response.urljoin(breadcrumb.xpath('.//a/@href').get())
            })

        scrape_metadata['breadcrumbs'] = breadcrumbs
        product_loader.add_value('_scrape_metadata', json.dumps(scrape_metadata))
        product_loader.add_value('status', 'Done')
        yield product_loader.load_item()

        # EXTRACTING PRICES
        #
        pricing_loaders = ItemLoader(item=IcsV1PricingItem(), selector=response)
        pricing_loaders.default_output_processor = TakeFirst()
        pricing_loaders.add_value('vendor_id', self.VENDOR_ID)
        pricing_loaders.add_value('sku', sku)
        pricing_loaders.add_value('price_string', "")
        pricing_loaders.add_value('currency', "USD")
        pricing_loaders.add_xpath('min_qty', '//input[@name="pdpAddtoCartInput"]/@data-min')
        pricing_loaders.add_xpath('price', '//input[@name="variantPriceValue"]/@value')

        if 'Volume discounts available' in response.text:

            for tr in response.xpath('//table[@class="volume__prices"]//tr[./td]'):
                all_td = [i.strip() for i in tr.xpath(".//td//text()").getall() if i.strip()]

                pricing_loaders.replace_value('min_qty', re.findall("\d+", all_td[0]))
                pricing_loaders.replace_value('price', all_td[1])

                yield pricing_loaders.load_item()
        else:
            yield pricing_loaders.load_item()

        # ASSET STORING
        item = IcsV1AssetItem()
        item['vendor_id'] = self.VENDOR_ID
        item['sku'] = sku

        for index, images in enumerate(response.xpath('//img[@data-zoom-image]')):

            image_item = item.copy()
            if not index:
                image_item['is_main_image'] = True

            image_item['name'] = images.xpath('./@alt').get('')
            image_item['source'] = images.xpath('./@data-zoom-image').get('')
            image_item['file_name'] = image_item['source'].split("?")[0].split("/")[-1]

            yield image_item

        product_data_sheet = response.xpath('//div[@class="tabbody support-material"]//a')
        for data_sheet in product_data_sheet:
            data_sheet_item = item.copy()
            data_sheet_item['name'] = data_sheet.xpath("./text()").get('').strip()
            data_sheet_item['source'] = data_sheet.xpath("./@href").get('')
            data_sheet_item['file_name'] = data_sheet_item['source'].split("?")[0].split("/")[-1]
            if data_sheet_item['source'].startswith("http") and 'View Certificate' not in data_sheet_item['name']:
                yield data_sheet_item


if __name__ == '__main__':
    execute("scrapy crawl omega_data".split())
