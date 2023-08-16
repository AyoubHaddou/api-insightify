import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.index import router as api_router
import sentry_sdk

sentry_sdk.init(
    dsn="https://db70b5214cb646951529ab4064f946bf@o4505717202747392.ingest.sentry.io/4505717204582400",
    traces_sample_rate=1.0,
)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)