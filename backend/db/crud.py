import datetime

from sqlalchemy.orm import Session
from sqlalchemy import desc, asc

from db import models, schemas

def get_stonks(db: Session):
    return db.query(models.Stonk).all()

def get_stonk(db: Session, stonk_id: int):
    return db.query(models.Stonk).filter(models.Stonk.id == stonk_id).first()

def get_stonk_by_name(db: Session, name: str):
    return db.query(models.Stonk).filter(models.Stonk.name == name).first()

def get_stonk_by_ticker(db: Session, ticker: str):
    return db.query(models.Stonk).filter(models.Stonk.ticker == ticker).first()

def create_stonk(db: Session, stonk: schemas.StonkCreate):
    db_stonk = models.Stonk(name=stonk.name, ticker=stonk.ticker)
    db.add(db_stonk)
    db.commit()
    db.refresh(db_stonk)
    return db_stonk


def get_stonk_current_price(db: Session, stonk_id: int):
    return db.query(models.Price).filter(models.Price.stonk_id == stonk_id).order_by(desc(models.Price.datetime)).limit(1).first()

def get_stonk_historical_prices(db: Session, stonk_id: int, start: datetime, end: datetime):
    return db.query(models.Price).filter(
        models.Price.stonk_id == stonk_id,
        models.Price.datetime.between(start, end)
    ).order_by(asc(models.Price.datetime)).all()


def create_price(db: Session, price: schemas.PriceCreate):
    db_price = models.Price(
        price=price.price,
        datetime=price.datetime,
        stonk_id=price.stonk_id
    )
    db.add(db_price)
    db.commit()
    db.refresh(db_price)
    return db_price