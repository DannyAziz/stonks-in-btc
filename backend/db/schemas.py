import datetime

from typing import List, Optional

from pydantic import BaseModel


class StonkBase(BaseModel):
    ticker: str
    name: str


class StonkCreate(StonkBase):
    pass


class Stonk(StonkBase):
    id: int
    class Config:
        orm_mode = True


class PriceBase(BaseModel):
    price: float
    datetime: datetime.datetime
    stonk_id: int

class PriceCreate(PriceBase):
    pass

class Price(PriceBase):
    id: int
    class Config:
        orm_mode = True