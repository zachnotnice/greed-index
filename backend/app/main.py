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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
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
