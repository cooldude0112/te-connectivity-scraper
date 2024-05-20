import gc
import json
import os
from datetime import datetime
from urllib.parse import quote

import pandas as pd
import pymysql

from validator import do_validation
import time

t1 = time.time()

# DATABASE DETAILS
db_host = 'localhost'
db_user = 'root'
db_password = 'actowiz'
db_name = 'ics_master_db_te_connectivity'

asset_table = "asset_table_copy"
product_table = "product_table"
pricing_table = "pricing_table"

# DEFINING THE GLOBALS
VENDOR_ID = "ACT-B2-013"
TODAY_DATE = datetime.now().strftime('%Y-%m-%d')
OUTPUT_LOCATION = "C:/my_ics_output_folder/"

output_part_files = OUTPUT_LOCATION + f"{db_name}/{TODAY_DATE}/excel/"
if not os.path.exists(output_part_files):
    os.makedirs(output_part_files)

output_folder = OUTPUT_LOCATION + f"{db_name}/{TODAY_DATE}/json/"
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

file_name = output_folder + f"{TODAY_DATE}-v1.json"


def process_asset_df(input_asset_df):
    print("\n\nStarted processing the asset df ...")

    # Convert 'media_type' to lowercase in the input_asset_df
    print("Updating the media_type")
    input_asset_df['media_type'] = input_asset_df['media_type'].str.lower()

    # Apply quote function to 'source' preserving certain characters
    print("Updating the source")
    input_asset_df['source'] = input_asset_df['source'].apply(lambda url: quote(url, safe='/:?=&%'))

    # Separate rows into 'asset_df' and 'main_image_df' based on 'is_main_image'
    print("Partitioning the asset and main image df")
    asset_df = input_asset_df[input_asset_df['is_main_image'] != 1]
    main_image_df = input_asset_df[input_asset_df['is_main_image'] == 1]

    # Define the columns to include in the json_container
    columns_to_include = ['name', 'source', 'sha256', 'type', 'media_type']

    # Group and aggregate rows into the first dictionary for 'asset_df'
    print("Generating the final asset df")
    asset_df_grouped = asset_df.groupby('hash_key')[columns_to_include].apply(
        lambda group: group.to_dict('records') if not group.empty else []).reset_index(name='json_container')

    # Group and aggregate rows into the first dictionary for 'main_image_df'
    print("Generating the final main image df")
    main_image_df_grouped = main_image_df.groupby('hash_key')[columns_to_include].apply(
        lambda group: group.to_dict('records')[0] if not group.empty else {}).reset_index(name='json_container')

    # Rename columns
    asset_df_grouped = asset_df_grouped.rename(
        columns={'hash_key': 'hash_key', 'json_container': 'assets'}
    )
    main_image_df_grouped = main_image_df_grouped.rename(
        columns={'hash_key': 'hash_key', 'json_container': 'main_image'}
    )

    print("Asset DF processed ...\n\n")

    del input_asset_df, main_image_df, asset_df
    gc.collect()

    return asset_df_grouped, main_image_df_grouped


