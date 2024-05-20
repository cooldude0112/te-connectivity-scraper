import threading

import json
from threading import Thread

from jsonschema.validators import validate

error_flag = threading.Event()

json_schema = json.loads(open('ScrapeVendorProduct.schema.json', "rb").read())

error_list = list()


def do_validation(file_name):
    print("File Validation started ....")
    data = json.loads(open(file_name, "rb").read())
    for index in range(0, len(data), 1000):
        tt = list()

        end_iterators = index + 1000
        if end_iterators > len(data):
            end_iterators = len(data)

        for i in range(index, end_iterators):
            tt.append(Thread(target=compare_the_row, args=[data[i], i]))

        for t in tt:
            t.start()

        for t in tt:
            t.join()

        # Check the error flag
        if error_flag.is_set():
            print("An error occurred in at least one thread.")

            open("validation_error.json", "w").write(json.dumps(error_list))
            for key, values in error_list[0].items():
                if 'json' in key:
                    values = json.dumps(values)
                print(key, ": ", values)
            print(error_list)
            exit(-1)
            return False

    print("File Validated ....")
    return True

def compare_the_row(row, index):
    try:
        print("processing ...", index)
        validate(
            instance=row,
            schema=json_schema
            # schema=json.loads(open('new_schema.json', "rb").read())
        )
        return True
    except Exception as e:
        error_flag.set()
        error_list.append({
            "index": index,
            "sku": row['sku'],
            "error": str(e),
            "json": row,
        })
        print(e)
        print(json.dumps(object))
        exit(-1)

if __name__ == '__main__':
    input_file = r"Data.json"
    do_validation(input_file)