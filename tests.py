from enums import ETFManager
from scrapers import IsharesFundHoldingsScraper, IsharesFundsListScraper
import schemas
from typing import List


class TestIsharesFundsListScraper:
    def test_get_fund_list(self):
        fund_list_scraper = IsharesFundsListScraper(
            "https://www.ishares.com/nl/professionele-belegger/nl/producten/etf-investments#/?productView=all&dataView=keyFactspageNumber=1",  # noqa: E501
            ETFManager.ISHARES,  # type: ignore
        )
        fund_list = fund_list_scraper.get_funds_list()
        assert len(fund_list) > 0


class TestIsharesFundHoldingsScraper:
    def test_get_holdings_stoxx50(self):
        scraper = IsharesFundHoldingsScraper(
            "https://www.ishares.com/nl/professionele-belegger/nl/producten/251781/ishares-euro-stoxx-50-ucits-etf-inc-fund",  # noqa: E501
            "ishares-euro-stoxx-50-ucits-etf-inc-fund",
        )
        holdings = scraper.get_holdings()
        assert len(holdings) > 0

    def test_get_holdings_sp500(self):
        scraper = IsharesFundHoldingsScraper(
            "https://www.ishares.com/nl/professionele-belegger/nl/producten/239726/ishares-core-sp-500-etf",  # noqa: E501
            "iShares Core S&P 500 ETF IVV",
        )
        holdings = scraper.get_holdings()
        assert len(holdings) > 0


class TestFundHoldingSchemas:
    def test_north_america_funding_holding(self):
        us_stock = [
            "AAPL",
            "APPLE INC",
            "IT",
            "Aandelen",
            {"display": "USD 26.189.981.895", "raw": 26189981895.15},
            {"display": "7,51", "raw": 7.51473},
            {"display": "26.189.981.895,15", "raw": 26189981895.15},
            {"display": "135.188.055", "raw": 135188055},
            "037833100",
            "US0378331005",
            "2046251",
            {"display": "193,73", "raw": 193.73},
            "Verenigde Staten",
            "NASDAQ",
            "USD",
            "1,00",
            "-",
        ]

    def test_rest_of_world_fund_holding(self):
        nl_stock = [
            "ASML",
            "ASML HOLDING NV",
            "IT",
            "Aandelen",
            {"display": "EUR 262.906.424", "raw": 262906423.8},
            {"display": "8,51", "raw": 8.51186},
            {"display": "262.906.423,80", "raw": 262906423.8},
            {"display": "398.766", "raw": 398766},
            "NL0010273215",
            {"display": "659,30", "raw": 659.3},
            "Nederland",
            "Euronext Amsterdam",
            "EUR",
        ]

    def test_non_stock(self):
        non_stock = [
            "GBP",
            "GBP CASH",
            "Liquide middelen en/of derivaten",
            "Liquiditeiten",
            {"display": "EUR 129.522", "raw": 129522},
            {"display": "0,00", "raw": 0.00419},
            {"display": "129.522,00", "raw": 129522},
            {"display": "110.747", "raw": 110747},
            "-",
            {"display": "116,95", "raw": 116.95},
            "Verenigd Koninkrijk",
            "-",
            "GBP",
        ]
