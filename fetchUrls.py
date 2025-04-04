from chromedriver import ChromeDriver
import json

chromeDriver = ChromeDriver(headless=True)

urls = chromeDriver.fetchMainTableData(
    tablePageUrl="https://www.cmegroup.com/markets/products.html#sortAsc&sortDirection=desc&sortField=vol"
)

with open("urls.json", "w") as f:
    json.dump(urls, f, indent=4)

chromeDriver.shutdown()
