import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

import models
import schemas
from enums import ETFManager
from scrapers import IsharesFundHoldingsScraper, IsharesFundsListScraper

load_dotenv()


def get_db() -> Session:
    db_url = os.environ["DATABASE_URL"]
    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)
    session = Session()
    return session


def load_holding(db: Session, holding: schemas.FundHolding) -> None:
    holding_db_obj = models.FundHolding(**holding)
    db.add(holding_db_obj)
    db.commit()


fund_list_scraper = IsharesFundsListScraper(
    "https://www.ishares.com/nl/professionele-belegger/nl/producten/etf-investments#/?productView=all&dataView=keyFactspageNumber=1",  # noqa: E501
    ETFManager.ISHARES,  # type: ignore
)

fund_list = fund_list_scraper.get_funds_list()

print(f"{len(fund_list)} ishares funds found.")

db = get_db()
for fund_ref in fund_list:
    print(f"Processing fund name: {fund_ref.name}.")
    print(f"Processing fund url: {fund_ref.url}.")

    holdings_scraper = IsharesFundHoldingsScraper(fund_ref.url, fund_ref.name)
    holdings = holdings_scraper.get_holdings()
#     for holding in holdings:
#         print(f"Processing holding: {holding.name}.")

#         load_holding(db, holding)

# url = "https://www.ishares.com/nl/professionele-belegger/nl/producten/239726/ishares-core-sp-500-etf"
# name = "sp500"

# dummy_url = "https://www.ishares.com/nl/professionele-belegger/nl/producten/239726/ishares-core-sp-500-etf/1497735778849.ajax?tab=all&fileType=json&asOfDate=20230718"

# holdings_scraper = IsharesFundHoldingsScraper(url, name)
# holdings_scraper.driver.get(url)
# holdings_scraper.driver.reject_cookies()
# # holdings_scraper.driver.continue_as_individual_investor()
# content_type = "application/json"
# pattern = r"^https:\/\/www\.ishares\.com\/nl\/professionele-belegger\/nl\/producten\/.*\/.*\/.*\.ajax\?tab=all&fileType=json&asOfDate=.*$"  # noqa: E501

# holdings_list = []

# import re

# print(re.match(pattern, dummy_url))

# for req in holdings_scraper.driver.requests:
#     if req.response:
#         if req.response.headers.get_content_type() == content_type and re.match(
#             pattern, req.url
#         ):
#             print("bingo")


# print(holdings_scraper.driver.driver.page_source)
