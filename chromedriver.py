from selenium.webdriver.chrome.options import Options
import gzip
import io
import time

# from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from seleniumwire import webdriver
import json
from pathlib import Path
from datetime import datetime


class ChromeDriver:

    def __init__(self, headless: bool = False, waitTime=10):
        options = Options()
        options.add_experimental_option("detach", True)
        options.add_argument("--disable-logging")
        options.add_argument("--log-level=3")
        if headless:
            options.add_argument("--headless=new")
        # options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-images")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument(
            "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
        )
        options.add_argument("--window-size=1920,1080")
        capabilities = DesiredCapabilities.CHROME.copy()
        capabilities["goog:loggingPrefs"] = {"performance": "ALL"}

        options.set_capability("goog:loggingPrefs", capabilities["goog:loggingPrefs"])

        # Initialize the driver with selenium-wire options
        self.driver = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, waitTime)
        if not headless:
            self.driver.maximize_window()

    def shutdown(self):
        self.driver.quit()

    def fetchMainTableData(self, tablePageUrl):
        self.driver.get(tablePageUrl)
        tableElement = self.wait.until(
            EC.presence_of_element_located(
                (
                    By.CSS_SELECTOR,
                    "div.main-table-wrapper table.product-slate-table-desktop.product-slate-table",
                )
            )
        )

        tr_elements = tableElement.find_elements(By.TAG_NAME, "tr")
        data = []

        for tr_element in tr_elements:
            td_elements = tr_element.find_elements(By.TAG_NAME, "td")

            if not td_elements:
                continue

            td_element_data = {}

            td_element_data["url"] = (
                td_elements[0].find_element(By.TAG_NAME, "a").get_attribute("href")
            )
            td_element_data["product"] = td_elements[0].text
            td_element_data["oi"] = td_elements[-1].text
            td_element_data["volume"] = td_elements[-2].text

            data.append(td_element_data)

        return data

    # def fetchProductDetails(self, productUrl):
    #     # Track requests before first get
    #     initial_request_count = len(self.driver.requests)
    #     self.driver.get(productUrl)

    #     productDetails_target_url_part = "CmeWS/mvc/quotes/v2/contracts-by-number"

    #     voi_button_element = self.wait.until(
    #         EC.presence_of_element_located(
    #             (By.CSS_SELECTOR, 'div.menu-item[data-key="volume"] > a')
    #         )
    #     )

    #     specsTables = self.driver.find_element(
    #         By.CSS_SELECTOR, "div.col table.contract-specs-table"
    #     )

    #     if not specsTables:
    #         print("SPECS TABLE NOT FOUND")
    #         contractUnit = None
    #     else:
    #         contractUnit = specsTables.find_element(By.CSS_SELECTOR, "td > div").text

    #     # Get only new requests for product details
    #     new_requests = self.driver.requests[initial_request_count:]
    #     productDetails = None

    #     for request in new_requests:
    #         if productDetails_target_url_part in request.url and request.response:
    #             with gzip.GzipFile(fileobj=io.BytesIO(request.response.body)) as f:
    #                 response_body = f.read().decode("utf-8")
    #             productDetails = json.loads(response_body)
    #             break  # stop once found

    #     # Track new request count for VOI
    #     initial_request_count = len(self.driver.requests)
    #     voi_url = voi_button_element.get_attribute("href")
    #     self.driver.get(voi_url)

    #     voi_target_url_part = "CmeWS/mvc/Volume/LastTotals"
    #     new_requests = self.driver.requests[initial_request_count:]
    #     price30Days = None

    #     for request in new_requests:
    #         if voi_target_url_part in request.url and request.response:
    #             with gzip.GzipFile(fileobj=io.BytesIO(request.response.body)) as f:
    #                 response_body = f.read().decode("utf-8")
    #             price30Days = json.loads(response_body)
    #             break  # stop once found

    #     return productDetails[0], price30Days, contractUnit

    def fetchProductDetails(self, productUrl):
        initial_request_count = len(self.driver.requests)
        self.driver.get(productUrl)

        productDetails_target_url_part = "CmeWS/mvc/quotes/v2/contracts-by-number"

        specsTables = self.wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "div.col table.contract-specs-table")
            )
        )

        voi_button_element = self.driver.find_element(
            By.CSS_SELECTOR, 'div.menu-item[data-key="volume"] > a'
        )

        if not specsTables:
            print("SPECS TABLE NOT FOUND")
            contractUnit = None
        else:
            contractUnit = specsTables.find_element(By.CSS_SELECTOR, "td > div").text

        # Get only new requests for product details
        new_requests = self.driver.requests[initial_request_count:]
        productDetails = None

        # Time measurement for first loop
        for request in new_requests:
            if productDetails_target_url_part in request.url and request.response:
                with gzip.GzipFile(fileobj=io.BytesIO(request.response.body)) as f:
                    response_body = f.read().decode("utf-8")
                productDetails = json.loads(response_body)
                break

        # Track new request count for VOI
        initial_request_count = len(self.driver.requests)
        voi_url = voi_button_element.get_attribute("href")
        
        time.sleep(30)
        self.driver.get(voi_url)

        voi_target_url_part = "CmeWS/mvc/Volume/LastTotals"
        new_requests = self.driver.requests[initial_request_count:]
        price30Days = None

        for request in new_requests:
            if voi_target_url_part in request.url and request.response:
                with gzip.GzipFile(fileobj=io.BytesIO(request.response.body)) as f:
                    response_body = f.read().decode("utf-8")
                price30Days = json.loads(response_body)
                break

        
        return productDetails[0], price30Days, contractUnit

    def screenshot(self, idx):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        filename = Path("screenshots") / f"{idx}_{timestamp}.png"
        self.driver.save_screenshot(filename)
