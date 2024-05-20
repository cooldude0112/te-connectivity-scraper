import os.path
import time
import pymysql
import scrapy
from scrapy.cmdline import execute
from scrapy.utils.response import open_in_browser
import hashlib
import ics_v1.db_config as db


class DownloadAssestSpider(scrapy.Spider):
    name = 'download_assest'
    assets_save = 'C:/Work/Actowiz/pages/ics/assets/'
    VENDOR_ID = "ACT-B2-013"
    VENDOR_NAME = "TE connectivity"

    def __init__(self,name=None, vendor_id=None, **kwargs):
        super().__init__(name, **kwargs)
        if not vendor_id:
            exit(-1)
        self.VENDOR_ID = vendor_id
        self.assets_save += vendor_id + "/"
        if not os.path.exists(self.assets_save):
            os.makedirs(self.assets_save)
        # self.start = start
        # self.end = end
        self.con = pymysql.connect(host=db.db_host, user=db.db_user, password=db.db_password, db=db.db_name)
        self.cursor = self.con.cursor()

    def start_requests(self):
        # select_query = [
        #     f"select id, source, file_name, is_main_image, name from {db.asset_table} where",
        #     f"vendor_id = '{self.VENDOR_ID}'",
        #     f"and status = 'pending'"
        #     f"and id between {self.start} and {self.end}"
        # ]
        #
        # self.cursor.execute(" ".join(select_query))
        # for data in self.cursor.fetchall():
        #     print(data)
        #     yield scrapy.Request(
        #         url=data[1],
        #         cb_kwargs={
        #             "id": data[0],
        #             "file_name": data[2],
        #             "main": data[3],
        #             "name": data[4],
        #         },
        #         dont_filter=True
        #     )
        #     time.sleep(2)

        batch_counter = 0
        for index in range(0, 867816, 1000):
            select_query = (f"select id, source, file_name, is_main_image, name from {db.asset_table} where",
                            f"vendor_id = '{self.VENDOR_ID}'"
                            f'and status = "pending" and '
                            f'id between {index + 1} and {index + 1000}')
            self.cursor.execute(" ".join(select_query))
            bunch = self.cursor.fetchall()
            for url_data in bunch:
                yield scrapy.Request(
                    url=url_data[1],
                    cb_kwargs={"id":url_data[0],"file_name": url_data[2],"main": url_data[3],"name": url_data[4],
                                },dont_filter=True)
                batch_counter += 1  # Increment the counter
                if batch_counter % 50 == 0:  # Pause for 5 seconds every 50 bunches
                    time.sleep(1)


    def parse(self, response, **kwargs):
        file_name = kwargs['file_name']
        if response.url.endswith(".exe"):
            file_name = response.url.split("/")[-1]
        if not file_name or file_name.endswith(".zip") or file_name.endswith(".asp") or file_name.endswith(".pdp"):
            try:
                file_name = response.headers['content-disposition'].decode("utf-8").split("=")[-1].strip('"')
            except:
                file_name = ''

        file_type = None
        if kwargs['main']:
            file_type = "image/product"
        elif ".zip" in file_name:
            file_type = "other"
        elif file_name.split(".")[-1].lower() in ['dxf', 'dwg', 'slddrw']:
            file_type = "cad/2D"
        elif file_name.split(".")[-1].lower() in ['step', 'iges', 'igs', 'sldprt', 'ipt', 'x_t', 'eprt', '.step']:
            file_type = "cad/3D"
        elif file_name.split(".")[-1].lower() in ['cert', 'crt']:
            file_type = "document/cert"

        if 'software' in kwargs['name'].lower():
            file_type = "other"

        if not file_type:
            if 'manual' in kwargs['name'].lower():
                file_type = "document/manual"
            elif 'spec' in kwargs['name'].lower():
                file_type = "document/spec"
            elif 'catalog' in kwargs['name'].lower():
                file_type = "document/catalog"

        if not file_type and '.pdf' in file_name.lower():
            file_type = "document"

        if not file_type and file_name.split(".")[-1].lower() in ['png', 'jpg']:
            file_type = "image/product"

        if not file_type:
            file_type = "other"
        if 'Content-Length' in response.headers:
            length=response.headers['Content-Length'].decode("utf-8")
        else:
            length=response.body.__sizeof__()


        sha256 = hashlib.sha256(response.body).hexdigest()

        item = dict()
        item['download_path'] = self.assets_save + str(sha256)
        item['media_type'] = response.headers['Content-Type'].decode("utf-8")
        item['length'] = length
        item['type'] = file_type
        item['sha256'] = sha256
        item['file_name'] = file_name
        item['status'] = "Done"

        print(item)

        open(item['download_path'], "wb").write(response.body)

        try:
            id = kwargs['id']

            field_list = []
            for field in item.items():
                field_list.append(f'{field[0]}="{field[1]}"')

            update = f'update {db.asset_table} set {", ".join(field_list)} where Id=%s'
            self.cursor.execute(update, id)

            self.con.commit()
            self.logger.info(f'{db.asset_table} Inserted...')
            self.con.commit()

        except Exception as e:
            print(e)
            self.logger.error(e)


if __name__ == '__main__':
    execute("scrapy crawl download_assest -a vendor_id=ACT-B2-013".split())
