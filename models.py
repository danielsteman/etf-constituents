from sqlalchemy import Column, Float, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class FundHolding(Base):
    __tablename__ = "fundholdings"

    id_ = Column(Integer, primary_key=True, index=True)
    fund_name = Column(Integer, ForeignKey("fundreference.id_"))
    ticker = Column(String(255))
    name = Column(String(255))
    sector = Column(String(255))
    instrument = Column(String(255))
    market_value = Column(Float)
    weight = Column(Float)
    nominal_value = Column(Float)
    nominal = Column(Float)
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

    holdings = relationship("FundHolding", back_populates="reference")
