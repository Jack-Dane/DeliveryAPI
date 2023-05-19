FROM python:3.10

COPY . /api
WORKDIR /api

RUN pip install -r requirements.txt

CMD uvicorn deliveryAPI.api.api:app --reload
