import hashlib
import scrapy
import os
import pymysql
import time
from scrapy.cmdline import execute
import json
import re
import gzip
import datetime
from ics_v1 import db_config as db
from ics_v1.items import IcsV1PDPItem,IcsV1AssetItem,IcsV1PricingItem
from itemloaders import ItemLoader
from itemloaders.processors import TakeFirst, Join


def check_status(x):
    return True if x == 'INSTOCK' else False

class PdpSpiderSpider(scrapy.Spider):
    name = "pdp_spider"
    allowed_domains = ["exmaple.com","'api.te.com'"]
    start_urls = ["https://te.com"]
    VENDOR_ID = "ACT-B2-013"
    VENDOR_NAME = "TE connectivity"
    page_save = 'C:/Work/Actowiz/pages/ics/htmls/' + VENDOR_ID + "-" + VENDOR_NAME + "/"
    json_save = 'C:/Work/Actowiz/pages/ics/json/' + VENDOR_ID + "-" + VENDOR_NAME + "/"
    handle_httpstatus_list = [500]


    def __init__(self,start,end,name=None, **kwargs):
    # def __init__(self,name=None, **kwargs):
        super().__init__(name, **kwargs)
        # DATABASE CONNECTION
        self.con = pymysql.connect(host=db.db_host, user=db.db_user, password=db.db_password, db=db.db_name)
        self.cursor = self.con.cursor()
        self.start =int(start)
        self.end = int(end)
        if not os.path.exists(self.page_save):
            os.makedirs(self.page_save)
        if not os.path.exists(self.json_save):
            os.makedirs(self.json_save)

    def start_requests(self):

            # select_query = (f'SELECT id,product_urls from {db.sitemap_table} WHERE '
            #                     f'status = "pending" and '
            #                     f'id between {self.start} and {self.end}')
            # print(select_query)
            # self.cursor.execute(select_query)
            # bunch = self.cursor.fetchall()
            # for url_data in bunch:
            #     final_url = f"{self.page_save}{url_data[0]}.html"
            #     "file:///C:/Work/Actowiz/pages/ics/htmls/ACT-B2-013-TE%20connectivity/1.html"
            #     if os.path.exists(final_url):
            #         final_link=f"file:///C:/Work/Actowiz/pages/ics/htmls/ACT-B2-013-TE%20connectivity/{url_data[0]}.html"
            #         print('1',final_link)
            #         yield scrapy.Request(url=final_link,
            #                              callback=self.parse, cb_kwargs={'id': url_data[0],'pdp_url':url_data[1]})

            batch_counter = 0
            for index in range(0,69300,1000):
                select_query = (f'SELECT id,product_urls from {db.sitemap_table} WHERE '
                                f'status = "pending" and '
                                f'id between {index + 1} and {index + 1000}')
                print(select_query)
                self.cursor.execute(select_query)
                bunch = self.cursor.fetchall()
                for url_data in bunch:
                    yield scrapy.Request(
                        url=url_data[1],
                        # url = "https://www.te.com/usa-en/product-1747067-2.html",
                                         callback=self.parse, cb_kwargs={'id': url_data[0],'pdp_url':url_data[1]})
                    batch_counter += 1  # Increment the counter
                    if batch_counter % 50 == 0:  # Pause for 5 seconds every 50 bunches
                        time.sleep(5)


    def parse(self, response, **kwargs):
        id = kwargs['id']
        # print(id)
        sku = response.xpath('//li[@class="product-tcpn"]/span[@class="part-basic-detail-value"]/text()').get('')
        hash_key = hashlib.sha256(sku.encode()).hexdigest()
        # open(self.page_save + str(id) + ".html.gz", "wb").write(response.body)
        gzip.open(self.page_save + str(id) + ".html.gz", "wb").write(response.body)
        product_loader = ItemLoader(item=IcsV1PDPItem(), selector=response)
        product_loader.default_output_processor = TakeFirst()

        product_loader.add_value('id', id)
        product_loader.add_value('hash_key', hash_key)
        product_loader.add_value('vendor_id', self.VENDOR_ID)
        product_loader.add_value('vendor_name', self.VENDOR_NAME)
        product_loader.add_value('sku', sku)
        mpn = response.xpath('//div[@class="PDP-summary-info desktop"]/h1/text()').get('')
        product_loader.add_value('mpn', mpn)
        product_loader.add_value('pdp_url', kwargs['pdp_url'])

        product_loader.add_xpath('name',
                                 '//li[@class="product-description"]/span[@class="part-basic-detail-value"]/text()',
                                 Join())

        cat = response.xpath('//div[@class="te-pdp-breadcrumb"]//li//p/text()').getall()
        product_loader.add_value('category', cat)
        product_loader.replace_value('category', json.dumps(product_loader.get_collected_values('category')))

        if response.xpath('//div[@class="product-family-series"]/ul/li[1]/text()').get():
            product_loader.add_xpath('manufacturer', '//div[@class="product-family-series"]/ul/li[1]/text()' )
        else:
            product_loader.add_value('manufacturer', self.VENDOR_NAME)

        # product_loader.add_xpath('in_stock', '//meta[@itemprop="availability"]/@content', check_status)

        # product_loader.add_xpath('estimated_lead_time', '//div[contains(@class, "lead-time")]/span/text()')

        des = "".join(response.xpath('//div[@class="product-ids-model-summary"]//li/h3//text()').getall()).replace('\t','').replace('\n', ' ')
        h1 = response.xpath('//div[@class="PDP-summary-info desktop"]//h2/text()').get('')
        describ = re.sub(r'\u2009', '', des)
        describption = h1 + describ
        product_loader.add_value('description', describption)
        product_loader.replace_value(
            'description', " ".join(product_loader.get_collected_values('description')).strip())

        ht = "".join(response.xpath('//div[@class="PDP-summary-info desktop"]//h2').getall()).replace('\n', ' ')
        ml = "".join(response.xpath('//div[@class="product-ids-model-summary"]//li').getall()).strip().replace('\t','').replace('\n', '')
        html = re.sub(r'\u2009', '', ml).replace("&thinsp;", "")
        html = ht + html
        product_loader.replace_value('description_html', html)
        product_loader.replace_value(
            'description_html', " ".join(product_loader.get_collected_values('description_html')).strip())

        attributes = list()
        for attribute in response.xpath('//div[@data-module-component="product-features"]'):
            name_text = attribute.xpath('.//span/text()').getall()
            # decoded = bytes(name_text, "utf-8").decode("unicode_escape")
            # name = re.sub(r'[^\w\s]', '', decoded)
            val_text = attribute.xpath('.//em/text()').getall()
            # decoded_ = bytes(val_text, "utf-8").decode("unicode_escape")
            # value = re.sub(r'[^\w\s]', '', decoded_)
            for att_index in range(len(name_text)):
                attributes.append({
                    'name': name_text[att_index].encode('ascii', 'ignore').decode(),
                    'value': val_text[att_index].encode('ascii', 'ignore').decode(),
                    'group': attribute.xpath('.//h4/text()').get('').strip()
                })
        # print(attributes)
        product_loader.add_value('attributes', json.dumps(attributes))

        scrape_metadata = dict()
        scrape_metadata['url'] = kwargs['pdp_url']
        scrape_metadata['date_visited'] = str(datetime.datetime.now()).replace(" ", "T")[:-3] + "Z"
        breadcrumbs = [{"name": "Home", "url": "https://www.te.com/usa-en/home.html"}]

        for breadcrumb in response.xpath('//div[@class="te-pdp-breadcrumb"]//li'):
            breadcrumbs.append({
                "name": breadcrumb.xpath('.//a//p//text()')[-1].get(),
                "url": response.urljoin(breadcrumb.xpath('.//a/@href').get())
            })

        scrape_metadata['breadcrumbs'] = breadcrumbs
        product_loader.add_value('_scrape_metadata', json.dumps(scrape_metadata))

        # ASSET STORING
        item = IcsV1AssetItem()
        item['vendor_id'] = self.VENDOR_ID
        item['sku'] = sku
        item['hash_key'] = hash_key

        for index, images in enumerate(
            response.xpath('//ul[@class="product-thumbnails"]//img|//div[@class="product-summary-gallery"]//img')):

            image_item = item.copy()
            if not index:
                image_item['is_main_image'] = True

            image_item['name'] = images.xpath('./@data-alt |./@alt').get('')
            image_item['source'] = "https://www.te.com/" + images.xpath('./@src').get('')
            image_item['file_name'] = image_item['source'].split("?")[0].split("/")[-1]
            # print("image", image_item)
            yield image_item

        product_data_sheet = response.xpath('//div[@class="documents-list"]//li/a')
        for data_sheet in product_data_sheet:
            data_sheet_item = item.copy()
            data_sheet_item['name'] = data_sheet.xpath("./text()").get('').strip()
            data_sheet_item['source'] = data_sheet.xpath("./@href").get('')
            # data_sheet_item['file_name'] = data_sheet_item['source'].split("?")[0].split("/")[-1]
            if data_sheet_item['source'].startswith("http") and 'View Certificate' not in data_sheet_item['name']:
                # print("datasheet", data_sheet_item)
                yield data_sheet_item

        time.sleep(0.2)

        # final_url = f"{self.json_save}{kwargs['id']}.html"
        # "file:///C:/Work/Actowiz/pages/ics/htmls/ACT-B2-013-TE%20connectivity/1.html"
        # if os.path.exists(final_url):
        #     final_link = f"file:///C:/Work/Actowiz/pages/ics/json/ACT-B2-013-TE%20connectivity/{kwargs['id']}.html"
        #     print(final_link)

        final_link = f"https://api.te.com/api/v1/exp-tecom-commerce-api/b2c/price-inventory/products?tcpn={sku}&country=usa&language=en"
        yield scrapy.Request(
            url= final_link,
            callback=self.price,
            cb_kwargs={
                'product_dict': product_loader.load_item()},
            # cb_kwargs={'sku': sku, 'url': response.url, 'hash': hash_key, 'id': id},
            dont_filter=True,)


    def price(self,response,**kwargs):
        # print(response.body)
        url = kwargs['product_dict']['pdp_url']
        if response.status == 500:
            qry = f'update {db.sitemap_table} set status = "NOT PRICE" where product_urls ="{url}"'
            self.cursor.execute(qry)
            self.con.commit()
        jsondata = json.loads(response.text)
        gzip.open(self.json_save + str(kwargs['product_dict']['id']) + ".gz", "wb").write(response.body)
        # EXTRACTING PRICES
        pricing_loaders = ItemLoader(item=IcsV1PricingItem(), selector=response)
        pricing_loaders.default_output_processor = TakeFirst()
        pricing_loaders.add_value('vendor_id', self.VENDOR_ID)
        pricing_loaders.add_value('sku', kwargs['product_dict']['sku'])
        hashkey = kwargs['product_dict']['hash_key']
        pricing_loaders.add_value('hash_key',hashkey)
        pricing_loaders.add_value('price_string', "")
        pricing_loaders.add_value('currency', "USD")
        minqty = jsondata["prices"]
        for i in minqty:
            pricing_loaders.replace_value('min_qty', f'{i["minQuantity"]}')
            pricing_loaders.replace_value('price', f'{i["formattedValue"]}')

            if 'Volume discounts available' in response.text:

                for tr in response.xpath('//table[@class="volume__prices"]//tr[./td]'):
                    all_td = [i.strip() for i in tr.xpath(".//td//text()").getall() if i.strip()]

                    pricing_loaders.replace_value('min_qty', re.findall("\d+", all_td[0]))
                    pricing_loaders.replace_value('price', all_td[1])

                    # print("ffffff", pricing_loaders.load_item())
                    yield pricing_loaders.load_item()
            else:
                yield pricing_loaders.load_item()
                # print("eeee", pricing_loaders.load_item())

        # print("!!!!!!!!!!!!!!!",kwargs['product_dict'])
        product_loader = ItemLoader(item=IcsV1PDPItem(), selector=response)
        product_loader.default_output_processor = TakeFirst()
        json_data = jsondata
        availablecheckout = json_data["orderable"]
        stock = json_data["stock"]["stockLevelStatus"]

        product_loader.replace_value('in_stock', f"{stock}", check_status)

        product_loader.add_value('available_to_checkout',availablecheckout)
        delivery_time = json_data["stock"]["standardLeadTime"]
        if delivery_time != 0:
            min_qty = json_data["stockMetaData"]["minimumOrderQuantity"]
            lead_time = [{"min_qty": min_qty ,"time_to_ship": {"raw_value": f"Ships within {delivery_time} days"}}]
            json_lead = json.dumps(lead_time)
            product_loader.add_value('estimated_lead_time', json_lead)
        else:
            plus = json_data["stock"]["stockLevel"]
            lead_time = [{"min_qty": 1,"time_to_ship": {"raw_value": "SHIPS IMMEDIATELY"}},{"min_qty": int(plus)+1 ,"time_to_ship": {"raw_value": None}}]
            json_lead = json.dumps(lead_time)
            product_loader.add_value('estimated_lead_time', json_lead)
        qty_inc = json_data["stockMetaData"]["standardPackagingQty"]
        product_loader.replace_value('quantity_increment',qty_inc)
        product_loader.add_value('hash_key',kwargs['product_dict']['hash_key'])

        product_loader.add_value('status', 'Done')
        for i in kwargs['product_dict']:
            product_loader.add_value(i,kwargs['product_dict'][i])
        # print("####",product_loader.load_item())
        yield product_loader.load_item()



if __name__ == '__main__':
    execute("scrapy crawl pdp_spider -a start=1 -a end=70000".split())
