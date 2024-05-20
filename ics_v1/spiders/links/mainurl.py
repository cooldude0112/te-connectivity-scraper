import json
import scrapy
import html
from scrapy.cmdline import execute
from scrapy.selector import Selector
import pymysql
from ics_v1 import db_config as db



class MainurlSpider(scrapy.Spider):
    name = "mainurl"
    allowed_domains = ["te.com"]
    start_urls =["http://www.te.com/usa-en/store/view-all-te-store-products.html?q=&type=products&samples=N&inStoreWithoutPL&instock"]

    con = pymysql.connect(host=db.db_host, user=db.db_user, password=db.db_password, db=db.db_name)
    cursor = con.cursor()

    def start_requests(self):
        new_val = -20
        for i in range(2289):
            new_val = new_val + 20
            page_url = f"http://www.te.com/teccatv2/service/search/products?o={new_val}&s=20&n=0&storeid=TEUSA&instock=testore&c=usa&l=en&st=web&mediaType=jsonns"
            # print(page_url)
            yield scrapy.Request(url=page_url,callback=self.parse)


    def parse(self, response):
        json_data = json.loads(response.text)
        for i in json_data["results"]["products"]:
            url = i["tcpn"]
            makeurl = f"http://www.te.com/usa-en/product-{url}.html"
            print(makeurl)
            insert = f"insert into {db.url_table} (url) values ('{makeurl}')"
            self.cursor.execute(insert)
            self.con.commit()


if __name__ == '__main__':
    execute('scrapy crawl mainurl'.split())