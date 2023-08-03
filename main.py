import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.index import router as api_router
import sentry_sdk

sentry_sdk.init(
    dsn="https://0073014a6458f1c0f7f645c744404083@o4505619604635648.ingest.sentry.io/4505640867201024",
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