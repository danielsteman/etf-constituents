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

from seleniumwire import webdriver
from typing import List
import gzip
import json
import logging
import re

from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from schemas import FundHoldings, FundReference
from exceptions import FundsNotScrapedException, HoldingsNotScrapedException
from enums import ETFManager


class Driver:
    def __init__(self, variant: ETFManager) -> None:
        self.variant = variant
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
    Example usage:

    scraper = IsharesFundScraper(
        "https://www.ishares.com/nl/particuliere-belegger/nl/producten/251781/ishares-euro-stoxx-50-ucits-etf-inc-fund"
    )
    scraper.get_holdings()
    >>>
    [IsharesFundHoldings(), IsharesFundHoldings(), ...]
    """

    def __init__(self, url: str, fund_name: str) -> None:
        self.url = url
        self.fund_name = fund_name
        self.driver = Driver(variant=ETFManager.ISHARES)

    def get_holdings(self) -> List[FundHoldings]:
        self.driver.get(self.url)
        self.driver.reject_cookies()
        self.driver.continue_as_individual_investor()

        content_type = "application/json"
        pattern = r"^https:\/\/www\.ishares\.com\/nl\/particuliere-belegger\/nl\/producten\/.*\/.*\/.*\.ajax\?tab=all&fileType=json&asOfDate=.*$"  # noqa: E501

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
                            f"Holdings for {req.url} not found"
                        )

                    for holdings in holdings_dicts:
                        holdings_object = FundHoldings(
                            fund_name=self.fund_name,
                            ticker=holdings[0],
                            name=holdings[1],
                            sector=holdings[2],
                            instrument=holdings[3],
                            market_value=holdings[4]["raw"],
                            weight=holdings[5]["raw"],
                            nominal_value=holdings[6]["raw"],
                            nominal=holdings[7]["raw"],
                            isin=holdings[8],
                            currency=holdings[12],
                            exchange=holdings[11],
                        )

                        holdings_list.append(holdings_object)

        return holdings_list
