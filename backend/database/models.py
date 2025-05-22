from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
import enum

Base = declarative_base()

class Exchange(enum.Enum):
    NSE = "NSE"
    BSE = "BSE"
    NSDL = "NSDL"

class Bond(Base):
    __tablename__ = "bonds"

    id = Column(Integer, primary_key=True, index=True)
    isin = Column(String, unique=True, index=True)
    name = Column(String)
    issuer = Column(String)
    exchange = Column(Enum(Exchange))
    face_value = Column(Float)
    coupon_rate = Column(Float)
    maturity_date = Column(DateTime)
    yield_to_maturity = Column(Float)
    last_price = Column(Float)
    volume = Column(Integer)
    transactions = relationship("Transaction", back_populates="bond")

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    bond_id = Column(Integer, ForeignKey("bonds.id"))
    price = Column(Float)
    quantity = Column(Integer)
    timestamp = Column(DateTime)
    bond = relationship("Bond", back_populates="transactions") 