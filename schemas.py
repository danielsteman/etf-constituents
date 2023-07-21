from pydantic import BaseModel
from typing import Optional


class FundHolding(BaseModel):
    fund_name: str
    ticker: str
    name: str
    sector: str
    instrument: str
    market_value: float
    weight: float
    nominal_value: float
    nominal: float
    cusip: Optional[str] = None
    isin: str
    sedol: Optional[str] = None
    currency: str
    exchange: str


class FundReference(BaseModel):
    name: str
    fund_manager: str
    url: str
