import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.database import init_db
from app.api.billionaires import router as billionaires_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="Greed Index API",
    description="Tracking and ranking the top 200 US billionaires by genuine charitable giving.",
    version="1.0.0",
    lifespan=lifespan,
)

# Allowed origins: localhost for dev, plus any explicit origins from FRONTEND_URL
# (comma-separated). Vercel preview/production *.vercel.app domains are matched
# via regex so deploys work without reconfiguring on every new preview URL.
_default_origins = ["http://localhost:3000", "http://localhost:3001"]
_env_origins = [o.strip() for o in os.getenv("FRONTEND_URL", "").split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_default_origins + _env_origins,
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(billionaires_router)


@app.get("/")
def root():
    return {
        "name": "Greed Index API",
        "description": "Holding America's billionaires publicly accountable.",
        "docs": "/docs",
    }
