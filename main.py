from dataclasses import dataclass
from typing import Any, List
import httpx
import json

url = "https://www.ishares.com/nl/particuliere-belegger/nl/producten/251781/ishares-euro-stoxx-50-ucits-etf-inc-fund/1497735778849.ajax?tab=all&fileType=json"

res = httpx.get(url)
holdings = json.loads(res.content)["aaData"]


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


mapped_holdings = [IsharesFundHoldings(share) for share in holdings]

print(mapped_holdings)
