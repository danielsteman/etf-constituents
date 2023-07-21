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

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from seleniumwire import webdriver

import schemas
from exceptions import (
    FundsNotScrapedException,
    HoldingsNotScrapedException,
    UnsupportedFundHoldingData,
)
from schemas import FundHolding, FundReference


def retry(func):
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
            except HoldingsNotScrapedException:
                retries += 1
                print(
                    f"Failed to extract holdings. Retrying\
                    ({retries}/{self.max_retries})"
                )
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

    def wait(self, seconds: int) -> None:
        time.sleep(seconds)

    @property
    def requests(self):
        return self.driver.requests

    @retry
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

    @retry
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
        logging.info("Enter as professional investor.")

    @retry
    def continue_as_individual_investor(self) -> None:
        continue_button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, '//*[@id="direct-url-screen-{lang}"]/div/div[2]/div/a')
            )
        )
        continue_button.click()
        logging.info("Enter as individual investor.")

    def get_elements(self, xpath: str):
        elements = WebDriverWait(self.driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, xpath))
        )
        return elements

    def show_all_positions(self) -> None:
        try:
            xpath = "/html/body/div[1]/div[2]/div/div/div/div/div/div[13]/div/div/div/div[1]/ul/li[2]/a"  # noqa: E501
            element = self.driver.find_element(By.XPATH, xpath)
            element.click()
            print("Showing all positions tab.")
        except NoSuchElementException:
            print("All positions tab is already active.")


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
            raise FundsNotScrapedException("Sections have not been scraped.")

        funds_list = []

        for section in sections:
            name = section.text
            href = section.get_attribute("href")
            if href:
                funds_list.append(
                    FundReference(
                        name=name,
                        fund_manager=self.fund_manager.value,
                        url=href,
                    )
                )
            else:
                logging.warning(f"Found no href for {section.text}.\n")

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

    def __init__(
        self, fund_ref: FundReference, *, max_retries: int = 3, retry_delay: int = 1
    ) -> None:
        self.fund_ref = fund_ref
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.driver = Driver(variant=ETFManager.ISHARES)

    @staticmethod
    def map_to_schema(fund_name, data: List):
        if len(data) == 17:
            return schemas.FundHolding(
                fund_name=fund_name,
                ticker=data[0],
                name=data[1],
                sector=data[2],
                instrument=data[3],
                market_value=data[4]["raw"],
                weight=data[5]["raw"],
                nominal_value=data[6]["raw"],
                nominal=data[7]["raw"],
                cusip=data[8],
                isin=data[9],
                sedol=data[10],
                country=data[12],
                exchange=data[13],
                currency=data[14],
            )
        elif len(data) == 13:
            return schemas.FundHolding(
                fund_name=fund_name,
                ticker=data[0],
                name=data[1],
                sector=data[2],
                instrument=data[3],
                market_value=data[4]["raw"],
                weight=data[5]["raw"],
                nominal_value=data[6]["raw"],
                nominal=data[7]["raw"],
                isin=data[8],
                country=data[10],
                exchange=data[11],
                currency=data[12],
            )
        elif len(data) == 26:
            return schemas.FundHolding(
                fund_name=fund_name,
                name=data[0],
                sector=data[1],
                instrument=data[2],
                market_value=data[3]["raw"],
                weight=data[4]["raw"],
                nominal_value=data[5]["raw"],
                nominal=data[6]["raw"],
                cusip=data[7],
                isin=data[8],
                sedol=data[9],
                country=data[10],
                currency=data[12],
            )
        else:
            raise UnsupportedFundHoldingData(
                f"Data of length {len(data)} will probably not fit in the `FundHolding`\
                schema."
            )

    def should_be_intercepted(self, url: str) -> bool:
        pattern = r"^https:\/\/www\.ishares\.com\/nl\/professionele-belegger\/nl\/producten\/.*\/.*\/.*\.ajax\?tab=all&fileType=json&asOfDate=.*$"  # noqa: E501
        match = re.match(pattern, url)
        if match:
            return True
        return False

    @retry
    def get_holdings(self) -> List[FundHolding]:
        self.driver.get(self.fund_ref.url)
        self.driver.reject_cookies()
        self.driver.continue_as_professional_investor()
        self.driver.show_all_positions()

        content_type = "application/json"

        holdings_list = []

        self.driver.wait(3)  # wait for page to be fully loaded

        for req in self.driver.requests:
            if req.response:
                if (
                    req.response.headers.get_content_type() == content_type
                    and self.should_be_intercepted(req.url)
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
                        holding_obj = IsharesFundHoldingsScraper.map_to_schema(
                            self.fund_ref.name, holdings
                        )
                        holdings_list.append(holding_obj)

        if not holdings_list:
            raise HoldingsNotScrapedException("Did not find requests to intercept.")

        return holdings_list
