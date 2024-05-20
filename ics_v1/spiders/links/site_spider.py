import scrapy
import pymysql
from scrapy.cmdline import execute
from ics_v1.items import IcsV1SiteMapLinksItem
from ics_v1 import db_config as db


class SiteSpiderSpider(scrapy.Spider):
    name = "site_spider"
    allowed_domains = ["www.te.com"]
    start_urls = ["https://www.te.com"]
    VENDOR_ID = "ACT-B2-013"
    VENDOR_NAME = "TE connectivity"

    def __init__(self, name=None, **kwargs):
        super().__init__(name, **kwargs)
        # DATABASE CONNECTION
        self.con = pymysql.connect(host=db.db_host, user=db.db_user, password=db.db_password, db=db.db_name)
        self.cursor = self.con.cursor()

    def parse(self, response):
        qry = f"select url from {db.producturl_table}"
        self.cursor.execute(qry)
        for url in self.cursor.fetchall():
            print(url[0])
            item = IcsV1SiteMapLinksItem()
            item['vendor_id'] = self.VENDOR_ID
            item['vendor_name'] = self.VENDOR_NAME
            item['product_urls'] = url[0]
            yield item

if __name__ == '__main__':
    execute('scarpy crawl site_spider'.split())
