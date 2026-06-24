import argparse
import uvicorn
from fastapi import FastAPI
from src.api import api_router

app = FastAPI(title="bookings", description="Booking management service", version="0.1.0")
app.include_router(api_router)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8080, help="Port to run the server on")
    args = parser.parse_args()

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=args.port,
        log_level="debug",
        access_log=False,
    )
