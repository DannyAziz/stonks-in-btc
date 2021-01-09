import datetime
import requests
import pickle
import os

import yfinance as yf

from db import crud, schemas, SessionLocal

COINDESK_HEADERS = {
    'authority': 'production.api.coindesk.com',
    'pragma': 'no-cache',
    'cache-control': 'no-cache',
    'accept': 'application/json, text/plain, */*',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36',
    'origin': 'https://www.coindesk.com',
    'sec-fetch-site': 'same-site',
    'sec-fetch-mode': 'cors',
    'sec-fetch-dest': 'empty',
    'referer': 'https://www.coindesk.com/',
    'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
}

def convert_usd_to_btc(usd_amount, rate):
    return float(usd_amount )/ float(rate)

def get_historical_stonk_price_in_usd(stonk: yf.Ticker, ticker: str):
    price_data = stonk.history(start='2013-10-01')
    return price_data

def get_stonk_price_since_date_in_usd(stonk: yf.Ticker, ticker: str, since_date: datetime.datetime):
    price_data = stonk.history(start=since_date.strftime('%Y-%m-%d'))
    return price_data

def get_stonk_data(ticker: str):
    stonk = yf.Ticker(ticker)

    historical_daily_prices = get_historical_stonk_price_in_usd(stonk, ticker)

    return {
        'name': stonk.info['longName'],
        'historical_daily_prices': historical_daily_prices,
    }

def get_current_bitcoin_price():
    datetime_now = datetime.datetime.now()
    datetime_hour_ago = datetime_now - datetime.timedelta(hours=1)
    url = f"https://production.api.coindesk.com/v2/price/values/BTC?start_date={datetime_hour_ago.strftime('%Y-%m-%dT%H:00')}&end_date={datetime_now.strftime('%Y-%m-%dT%H:00')}&ohlc=false"

    retries = 0
    max_retries = 3

    while retries != max_retries:
        try:
            response = requests.get(url, headers=COINDESK_HEADERS)
            if response.status_code != 200:
                raise Exception(f'Failed to fetch historical BTC prices, status code: {response.status_code}')
            break
        except Exception as e:
            print(e)
            retries += 1

    if response.status_code != 200:
        raise Exception(f'Failed to fetch historical BTC prices, status code: {response.status_code}')

    data = response.json()
    entries = data['data']['entries']
    current_price = entries[len(entries) - 1][1]
    
    return current_price

def get_bitcoin_price_on_day(day: datetime.datetime):
    day = day.replace(hour=0, minute=0, second=0)
    file_name = 'btc_price_dict.pkl'
    if not os.path.isfile(file_name):
        create_historical_btc_price_file()
    bitcoin_price_dict = pickle.load(open(file_name, 'rb'))
    return bitcoin_price_dict[day]


def bootstrap_new_stonk(ticker: str):
    db = SessionLocal()

    stonk_data = get_stonk_data(ticker)

    stonk_db_obj = crud.create_stonk(
        db=db,
        stonk=schemas.StonkCreate(
            name=stonk_data['name'],
            ticker=ticker
        )
    )

    for datestring in stonk_data['historical_daily_prices']['Close'].keys():
        # Coindesk is missing prices for some days, not a lot but a few - Right now it's not worth solving this so a few gaps is OK
        try:
            price_datetime = datestring.to_pydatetime()
            price_in_usd = stonk_data['historical_daily_prices']['Close'][datestring]
            price_in_btc = convert_usd_to_btc(
                price_in_usd,
                get_bitcoin_price_on_day(price_datetime)
            )
            print(f'Saving Price for {ticker} on {datestring} @ {str(price_in_btc)}')
            crud.create_price(
                db=db,
                price=schemas.PriceCreate(
                    price=price_in_btc,
                    datetime=price_datetime,
                    stonk_id=stonk_db_obj.id
                )
            )
        except Exception as e:
            print(e)

    # Converts all USD prices to BTC
    db.close()

def update_stonk(ticker: str):
    pass


def create_historical_btc_price_file():
    bulk_url = f"https://production.api.coindesk.com/v2/price/values/BTC?start_date=2010-07-17T23:00&end_date={datetime.datetime.now().strftime('%Y-%m-%dT%H:00')}&ohlc=false"

    response = requests.get(bulk_url, headers=COINDESK_HEADERS)

    if response.status_code != 200:
        raise Exception('Failed to get BTC data')

    entries = response.json()['data']['entries']

    btc_price_dict = {}

    for entry in entries:
        btc_price_dict[datetime.datetime.utcfromtimestamp(entry[0] / 1000).replace(hour=0, minute=0, second=0)] = entry[1]
    
    with open('btc_price_dict.pkl', 'wb') as outfile:
        pickle.dump(btc_price_dict, outfile)