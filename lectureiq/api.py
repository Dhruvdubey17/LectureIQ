"""FastAPI surface: ingest a lecture, ask a question, get cited answers."""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from . import config
from .ingest import ingest as _ingest
from .rag import ask as _ask

app = FastAPI(title="LectureIQ")

# Open CORS for local Next.js dev. Lock this down before any real deployment.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class IngestReq(BaseModel):
    url: str
    source: str = "captions"


class AskReq(BaseModel):
    question: str
    k: int | None = None


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/ingest")
def ingest_endpoint(req: IngestReq):
    try:
        return _ingest(req.url, source=req.source)
    except (RuntimeError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.post("/ask")
def ask_endpoint(req: AskReq):
    try:
        return _ask(req.question, k=req.k or config.TOP_K)
    except (RuntimeError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc))
