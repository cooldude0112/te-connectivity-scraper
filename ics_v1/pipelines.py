# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import ics_v1.db_config as db
from ics_v1.items import IcsV1SiteMapLinksItem, IcsV1PricingItem, IcsV1PDPItem, IcsV1AssetItem


# useful for handling different item types with a single interface


class IcsV1Pipeline:

    def insert_item(self, item, spider, table_name, product_table=0):
        try:
            if product_table:
                id = item.pop('id')

            field_list = []
            value_list = []

            for field in item:
                field_list.append(str(field))
                value_list.append('%s')

            fields = ','.join(field_list)
            values = ", ".join(value_list)
            insert_db = f"insert into {table_name}( " + fields + " ) values ( " + values + " )"
            spider.cursor.execute(insert_db, tuple(item.values()))

            if product_table:
                update = f'update {db.sitemap_table} set status="Done" where Id=%s'
                spider.cursor.execute(update, id)

            spider.con.commit()
            spider.logger.info(f'{table_name} Inserted...')
            spider.con.commit()
        except Exception as e:
            spider.logger.error(e)

    def process_item(self, item, spider):

        if isinstance(item, IcsV1SiteMapLinksItem):
            self.insert_item(item, spider, db.sitemap_table)
        if isinstance(item, IcsV1AssetItem):
            self.insert_item(item, spider, db.asset_table)
        if isinstance(item, IcsV1PricingItem):
            self.insert_item(item, spider, db.pricing_table)
        if isinstance(item, IcsV1PDPItem):
            self.insert_item(item, spider, db.product_table, 1)

        return item
