import pymysql
import scrapy
from scrapy.cmdline import execute

from ics_v1.items import IcsV1SiteMapLinksItem
import ics_v1.db_config as db


class OmegaLinksSpider(scrapy.Spider):
    name = 'omega_links'
    allowed_domains = ['omega.com']
    start_urls = ['https://www.omega.com/hybris-sitemap.xml']
    VENDOR_ID = "ACT-B2-013"
    VENDOR_NAME = "TE connectivity"

    def __init__(self, name=None, **kwargs):
        super().__init__(name, **kwargs)
        # DATABASE CONNECTION
        self.con = pymysql.connect(host=db.db_host, user=db.db_user, password=db.db_password, db=db.db_name)
        self.cursor = self.con.cursor()

    def parse(self, response, **kwargs):
        response.selector.remove_namespaces()
        for url in response.xpath("//loc//text()").getall():
            if '/p/' not in url:
                continue
            item = IcsV1SiteMapLinksItem()
            item['vendor_id'] = self.VENDOR_ID
            item['vendor_name'] = self.VENDOR_NAME
            item['product_urls'] = url
            yield item


if __name__ == '__main__':
    execute("scrapy crawl omega_links".split())
