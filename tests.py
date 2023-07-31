import pytest

from enums import ETFManager
from exceptions import HoldingsNotScrapedException
from schemas import FundHolding, FundReference
from scrapers import IsharesFundHoldingsScraper, IsharesFundsListScraper, PaginatedUrl


class TestIsharesFundsListScraper:
    def test_get_funds(self):
        fund_list_scraper = IsharesFundsListScraper(
            "https://www.ishares.com/nl/professionele-belegger/nl/producten/etf-investments#/?productView=all&dataView=keyFacts&pageNumber=1",
            ETFManager.ISHARES,
        )
        fund_list = fund_list_scraper._get_funds(
            "https://www.ishares.com/nl/professionele-belegger/nl/producten/etf-investments#/?productView=all&dataView=keyFacts&pageNumber=1"
        )
        assert len(fund_list) > 0

    def test_page_by_query_param(self):
        fund_list_scraper = IsharesFundsListScraper(
            "https://www.ishares.com/nl/professionele-belegger/nl/producten/etf-investments#/?productView=all&dataView=keyFacts&pageNumber=1",
            ETFManager.ISHARES,
        )

        fund_list_page_1 = fund_list_scraper._get_funds(
            "https://www.ishares.com/nl/professionele-belegger/nl/producten/etf-investments#/?productView=all&dataView=keyFacts&pageNumber=1"
        )
        fund_list_page_1_names = [x.name for x in fund_list_page_1]

        fund_list_page_2 = fund_list_scraper._get_funds(
            "https://www.ishares.com/nl/professionele-belegger/nl/producten/etf-investments#/?productView=all&dataView=keyFacts&pageNumber=2",
            continue_session=True,
        )
        fund_list_page_2_names = [x.name for x in fund_list_page_2]

        assert fund_list_page_1_names != fund_list_page_2_names

    def test_get_all_funds(self):
        fund_list_scraper = IsharesFundsListScraper(
            "https://www.ishares.com/nl/professionele-belegger/nl/producten/etf-investments#/?productView=all&dataView=keyFacts&pageNumber=1",
            ETFManager.ISHARES,
        )
        fund_list = fund_list_scraper.get_all_funds()
        assert len(fund_list) > 0


