import json
import os
import time

import redis
from confluent_kafka import Producer
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

KAFKA_CONF = {
    "bootstrap.servers": os.getenv("KAFKA_HOST", "localhost:29092"),
}

producer = Producer(KAFKA_CONF)

app = FastAPI()

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))


try:
    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
except Exception as e:
    print(f"Error connection to Redis", {e})


class UrlPayload(BaseModel):
    long_url: str


@app.get("/")
def health_check():
    try:
        r.ping()
        db_status = "Connected"
    except:
        db_status = "Disconnected"

    return {
        "service": "Python Ingestion",
        "redis_status": db_status,
    }


@app.post("/ingest")
def shorted_url(payload: UrlPayload):
    try:
        url_id = r.incr("global_url_counter")
        short_code = f"s{url_id}"

        r.set(short_code, payload.long_url)

        event = {
            "id": url_id,
            "short_url": short_code,
            "long_url": payload.long_url,
            "created_at": time.time(),
        }

        producer.produce(
            "url_events",
            key=short_code,
            value=json.dumps(event),
        )
        producer.poll(0)

        return {
            "short_code": short_code,
            "status": "In Queue",
        }
    except Exception as e:
        return {"error": str(e)}
