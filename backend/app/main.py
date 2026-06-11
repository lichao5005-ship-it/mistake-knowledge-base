from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.shared.database import SessionLocal, init_db
from app.modules.auth.router import router as auth_router
from app.modules.knowledge.router import router as knowledge_router
from app.modules.upload.router import router as upload_router

app = FastAPI(title="错题本", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

static_dir = Path(__file__).parent / "static" / "uploads"
static_dir.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir.parent)), name="static")

app.include_router(knowledge_router)
app.include_router(auth_router)
app.include_router(upload_router)


@app.on_event("startup")
def on_startup():
    init_db()
    from app.modules.knowledge.models import Subject

    db = SessionLocal()
    if not db.query(Subject).count():
        db.add_all([
            Subject(name="语文", icon="📘", sort_order=1),
            Subject(name="数学", icon="🧮", sort_order=2),
            Subject(name="英语", icon="🔤", sort_order=3),
        ])
        db.commit()
    db.close()


@app.get("/api/health")
def health():
    return {"status": "ok"}
