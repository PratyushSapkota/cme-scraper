from database import TableRow, Database
from chromedriver import ChromeDriver
from datafile import log_json, read_json, log_failed, addToLogs
from utils import calculatePriceAverage
import json
import csv
import time
import random
import os
import traceback

databaseTable = "v2"
urlFile = "urls.json"

database = Database("database.db")


def alpha(product, chromeDriver: ChromeDriver):
    tableRow = TableRow(databaseTable)
    productDetails, price30Days, contractUnit = chromeDriver.fetchProductDetails(
        product["url"]
    )
    average_volume, average_oi = calculatePriceAverage(price30Days)
    tableRow.data["product"] = product["product"]
    tableRow.data["url"] = product["url"]
    tableRow.data["volume_30"] = average_volume
    tableRow.data["oi_30"] = average_oi
    tableRow.data["last"] = productDetails["last"]
    tableRow.data["ContractUnit"] = contractUnit
    tableRow.data["volume"] = product["volume"]
    tableRow.data["oi"] = product["oi"]
    database.insert_row(tableRow)


# def main():
#     urls = read_json("urls.json")
#     for rangeNum in range(0, 500, 100):
#         start = rangeNum
#         end = rangeNum + 100
#         alphaFail = 0
#         chromeDriver = ChromeDriver(headless=False)
#         addToLogs(f"Started range of {start} {end} \n \n")

#         for idx, product in enumerate(urls[start:end]):
#             print(idx)
#             try:
#                 alpha(product, chromeDriver)
#                 addToLogs(f"{idx} ✅")
#             except:
#                 print(f"fail: {alphaFail}")
#                 alphaFail += 1

#                 if alphaFail >= 5:
#                     time.sleep(2 * 60)
#                     alphaFail = 0

#                 try:
#                     chromeDriver.driver.refresh()
#                     alpha(product, chromeDriver)
#                 except:
#                     print("Final Fail")
#                     chromeDriver.screenshot(idx)
#                     addToLogs(f"{idx} ❌")
#                     log_failed(idx)

#         chromeDriver.shutdown()
#         addToLogs(f"Ended range of {start} {end} \n \n")


def main():
    urls = read_json("urls.json")
    for rangeNum in range(0, 500, 100):
        start = rangeNum
        end = rangeNum + 100
        alphaFail = 0
        chromeDriver = ChromeDriver(headless=False)
        addToLogs(f"Started range of {start} {end} \n \n")

        for idx, product in enumerate(urls[start:end]):
            print(f"Processing product {idx + start}")
            try:
                alpha(product, chromeDriver)
                addToLogs(f"{idx + start} ✅")  # Log success with correct index
            except Exception as e:
                print(f"Error processing {idx + start}: {e}")
                alphaFail += 1

                if alphaFail >= 5:
                    time.sleep(
                        2 * 60
                    )  # Wait for 2 minutes if 5 failures occur in a row
                    alphaFail = 0

                try:
                    chromeDriver.driver.refresh()
                    alpha(product, chromeDriver)  # Retry after refresh
                    addToLogs(f"{idx + start} ✅ (retry)")  # Log retry success
                except Exception as e:
                    print(f"Final Fail for {idx + start}: {e}")
                    chromeDriver.screenshot(idx)
                    addToLogs(f"{idx + start} ❌")  # Log failure
                    log_failed(idx)

        chromeDriver.shutdown()
        addToLogs(f"Ended range of {start} {end} \n \n")


main()