def process_pricing_df(input_price_df):
    print("\n\nStarted Processing the price df")
    # Step 1: Fill NaN and 0 values in 'min_qty' with 1, set data type to integer, and replace 0 with 1
    input_price_df['min_qty'] = input_price_df['min_qty'].fillna(1).astype(int)
    input_price_df['min_qty'] = input_price_df['min_qty'].replace(0, 1)

    # Step 2: Drop duplicate rows based on all columns
    print("Dropping duplicates from df is any.")
    input_price_df = input_price_df.drop_duplicates()

    # Step 3: Generate 'price_df' with 'hash_key' and 'json_container' containing specific columns
    print("Generating the final structure of price df")
    columns_to_include = ['min_qty', 'price', 'currency', 'price_string']
    price_df = input_price_df.groupby('hash_key')[columns_to_include].apply(
        lambda group: group.to_dict('records') if not group.empty else []
    ).reset_index(name='json_container')

    # step 4: Fill NaN values in price_string with ""
    input_price_df['price_string'] = input_price_df['price_string'].fillna("")

    # Step 5: Modify dictionaries in 'json_container' based on 'price_string'
    def modify_dict(record):
        if record['price_string']:
            record.pop('price', None)
            record.pop('currency', None)
        else:
            record.pop('price_string', None)
        return record

    print("Filtering value of price and price-string ")
    price_df['json_container'] = price_df['json_container'].apply(lambda records: [modify_dict(d) for d in records])

    # Rename columns
    price_df = price_df.rename(
        columns={'hash_key': 'hash_key', 'json_container': 'price'}
    )

    del input_price_df
    gc.collect()

    print("Price DF processed ...\n\n")
    return price_df


# CREATING THE MYSQL OBJECT
con = pymysql.connect(host=db_host, user=db_user, password=db_password, db=db_name, port=3306)

print("READING THE PRICING TABLE", end="")
pricing_df = pd.read_sql(
    sql=(
        f"select `hash_key`, `sku`, `min_qty`, `price`, `price_string`, `currency` "
        f"from {pricing_table} where vendor_id = '{VENDOR_ID}'"
    ),
    con=con
)
# pricing_df = pd.read_json(location + "pricing_table.json", dtype={"hash_key": str, 'sku': str})
print("\rPRICING TABLE LOADED: ", len(pricing_df), " TOTAL ENTRIES")

print("READING THE ASSET TABLE", end="")
asset_df = pd.read_sql(
    sql=(
        f"select `hash_key`, `sku`, `name`, `source`, `sha256`, `type`, `media_type`, `length`, `file_name`, "
        f"`download_path`, `is_main_image` from {asset_table} where vendor_id = '{VENDOR_ID}' and status ='Done';"
    ),
    con=con
)
print("\rASSET TABLE LOADED: ", len(asset_df), " TOTAL ENTRIES")

print("READING THE PRODUCT TABLE", end="")
product_df = pd.read_sql(
    sql=(
        f"select `hash_key`, `vendor_name`, `sku`, `pdp_url`, `name`, `category`, `uom`, `sku_unit`, `sku_quantity`, "
        f"`quantity_increment`, `pack_label`, `available_to_checkout`, `in_stock`, `estimated_lead_time`, "
        f"`description`, `description_html`, `manufacturer`, `mpn`, `attributes`, `features`, `_scrape_metadata` "
        f"from {product_table} where vendor_id = '{VENDOR_ID}';"
    ),
    con=con
)
# product_df = pd.read_json(location + 'product_table_1.json', dtype={"hash_key": str, 'sku': str, 'mpn': str})
print("\rPRODUCTS TABLE LOADED: ", len(product_df), " TOTAL ENTRIES\n\n")

# PROCESSING THE PRICING TABLE
pricing_df = process_pricing_df(pricing_df)

# PROCESSING THE ASSET TABLE
asset_df = asset_df.drop_duplicates()
TOTAL_ASSETS = asset_df.length.count()
TOTAL_UNIQUE_ASSETS = len(asset_df.sha256.unique())
asset_df, main_image_df = process_asset_df(asset_df)

# MERGING THE ASSET DF WITH PRODUCT DF
print("ASSETS MAPPING PROCESS STARTING ...")
product_df = product_df.merge(asset_df[['hash_key', 'assets']], on='hash_key', how='left')
print("\nASSETS MAPPING PROCESS ENDS ...\n\n")

# MERGING THE MAIN IMAGE DF WITH PRODUCT DF
print("MAIN IMAGE MAPPING PROCESS STARTING ...")
product_df = product_df.merge(main_image_df[['hash_key', 'main_image']], on='hash_key', how='left')
print("\nMAIN IMAGE MAPPING PROCESS ENDS ...\n\n")

