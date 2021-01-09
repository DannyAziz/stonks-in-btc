import datetime

from db import crud, models, schemas, SessionLocal, engine

def run():
    db = SessionLocal()
    stonk = crud.create_stonk(
        db=db,
        stonk=schemas.StonkCreate(
            name='STONK',
            ticker='STONK'
        )
    )
    crud.create_price(
        db=db,
        price=schemas.PriceCreate(
            price=420.69,
            datetime=datetime.datetime.now(),
            stonk_id=stonk.id
        )
    )
    db.close()

def teardown():
    db = SessionLocal()
    db.query(models.Price).delete()
    db.query(models.Stonk).delete()
    db.commit()
    db.close()