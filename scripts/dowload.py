import sys
import os
import internetarchive as ia
import os
import itertools
import random
from pprint import pprint
from datetime import datetime
import concurrent.futures
import logging

OUT_DIR = "./out"
MAX_WORKERS = 30
QUERY_STRING = "collection:newspapers " "AND language:eng " "AND date:[1939 TO 1945] "


def download_item(identifier):

    filename = "{}.txt".format(identifier)
    filepath = out_dir + os.sep + filename
    if os.path.exists(filepath):
        return

    item = ia.get_item(identifier)

    logging.info("Downloading {} to {}".format(identifier, filepath))

    ocr_files = (file for file in item.get_files() if "DjVuTXT" in file.format)
    file = next(ocr_files, None)
    if not file:
        print("No OCR file for {}".format(identifier))

    success = file.download(filepath)
    if not success:
        return

    return item.identifier, item.metadata["date"]


def main(out_dir):
    items = ia.search_items(QUERY_STRING)
    # items = random.sample(list(items), 50)
    identifiers = (entry["identifier"] for entry in items)

    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        with open(out_dir + os.sep + "metadata.txt", "w") as fout:
            future_to_identifier = {
                executor.submit(download_item, identifier): identifier
                for identifier in identifiers
            }

            for future in concurrent.futures.as_completed(future_to_identifier):
                identifier = future_to_identifier[future]
                try:
                    ans = future.result()
                    if ans:
                        identifier, date = ans
                        print("{} is {}".format(identifier, date))
                        fout.writelines("{} {}\n".format(identifier, date))
                    else:
                        print("{} already downloaded.".format(identifier))
                except Exception as exc:
                    print("{} generated an exception: {}".format(identifier, exc))


if __name__ == "__main__":
    out_dir = OUT_DIR
    print(sys.argv)
    if len(sys.argv) == 2:
        out_dir = sys.argv[1]

    os.makedirs(out_dir, exist_ok=True)
    main(out_dir)
