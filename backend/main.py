import datetime

from typing import List

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from db import crud, models, schemas, SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

origins = [
    "http://localhost:8000",
    "http://localhost:3000",
    "https://stonksinbtc.xyz",
    "https://api.stonksinbtc.xyz"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



@app.get("/stonks/", response_model=List[schemas.Stonk])
def list_stonks(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    stonks = crud.get_stonks(db)
    return stonks

@app.get("/stonks/{stonk_id}", response_model=schemas.Stonk)
def get_stonk(stonk_id: int, db: Session = Depends(get_db)):
    stonk = crud.get_stonk(db, stonk_id)
    return stonk


@app.get("/stonks/{stonk_id}/price", response_model=schemas.Price)
def get_stonk_current_price(stonk_id: int, db: Session = Depends(get_db)):
    price = crud.get_stonk_current_price(db, stonk_id)
    return price

@app.get("/stonks/{stonk_id}/prices", response_model=List[schemas.Price])
def get_stonk_historical_prices(start: str, end: str, stonk_id: int, db: Session = Depends(get_db)):
    prices = crud.get_stonk_historical_prices(
        db,
        stonk_id,
        datetime.datetime.strptime(start, '%Y-%m-%d').replace(hour=0, minute=0, second=0),
        datetime.datetime.strptime(end, '%Y-%m-%d').replace(hour=0, minute=0, second=0)
    )
    return prices