class TestIsharesFundHoldingsScraper:
    def test_intercept_request_regex(self):
        urls = [
            "https://www.ishares.com/nl/professionele-belegger/nl/producten/239726/ishares-core-sp-500-etf/1497735778849.ajax?tab=all&fileType=json&asOfDate=20230719",
            "https://www.ishares.com/nl/professionele-belegger/nl/producten/251781/ishares-euro-stoxx-50-ucits-etf-inc-fund/1497735778849.ajax?tab=all&fileType=json&asOfDate=20230719",
            "https://www.ishares.com/nl/professionele-belegger/nl/producten/239458/ishares-core-total-us-bond-market-etf/1497735778849.ajax?tab=all&fileType=json&asOfDate=20230720",
        ]
        fund_ref = FundReference(
            name="ishares-euro-stoxx-50-ucits-etf-inc-fund",
            fund_manager="ishares",
            url="https://www.ishares.com/nl/professionele-belegger/nl/producten/251781/ishares-euro-stoxx-50-ucits-etf-inc-fund",  # noqa: E501
        )
        scraper = IsharesFundHoldingsScraper(fund_ref)
        for url in urls:
            assert scraper.should_be_intercepted(url)

    def test_get_positions_table_headers(self):
        fund_ref = FundReference(
            name="ishares-euro-stoxx-50-ucits-etf-inc-fund",
            fund_manager="ishares",
            url="https://www.ishares.com/nl/professionele-belegger/nl/producten/251781/ishares-euro-stoxx-50-ucits-etf-inc-fund",  # noqa: E501
        )
        scraper = IsharesFundHoldingsScraper(fund_ref)
        scraper.driver.get(fund_ref.url)
        scraper.driver.reject_cookies()
        scraper.driver.continue_as_professional_investor()
        scraper.driver.show_all_positions()
        headers = scraper.driver.get_positions_table_headers()
        if not headers:
            pytest.fail("No headers were found")
        assert headers == [
            "Beurscode",
            "emittent",
            "Naam",
            "Sector",
            "Beleggingscategorie",
            "Marktwaarde",
            "Weging",
            "(%)",
            "Nominale",
            "waarde",
            "Nominaal",
            "ISIN",
            "Beursvaluta",
        ]

    def test_get_holdings_stoxx50(self):
        fund_ref = FundReference(
            name="ishares-euro-stoxx-50-ucits-etf-inc-fund",
            fund_manager="ishares",
            url="https://www.ishares.com/nl/professionele-belegger/nl/producten/251781/ishares-euro-stoxx-50-ucits-etf-inc-fund",  # noqa: E501
        )
        scraper = IsharesFundHoldingsScraper(fund_ref)
        holdings = scraper.get_holdings()
        assert len(holdings) > 0

    def test_get_holdings_sp500(self):
        fund_ref = FundReference(
            name="iShares Core S&P 500 ETF IVV",
            fund_manager="ishares",
            url="https://www.ishares.com/nl/professionele-belegger/nl/producten/239726/ishares-core-sp-500-etf",  # noqa: E501
        )
        scraper = IsharesFundHoldingsScraper(fund_ref)
        holdings = scraper.get_holdings()
        assert len(holdings) > 0

    def test_get_holdings_aggregate_bond(self):
        fund_ref = FundReference(
            name="iShares Core U.S. Aggregate Bond ETF",
            fund_manager="ishares",
            url="https://www.ishares.com/nl/professionele-belegger/nl/producten/239458/ishares-core-total-us-bond-market-etf",  # noqa: E501
        )
        scraper = IsharesFundHoldingsScraper(fund_ref, max_retries=1)
        holdings = scraper.get_holdings()
        assert len(holdings) > 0

    def test_skip_fund_without_holdings(self):
        fund_ref = FundReference(
            name="iShares Developed World Index Fund (IE)",
            fund_manager="ishares",
            url="https://www.ishares.com/nl/professionele-belegger/nl/producten/228471/blackrock-blk-developed-world-index-flex-acc-eur-fund",  # noqa: E501
        )
        scraper = IsharesFundHoldingsScraper(
            fund_ref, skip_empty_funds=True, max_retries=1
        )
        try:
            holdings = scraper.get_holdings()
            assert not holdings
        except HoldingsNotScrapedException:
            pytest.fail("Failed to skip fund without holdings.")


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
        holdings = IsharesFundHoldingsScraper.map_to_schema(
            "random_fund_name", us_stock
        )
        assert holdings == FundHolding(
            fund_name="random_fund_name",
            ticker="AAPL",
            name="APPLE INC",
            sector="IT",
            instrument="Aandelen",
            market_value=26189981895.15,
            weight=7.51473,
            nominal_value=26189981895.15,
            nominal=135188055,
            cusip="037833100",
            isin="US0378331005",
            sedol="2046251",
            currency="USD",
            country="Verenigde Staten",
            exchange="NASDAQ",
        )

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
        holdings = IsharesFundHoldingsScraper.map_to_schema(
            "random_fund_name", nl_stock
        )
        assert holdings == FundHolding(
            fund_name="random_fund_name",
            ticker="ASML",
            name="ASML HOLDING NV",
            sector="IT",
            instrument="Aandelen",
            market_value=262906423.8,
            weight=8.51186,
            nominal_value=262906423.8,
            nominal=398766,
            isin="NL0010273215",
            currency="EUR",
            country="Nederland",
            exchange="Euronext Amsterdam",
        )

    def test_non_stock_holding(self):
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
        holdings = IsharesFundHoldingsScraper.map_to_schema(
            "random_fund_name", non_stock
        )
        assert holdings == FundHolding(
            fund_name="random_fund_name",
            ticker="GBP",
            name="GBP CASH",
            sector="Liquide middelen en/of derivaten",
            instrument="Liquiditeiten",
            market_value=129522,
            weight=0.00419,
            nominal_value=129522,
            nominal=110747,
            isin="-",
            currency="GBP",
            exchange="-",
            country="Verenigd Koninkrijk",
        )

    def test_bond_holding(self):
        bond = [
            "BLACKROCK CASH CL INST SL AGENCY",
            "Liquide middelen en/of derivaten",
            "Money Market",
            {"display": "USD 4.392.919.230", "raw": 4392919229.69},
            {"display": "4,69", "raw": 4.68829},
            {"display": "4.392.919.229,69", "raw": 4392919229.69},
            {"display": "4.391.601.749,00", "raw": 4391601749},
            "066922519",
            "US0669225197",
            "BKGRT85",
            "Verenigde Staten",
            "-",
            "USD",
            {"display": "0,06", "raw": 0.06},
            {"display": "5,16", "raw": 5.16},
            "1,00",
            {"display": "-", "raw": ""},
            {"display": "5,28", "raw": 5.28},
            "0,19",
            {"display": "-", "raw": ""},
            {"display": "5,16", "raw": 5.16},
            "0,18",
            "5,16",
            "USD",
            "-",
            "04/feb/2009",
        ]
        holdings = IsharesFundHoldingsScraper.map_to_schema("random_fund_name", bond)
        assert holdings == FundHolding(
            fund_name="random_fund_name",
            name="BLACKROCK CASH CL INST SL AGENCY",
            sector="Liquide middelen en/of derivaten",
            instrument="Money Market",
            market_value=4392919229.69,
            weight=4.68829,
            nominal_value=4392919229.69,
            nominal=4391601749,
            cusip="066922519",
            isin="US0669225197",
            sedol="BKGRT85",
            currency="USD",
            country="Verenigde Staten",
        )


class TestPaginatedUrl:
    def test_paginated_url(self):
        expected_urls = [
            "https://www.ishares.com/nl/professionele-belegger/nl/producten/etf-investments#/?productView=all&dataView=keyFacts&pageNumber=1",
            "https://www.ishares.com/nl/professionele-belegger/nl/producten/etf-investments#/?productView=all&dataView=keyFacts&pageNumber=2",
            "https://www.ishares.com/nl/professionele-belegger/nl/producten/etf-investments#/?productView=all&dataView=keyFacts&pageNumber=3",
            "https://www.ishares.com/nl/professionele-belegger/nl/producten/etf-investments#/?productView=all&dataView=keyFacts&pageNumber=4",
            "https://www.ishares.com/nl/professionele-belegger/nl/producten/etf-investments#/?productView=all&dataView=keyFacts&pageNumber=5",
        ]
        urls = PaginatedUrl(
            "https://www.ishares.com/nl/professionele-belegger/nl/producten/etf-investments#/?productView=all&dataView=keyFacts&pageNumber=1",
            r"(?<=pageNumber=)(\d+)",
        )
        generated_urls = []
        count = 0
        for url in urls:
            if count == 5:
                break
            generated_urls.append(url)
            count += 1
        assert expected_urls == generated_urls
