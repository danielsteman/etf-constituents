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
    print(f"Processing fund {fund_ref.name}.")

    holdings_scraper = IsharesFundHoldingsScraper(fund_ref.url, fund_ref.name)
    holdings = holdings_scraper.get_holdings()
    for holding in holdings:
        print(f"Processing holding {holding.name}.")

        load_holding(db, holding)
