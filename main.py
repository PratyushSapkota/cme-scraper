from database import TableRow, Database
from chromedriver import ChromeDriver
from datafile import log_json, read_json, addToLogs, json_report
from utils import calculatePriceAverage
import json
import csv
import time
import random
import os
import traceback


def alpha(product, chromeDriver: ChromeDriver, tableRow: TableRow):
    productDetails, price30Days, contractUnit = chromeDriver.fetchProductDetails(
        product["url"]
    )
    if productDetails is None or price30Days is None:
        raise RuntimeError("Failed to fetch product details or price data")
    
    average_volume, average_oi = calculatePriceAverage(price30Days)
    tableRow.data["product"] = product["product"]
    tableRow.data["url"] = product["url"]
    tableRow.data["volume_30"] = average_volume
    tableRow.data["oi_30"] = average_oi
    tableRow.data["last"] = productDetails["last"]
    tableRow.data["ContractUnit"] = contractUnit
    tableRow.data["volume"] = product["volume"]
    tableRow.data["oi"] = product["oi"]


def main():
    products = read_json("urls.json")
    tableName = read_json("database_settings.json")["tableName"]
    tableRow = TableRow(tableName)
    database = Database()

    for idx, product in enumerate(products):
        print(f"{idx} Processing")
        tableRow.clearRow()
        chromeDriver = ChromeDriver(headless=True)
        report = {"idx": idx, "url": product["url"], "success": "true"}
        try:
            alpha(product, chromeDriver, tableRow)
        except:
            print(f"{idx} Failed. Retrying")
            chromeDriver.shutdown()
            time.sleep(60)
            chromeDriver = ChromeDriver(headless=True)
            try:
                alpha(product, chromeDriver, tableRow)
            except:
                report["success"] = "false"
                print(f"{idx} Failed Completely")
        finally:
            if report["success"] == "true":
                print(f"{idx} Adding to database")
                database.insert_row(tableRow)

            chromeDriver.shutdown()
            json_report(report)
            time.sleep(2 * 60)

    database.close()


main()
