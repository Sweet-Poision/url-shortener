from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
import redis
import os

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
        "service" : "Python Ingestion",
        "redis_status": db_status,
    }


@app.post("/ingest")
def shorted_url(payload: UrlPayload):
    try:
        url_id = r.incr("global_url_counter")
        short_code = f"s{url_id}"

        r.set(short_code, payload.long_url)

        return {
            "short_code": short_code,
            "original_url": payload.long_url,
            "status": "Cached in Redis",
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
