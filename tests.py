from main import IsharesFundsListScraper, IsharesFundHoldingsScraper


class TestIsharesFundsListScraper:
    def test_get_fund_list(self):
        fund_list_scraper = IsharesFundsListScraper(
            "https://www.ishares.com/nl/professionele-belegger/nl/producten/etf-investments#/?productView=all&dataView=keyFactspageNumber=1"  # noqa: E501
        )
        fund_list = fund_list_scraper.get_funds_list()
        assert len(fund_list) > 0


class TestIsharesFundHoldingsScraper:
    def test_get_holdings(self):
        scraper = IsharesFundHoldingsScraper(
            "https://www.ishares.com/nl/particuliere-belegger/nl/producten/251781/ishares-euro-stoxx-50-ucits-etf-inc-fund"  # noqa: E501
        )
        holdings = scraper.get_holdings()
        assert len(holdings) > 0
