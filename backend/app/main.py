"""FastAPI entrypoint — Pharma Automation Hub (Tier 1 backend)."""
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from . import seed
from .routers import ai, auth, data, helpdesk, workflows

# Thư mục gốc dự án (nơi chứa index.html và 100.js)
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@asynccontextmanager
async def lifespan(app: FastAPI):
    seed.init_db()
    yield


app = FastAPI(title="Pharma Automation Hub API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(workflows.router)
app.include_router(data.router)
app.include_router(ai.router)
app.include_router(helpdesk.router)


@app.get("/api/v1/health")
def health():
    return {"status": "ok"}


@app.get("/", include_in_schema=False)
def index():
    return FileResponse(os.path.join(ROOT, "index.html"))


@app.get("/100.js", include_in_schema=False)
def intents_file():
    return FileResponse(os.path.join(ROOT, "100.js"))
