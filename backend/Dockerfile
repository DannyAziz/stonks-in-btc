FROM python:3.7

RUN apt-get update && apt-get install -y --no-install-recommends git libpq-dev gcc libzbar-dev python3-dev musl-dev

COPY requirements.txt .

RUN pip install -r requirements.txt