from pydantic import BaseModel
from typing import Optional


class NorthAmericaFundingHolding(BaseModel):
    fund_name: str
    ticker: str
    name: str
    sector: str
    instrument: str
    market_value: float
    weight: float
    nominal_value: float
    nominal: float
    cusip: str
    isin: str
    sedol: str
    currency: str
    exchange: str


class FundHolding(BaseModel):  # soon deprecated
    fund_name: str
    ticker: str
    name: str
    sector: str
    instrument: str
    market_value: float
    weight: float
    nominal_value: float
    nominal: float
    isin: str
    currency: str
    exchange: str


class FundHolding_(BaseModel):
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
