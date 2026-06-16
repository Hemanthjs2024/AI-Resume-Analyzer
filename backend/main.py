import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import analyse, generate, roadmap, chat

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger("resume-agent")

OUTPUT_DIR = Path(__file__).parent / "outputs"


@asynccontextmanager
async def lifespan(app: FastAPI):
    OUTPUT_DIR.mkdir(exist_ok=True)
    logger.info("Output directory ready at %s", OUTPUT_DIR)
    yield
    logger.info("Shutting down.")


app = FastAPI(
    title="AI Career Alignment Agent",
    description="Intelligent resume analysis, skill gap detection, and career roadmap engine.",
    version="1.0.0",
    lifespan=lifespan,
)

ALLOWED_ORIGINS = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:5173,http://localhost:3000",
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analyse.router, prefix="/api", tags=["Analysis"])
app.include_router(generate.router, prefix="/api", tags=["Generate"])
app.include_router(roadmap.router, prefix="/api", tags=["Roadmap"])
app.include_router(chat.router, prefix="/api", tags=["Chat"])


@app.get("/health")
async def health():
    return {"status": "ok", "service": "AI Career Alignment Agent"}


@app.get("/")
async def root():
    return {
        "message": "AI Career Alignment Agent API",
        "docs": "/docs",
        "health": "/health",
    }