# MERGING THE PRICING DF WITH PRODUCT DF
print("PRICING MAPPING PROCESS STARTING ...")
product_df = product_df.merge(pricing_df[['hash_key', 'price']], on='hash_key', how='left')
print("\nPRICING MAPPING PROCESS ENDS ...\n\n")

# DELETING THE OBJECT THAT ARE NOT USEFUL TO BETTER MANGE MEMORY CONSUMPTION
del product_df['hash_key'], main_image_df, asset_df, pricing_df
gc.collect()

# FILLING THE NOT MATCHED VALUES WITH THE EMPTY LIST
print("\n\nPROCESSING THE EMPTY DATA FIELDS")
for i in ['assets', 'price']:
    product_df[i] = product_df[i].apply(lambda x: x if isinstance(x, list) else [])

# FILLING THE NOT MATCHED VALUES WITH THE EMPTY LIST AND CONVERTING IT AS OBJECT
for i in ['attributes', '_scrape_metadata', 'category', 'features']:
    try:
        product_df[i] = product_df[i].fillna("[]")
        product_df[i] = product_df[i].apply(json.loads)
    except Exception as e:
        print(e, i)

# CONVERTING THE 0s AND 1s TO BOOLEAN VALUES true AND false
for i in ['in_stock', 'available_to_checkout']:
    product_df[i] = product_df[i].astype(bool)

# ENSURING THE ALL THE URL FILED ARE AS PER URL FORMAT
print("\n\nPROCESSING THE URLS")
product_df['pdp_url'] = product_df['pdp_url'].apply(lambda x: quote(x, safe='/:?=&%'))
product_df["_scrape_metadata"] = product_df["_scrape_metadata"].apply(
    lambda x: {
        **x,
        "date_visited": x['date_visited'] if len(x['date_visited']) == 24 else x['date_visited'][:-1] + ":00.000Z",
        "breadcrumbs": [{**d, "url": quote(d["url"], safe='/:?=&%')} for d in x["breadcrumbs"]],
        "url": quote(x['url'], safe='/:?=&%')
    }
)

print("\n\nDROPPING DUPLICATES FROM FINAL DATAFRAME IF ANY ")
# GENERATING THE CATEGORY_1 AS STRING TO USE IT AS DEDUPLICATION PROCESS.
product_df['category_1'] = product_df.category.apply(str)

# DROPPING DUPLICATES BASED ON THE SKU, PDP, NAME AND CATEGORY
product_df = product_df.drop_duplicates(subset=['sku', 'pdp_url', 'name', 'category_1'])

# REMOVING THE CATEGORY_1 AS NOT REQUIRED IN OUTPUT FILE
del product_df['category_1']

# GENERATING THE JSON FILE
print("\n\nGENERATING THE FILES.")
product_df.to_json(file_name, orient="records")
print("\n\nFILE GENERATED SUCCESSFULLY")

# VALIDATION CODE.
validated = do_validation(file_name=file_name)

# EXCEL FILE SIZE, NUMBER OF ROWS IN A SINGLE FILE, MAX 1000000 (1M)
size = 200000

if validated:
    k = product_df.shape[0]
    for i in range(int(k / size) + 1):
        df = product_df[size * i:size * (i + 1)]
        writer = pd.ExcelWriter(
            f"{output_part_files}/{TODAY_DATE}_PART_{str(i + 1).zfill(3)}.xlsx",
            engine='xlsxwriter',
            engine_kwargs={'options': {'strings_to_urls': False}}
        )
        writer.book.use_zip64()
        df.to_excel(writer)
        writer.close()

    print("\n\nTOTAL PRODUCTS: ", len(product_df))
    print("TOTAL ASSETS COUNT: ", TOTAL_ASSETS)
    print("TOTAL UNIQUE ASSETS: ", TOTAL_UNIQUE_ASSETS)

print(time.time() - t1)