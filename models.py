from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

Base = declarative_base()


class FundHoldings(Base):
    __tablename__ = "fundholdings"

    id_ = Column(Integer, primary_key=True, index=True)
    fund_name = Column(Integer, ForeignKey("fundreference.id_"))
    ticker = Column(String(255))
    name = Column(String(255))
    sector = Column(String(255))
    instrument = Column(String(255))
    market_value: float
    weight: float
    nominal_value: float
    nominal: float
    isin = Column(String(255))
    currency = Column(String(255))
    exchange = Column(String(255))

    reference = relationship("FundReference", back_populates="holdings")


class FundReference(Base):
    __tablename__ = "fundreference"

    id_ = Column(Integer, primary_key=True, index=True)
    name = Column(String(255))
    fund_manager = Column(String(255))
    url = Column(String(255))

    holdings = relationship("FundHoldings", back_populates="reference")
