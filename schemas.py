from pydantic import BaseModel


class FundHoldings(BaseModel):
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


class FundReference(BaseModel):
    name: str
    url: str
