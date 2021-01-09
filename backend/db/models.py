from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float, DateTime
from sqlalchemy.orm import relationship

from db import Base


class Stonk(Base):
    __tablename__ = 'stonks'

    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String(), index=True)
    name = Column(String())

    prices = relationship('Price', back_populates='stonk')


class Price(Base):
    __tablename__ = 'prices'

    id = Column(Integer, primary_key=True, index=True)
    price = Column(Float)

    datetime = Column(DateTime, index=True)

    stonk_id = Column(Integer, ForeignKey('stonks.id'))

    stonk = relationship('Stonk', back_populates='prices')