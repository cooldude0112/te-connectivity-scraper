import scrapy
from scrapy.cmdline import execute
from scrapy.selector import Selector
import pymysql
from ics_v1 import db_config as db

class UrlSpiderSpider(scrapy.Spider):
    name = "url_spider"
    allowed_domains = ["te.com"]

    con = pymysql.connect(host=db.db_host, user=db.db_user, password=db.db_password, db=db.db_name)
    cursor = con.cursor()

    def start_requests(self):
        select = f'select url from {db.url_table} where url not like "%CAT%"'
        self.cursor.execute(select)
        for index,url in enumerate(self.cursor.fetchall()):
            # print(index,url[0])
            yield scrapy.Request(url=url[0],cb_kwargs={'index':index},callback=self.parse)

    def parse(self, response, **kwargs):
        print("$$$$$$$",response)
        if "CAT" in response.url:
            link = response.xpath('//noscript').getall()[1]
            selector = Selector(text=link)
            for text in selector.css('div.prod-img a::attr(href)').getall():
                print(text)
                insert = f"insert into {db.producturl_table} (url) values ('{text}')"
                try:
                    self.cursor.execute(insert)
                    self.con.commit()
                    self.logger.info('(IF) Data Inserted successfully')
                except Exception as err:
                    print(f"Database Error : {err}")
        else:
            print(kwargs['index'],response.url)
            insert = f"insert into {db.producturl_table} (url) values ('{response.url}')"
            try:
                self.cursor.execute(insert)
                self.con.commit()
                self.logger.info('(IF) Data Inserted successfully')
            except Exception as err:
                print(f"Database Error : {err}")


if __name__ == '__main__':
    execute('scrapy crawl url_spider'.split())


