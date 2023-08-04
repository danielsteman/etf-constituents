from typing import Optional

from pydantic import BaseModel


class FundHolding(BaseModel):
    fund_name: str
    ticker: Optional[str] = None
    issuer: Optional[str] = None
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
    country: str
    exchange: Optional[str] = None


class FundReference(BaseModel):
    name: str
    fund_manager: str
    url: str
