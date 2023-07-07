"""
Pass url to funds overview
Capture request for all funds
[done] Pass url to fund page
[done] Capture request for holdings
[done] Parse response body
[done] Load each fund into an object
"""

from typing import List, Any
import logging
import json
import re
import gzip
from seleniumwire import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def get_driver() -> webdriver.Chrome:
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    return webdriver.Chrome(chrome_options=chrome_options)


class IsharesFundsListScraper:
    def __init__(self, url: str) -> None:
        self.url = url
        self.driver = get_driver()

    def get_funds_list(self):
        return


class IsharesFundHoldings:
    def __init__(self, raw_data: List[Any]) -> None:
        self.ticker = raw_data[0]
        self.name = raw_data[1]
        self.sector = raw_data[2]
        self.instrument = raw_data[3]
        self.market_value = raw_data[4]["raw"]
        self.weight = raw_data[5]["raw"]
        self.nominal_value = raw_data[6]["raw"]
        self.isin = raw_data[7]
        self.currency = raw_data[12]
        self.exchange = raw_data[11]

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}({self.name}, {self.weight}, {self.instrument})"
        )


class IsharesFundScraper:
    """
    Example usage:

    scraper = IsharesFundScraper(
        "https://www.ishares.com/nl/particuliere-belegger/nl/producten/251781/ishares-euro-stoxx-50-ucits-etf-inc-fund"
    )
    scraper.get_holdings()
    >>>
    [IsharesFundHoldings(), IsharesFundHoldings(), ...]
    """

    def __init__(self, url: str) -> None:
        self.url = url
        self.driver = get_driver()
        print(type(self.driver))

    def get_holdings(self) -> List[IsharesFundHoldings]:
        self.driver.get(self.url)
        accept_button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    '//*[@id="onetrust-reject-all-handler"]',
                )
            )
        )
        accept_button.click()

        logging.info("Rejected cookies")

        continue_as_private_investor_button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    '//*[@id="direct-url-screen-{lang}"]/div/div[2]/div/a',
                )
            )
        )
        continue_as_private_investor_button.click()

        logging.info("Enter as private investor")

        content_type = "application/json"
        pattern = r"^https:\/\/www\.ishares\.com\/nl\/particuliere-belegger\/nl\/producten\/.*\/.*\/.*\.ajax\?tab=all&fileType=json&asOfDate=.*$"

        holdings_list = []

        for req in self.driver.requests:
            if req.response:
                if req.response.headers.get_content_type() == content_type and re.match(
                    pattern, req.url
                ):
                    compressed_data = req.response.body
                    decompressed_data = gzip.decompress(compressed_data)
                    decoded_string = decompressed_data.decode("utf-8-sig")
                    holdings_dicts = json.loads(decoded_string)["aaData"]

                    for holdings in holdings_dicts:
                        holdings_list.append(IsharesFundHoldings(holdings))

        return holdings_list


scraper = IsharesFundScraper(
    "https://www.ishares.com/nl/particuliere-belegger/nl/producten/251781/ishares-euro-stoxx-50-ucits-etf-inc-fund"
)
scraper.get_holdings()
