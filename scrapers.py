"""
[done] Pass url to funds overview
[done] Scrape urls that lead to fund pages
[done] Pass url to fund page
[done] Capture request for holdings
[done] Parse response body
[done] Load each fund into an object

Issues:
scraper.get_holdings() sometimes returns an empty list
"""

import gzip
import json
import logging
import re
import time
from enum import Enum
from functools import wraps
from typing import List

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from seleniumwire import webdriver

from exceptions import (
    FundsNotScrapedException,
    HoldingsNotScrapedException,
    UnexpectedFundHoldingData,
)
from schemas import FundHolding, FundReference
import schemas


def retry_on_timeout(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        retries = 0
        while retries < self.max_retries:
            try:
                return func(self, *args, **kwargs)
            except TimeoutException:
                retries += 1
                print(f"Timeout occurred. Retrying ({retries}/{self.max_retries})")
                time.sleep(self.retry_delay)
        raise TimeoutError(f"Exceeded maximum retries ({self.max_retries})")

    return wrapper


class ETFManager(Enum):
    ISHARES = "ishares"


class Driver:
    def __init__(
        self, variant: ETFManager, *, max_retries: int = 3, retry_delay: int = 1
    ) -> None:
        self.variant = variant
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        self.driver = webdriver.Chrome(chrome_options=chrome_options)

    def __repr__(self) -> str:
        return f"Driver(variant={self.variant})"

    def get(self, url: str) -> None:
        self.driver.get(url)

    @property
    def requests(self):
        return self.driver.requests

    @retry_on_timeout
    def reject_cookies(self) -> None:
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

    @retry_on_timeout
    def continue_as_professional_investor(self) -> None:
        continue_button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    '//*[@id="direct-url-screen-{lang}"]/div/div[4]/div/a',
                )
            )
        )
        continue_button.click()
        logging.info("Enter as professional investor")

    @retry_on_timeout
    def continue_as_individual_investor(self) -> None:
        continue_button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, '//*[@id="direct-url-screen-{lang}"]/div/div[2]/div/a')
            )
        )
        continue_button.click()
        logging.info("Enter as individual investor")

    def get_elements(self, xpath: str):
        elements = WebDriverWait(self.driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, xpath))
        )
        return elements


class IsharesFundsListScraper:
    def __init__(self, url: str, fund_manager: ETFManager) -> None:
        self.url = url
        self.fund_manager = fund_manager
        self.driver = Driver(variant=fund_manager)

    def get_funds_list(self) -> List[FundReference]:
        self.driver.get(self.url)
        self.driver.reject_cookies()
        self.driver.continue_as_professional_investor()
        sections = self.driver.get_elements(
            '//*[@id="screener-funds"]/screener-cards/div/section[*]/div/div[1]/screener-fund-cell/a'  # noqa: E501
        )
        if not sections:
            raise FundsNotScrapedException("Sections have not been scraped")

        funds_list = []

        for section in sections:
            name = section.text
            href = section.get_attribute("href")
            if href:
                funds_list.append(
                    FundReference(
                        name=name, fund_manager=self.fund_manager.value, url=href
                    )
                )
            else:
                logging.warning(f"Found no href for {section.text}\n")

        return funds_list


class IsharesFundHoldingsScraper:
    """
    The IsharesFundHoldingsScraper intercepts a request that is made to the
    iShares backend to fetch fund holdings data when the fund page is loaded.
    The response body contains an object with a list of holdings under the key
    'aaData'. `FundHolding` is the corresponding schema.

    Example usage:

    scraper = IsharesFundScraper(
        "https://www.ishares.com/nl/professionele-belegger/nl/producten/251781/ishares-euro-stoxx-50-ucits-etf-inc-fund",
        "ishares-euro-stoxx-50-ucits-etf-inc-fund",
    )
    scraper.get_holdings()
    >>>
    [IsharesFundHolding(), IsharesFundHolding(), ...]
    """

    def __init__(self, url: str, fund_name: str) -> None:
        self.url = url
        self.fund_name = fund_name
        self.driver = Driver(variant=ETFManager.ISHARES)

    def map_to_schema(self, data: List):
        common_args = {
            "fund_name": self.fund_name,
            "ticker": data[0],
            "name": data[1],
            "sector": data[2],
            "instrument": data[3],
            "market_value": data[4]["raw"],
            "weight": data[5]["raw"],
            "nominal_value": data[6]["raw"],
            "nominal": data[7]["raw"],
        }
        if len(data) == 17:
            return schemas.FundHolding(
                **common_args,
                cusip=data[8],
                isin=data[9],
                sedol=data[10],
                exchange=data[13],
                currency=data[14],
            )
        elif len(data) == 14:
            return schemas.FundHolding(
                **common_args,
                isin=data[8],
                exchange=data[11],
                currency=data[12],
            )
        else:
            raise UnexpectedFundHoldingData(
                f"Data of lenght {len(data)} will probably not fit in the `FundHolding` schema."
            )

    def get_holdings(self) -> List[FundHolding]:
        self.driver.get(self.url)
        self.driver.reject_cookies()
        self.driver.continue_as_professional_investor()

        content_type = "application/json"
        pattern = r"^https:\/\/www\.ishares\.com\/nl\/professionele-belegger\/nl\/producten\/.*\/.*\/.*\.ajax\?tab=all&fileType=json&asOfDate=.*$"  # noqa: E501

        holdings_list = []

        for req in self.driver.requests:
            if req.response:
                if req.response.headers.get_content_type() == content_type and re.match(
                    pattern, req.url
                ):
                    compressed_data = req.response.body
                    decompressed_data = gzip.decompress(compressed_data)
                    decoded_string = decompressed_data.decode("utf-8-sig")

                    try:
                        holdings_dicts = json.loads(decoded_string)["aaData"]
                    except IndexError:
                        raise HoldingsNotScrapedException(
                            f"Holdings for {req.url} not found in response body."
                        )

                    for holdings in holdings_dicts:
                        holdings_list.append(self.map_to_schema(holdings))

        if not holdings_list:
            raise HoldingsNotScrapedException("Did not find requests to intercept.")

        return holdings_list
