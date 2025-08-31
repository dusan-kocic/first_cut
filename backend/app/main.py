import os
import uuid
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from redis import Redis
from rq import Queue
from rq.job import Job

load_dotenv()

REQUEST_ID_HEADER = os.getenv("REQUEST_ID_HEADER", "X-Request-ID")
FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "http://localhost:3000")
ALLOWED_UPLOAD_TYPES = set((os.getenv("ALLOWED_UPLOAD_TYPES") or "").split(","))
STORAGE_PATH_UPLOADS = Path(os.getenv("STORAGE_PATH_UPLOADS", "/tmp/first_cut/uploads"))
STORAGE_PATH_OUTPUTS = Path(os.getenv("STORAGE_PATH_OUTPUTS", "/tmp/first_cut/outputs"))

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
QUEUE_NAME = os.getenv("QUEUE_NAME", "default")

STORAGE_PATH_UPLOADS.mkdir(parents=True, exist_ok=True)
STORAGE_PATH_OUTPUTS.mkdir(parents=True, exist_ok=True)

redis_conn = Redis.from_url(REDIS_URL)
queue = Queue(QUEUE_NAME, connection=redis_conn)

DB = {}

app = FastAPI(title="first_cut API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_ORIGIN],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=[REQUEST_ID_HEADER],
)

@app.middleware("http")
async def add_request_id(request: Request, call_next):
    req_id = request.headers.get(REQUEST_ID_HEADER) or str(uuid.uuid4())
    response = await call_next(request)
    response.headers[REQUEST_ID_HEADER] = req_id
    return response

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/upload", status_code=201)
async def upload(file: UploadFile = File(...)):
    if ALLOWED_UPLOAD_TYPES and file.content_type not in ALLOWED_UPLOAD_TYPES:
        raise HTTPException(status_code=400, detail="Unsupported file type")
    item_id = str(uuid.uuid4())
    target = STORAGE_PATH_UPLOADS / f"{item_id}_{file.filename}"
    with target.open("wb") as f:
        f.write(await file.read())
    transcript = ""
    if file.content_type == "text/plain":
        transcript = target.read_text(encoding="utf-8", errors="ignore")
    DB[item_id] = {"filename": file.filename, "transcript": transcript, "lead": None, "job_id": None}
    return {"id": item_id, "filename": file.filename, "status": "ready"}

@app.get("/transcript/{item_id}")
async def get_transcript(item_id: str):
    item = DB.get(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Transcript id not found")
    return {"id": item_id, "transcript": item.get("transcript", ""), "status": "ready"}

@app.post("/lead")
async def submit_lead(payload: dict):
    item_id = payload.get("id")
    lead = payload.get("lead")
    if not item_id or lead is None:
        raise HTTPException(status_code=400, detail="id and lead are required")
    item = DB.get(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Transcript id not found")
    item["lead"] = lead
    return {"id": item_id, "lead": lead, "status": "lead_saved"}

@app.post("/article")
async def generate_article(payload: dict):
    item_id = payload.get("id")
    if not item_id:
        raise HTTPException(status_code=400, detail="id is required")
    item = DB.get(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Transcript id not found")
    out_file = STORAGE_PATH_OUTPUTS / f"{item_id}.txt"
    if out_file.exists():
        raise HTTPException(status_code=409, detail="Article already generated")
    if item.get("job_id"):
        raise HTTPException(status_code=409, detail="Article generation already in progress")
    from backend.queue.tasks import generate_article_job
    job = queue.enqueue(generate_article_job, item_id)
    item["job_id"] = job.get_id()
    return {"id": item_id, "status": "queued"}, 202

@app.get("/article/{item_id}")
async def get_article(item_id: str):
    item = DB.get(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Article id not found")
    out_file = STORAGE_PATH_OUTPUTS / f"{item_id}.txt"
    if out_file.exists():
        article = out_file.read_text(encoding="utf-8", errors="ignore")
        return {"id": item_id, "article": article, "status": "article_ready"}
    job_id: Optional[str] = item.get("job_id")
    if not job_id:
        return {"id": item_id, "status": "queued"}
    try:
        job = Job.fetch(job_id, connection=redis_conn)
        if job.get_status() in {"queued"}:
            return {"id": item_id, "status": "queued"}
        return {"id": item_id, "status": "processing"}
    except Exception:
        return {"id": item_id, "status": "processing"}
