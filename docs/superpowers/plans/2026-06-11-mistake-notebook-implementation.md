# 孩子错题本 — 实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 构建一个本地运行的错题本 Web 应用，家长通过手机拍照录入错题，AI 自动识别判错分类，孩子在 PC 端复习和练习。

**Architecture:** Python FastAPI 后端 + Vue 3 前端 SPA，模块化架构。每个业务模块独立（router + service + models），通过 ID 松耦合。AI 能力通过统一适配层调用通义千问 Qwen3.7-Plus。数据库用 SQLite WAL 模式，第一版本地运行。

**Tech Stack:** Python 3.11+, FastAPI, SQLAlchemy, SQLite, Vue 3 (Vite), Qwen3.7-Plus API, qrcode, aiofiles

---

## 文件结构总览

```
D:\mistake-knowledge-base\
├── backend/
│   ├── pyproject.toml              # Python 依赖管理
│   ├── .env                        # API Key 等配置（不提交）
│   ├── .env.example                # 环境变量模板
│   ├── alembic.ini                 # 数据库迁移配置
│   ├── alembic/
│   │   └── versions/               # 迁移脚本
│   │
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                 # FastAPI 应用入口，注册路由
│   │   │
│   │   ├── shared/
│   │   │   ├── __init__.py
│   │   │   ├── database.py         # 数据库引擎 + 基类 + 会话管理
│   │   │   ├── config.py           # 全局配置（从 .env 读取）
│   │   │   └── ai_client.py        # AI API 统一适配层
│   │   │
│   │   ├── modules/
│   │   │   ├── __init__.py
│   │   │   │
│   │   │   ├── knowledge/          # 知识点模块（共享数据）
│   │   │   │   ├── __init__.py
│   │   │   │   ├── models.py       # Subject, KnowledgePoint
│   │   │   │   ├── schemas.py      # Pydantic 请求/响应模型
│   │   │   │   ├── service.py      # 业务逻辑
│   │   │   │   └── router.py       # API 路由
│   │   │   │
│   │   │   ├── auth/               # 认证模块
│   │   │   │   ├── __init__.py
│   │   │   │   ├── models.py       # User, Session
│   │   │   │   ├── schemas.py
│   │   │   │   ├── service.py      # 扫码登录逻辑
│   │   │   │   └── router.py
│   │   │   │
│   │   │   ├── upload/             # 上传模块
│   │   │   │   ├── __init__.py
│   │   │   │   ├── models.py       # UploadSession, SourceFile
│   │   │   │   ├── schemas.py
│   │   │   │   ├── service.py      # 文件存储 + 二维码生成
│   │   │   │   └── router.py
│   │   │   │
│   │   │   ├── ocr/                # OCR 识别模块
│   │   │   │   ├── __init__.py
│   │   │   │   ├── models.py       # OcrResult, AiCorrection
│   │   │   │   ├── schemas.py
│   │   │   │   ├── service.py      # AI 调用：识别+判错+分析
│   │   │   │   ├── prompts.py      # Prompt 模板
│   │   │   │   └── router.py
│   │   │   │
│   │   │   ├── question/           # 题库模块
│   │   │   │   ├── __init__.py
│   │   │   │   ├── models.py       # Question, MistakeRecord, QuestionImage
│   │   │   │   ├── schemas.py
│   │   │   │   ├── service.py      # CRUD + 查询/筛选
│   │   │   │   └── router.py
│   │   │   │
│   │   │   ├── generate/           # 出题模块
│   │   │   │   ├── __init__.py
│   │   │   │   ├── models.py       # SimilarQuestion, ExamPaper, PracticeResult
│   │   │   │   ├── schemas.py
│   │   │   │   ├── service.py      # AI 出题逻辑
│   │   │   │   ├── prompts.py      # 出题 Prompt 模板
│   │   │   │   └── router.py
│   │   │   │
│   │   │   └── analysis/           # 分析模块
│   │   │       ├── __init__.py
│   │   │       ├── models.py       # ErrorAnalysis, StudyReport
│   │   │       ├── schemas.py
│   │   │       ├── service.py      # 统计数据聚合
│   │   │       └── router.py
│   │   │
│   │   └── static/                 # 上传文件存储目录
│   │       └── uploads/
│   │
│   └── tests/
│       ├── __init__.py
│       ├── conftest.py             # 测试配置 + 内存数据库
│       ├── test_knowledge.py
│       ├── test_upload.py
│       ├── test_ocr.py
│       ├── test_question.py
│       ├── test_generate.py
│       └── test_analysis.py
│
├── frontend/
│   ├── package.json
│   ├── vite.config.ts
│   ├── index.html
│   └── src/
│       ├── main.ts
│       ├── App.vue
│       ├── router/
│       │   └── index.ts
│       ├── api/
│       │   └── client.ts           # Axios API 客户端
│       ├── views/
│       │   ├── Home.vue            # 首页：三科概览
│       │   ├── Upload.vue          # 录入页：二维码 + 文件列表
│       │   ├── ConfirmUpload.vue   # 确认入库页
│       │   ├── Questions.vue       # 错题集
│       │   ├── Generate.vue        # 出题页
│       │   ├── Analysis.vue        # 统计页
│       │   ├── Settings.vue        # 设置页
│       │   └── student/
│       │       ├── Dashboard.vue   # 孩子端首页
│       │       ├── Review.vue      # 逐题复习
│       │       └── Quiz.vue        # 做题模式
│       └── components/
│           └── ...
│
├── docs/
│   ├── superpowers/
│   │   ├── specs/
│   │   │   └── 2026-06-11-mistake-notebook-design.md
│   │   └── plans/
│   │       └── 2026-06-11-mistake-notebook-implementation.md
│
└── .env
```

---

### Task 1: 项目脚手架搭建

**Files:**
- Create: `backend/pyproject.toml`
- Create: `backend/.env.example`
- Create: `backend/app/__init__.py`
- Create: `backend/app/main.py`
- Create: `backend/app/shared/__init__.py`
- Create: `backend/app/shared/config.py`
- Create: `backend/app/shared/database.py`
- Create: `backend/app/shared/ai_client.py`
- Create: `backend/.gitignore`

- [ ] **Step 1: 创建 pyproject.toml**

```toml
[project]
name = "mistake-notebook"
version = "0.1.0"
dependencies = [
    "fastapi>=0.115.0",
    "uvicorn[standard]>=0.30.0",
    "sqlalchemy>=2.0.0",
    "alembic>=1.13.0",
    "python-multipart>=0.0.12",
    "aiofiles>=24.1.0",
    "python-dotenv>=1.0.0",
    "qrcode[pil]>=7.4.0",
    "openai>=1.0.0",         # 兼容 OpenAI SDK 格式调用 Qwen API
    "pydantic>=2.0.0",
    "pydantic-settings>=2.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.24.0",
    "httpx>=0.27.0",
]
```

- [ ] **Step 2: 创建 .env.example**

```bash
# 通义千问 Qwen API 配置
QWEN_API_KEY=sk-your-api-key-here
QWEN_API_BASE=https://dashscope.aliyuncs.com/compatible-mode/v1
QWEN_MODEL=qwen3.7-plus

# 应用配置
SECRET_KEY=change-this-to-a-random-string
DATABASE_URL=sqlite:///./mistake.db
UPLOAD_DIR=./app/static/uploads
```

- [ ] **Step 3: 创建 config.py**

```python
from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    # Qwen API
    qwen_api_key: str = ""
    qwen_api_base: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    qwen_model: str = "qwen3.7-plus"

    # App
    secret_key: str = "dev-secret-key"
    database_url: str = "sqlite:///./mistake.db"
    upload_dir: str = "./app/static/uploads"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
```

- [ ] **Step 4: 创建 database.py**

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from app.shared.config import settings

engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {},
    echo=False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """创建所有表（开发阶段用，后续改用 alembic）"""
    Base.metadata.create_all(bind=engine)
```

- [ ] **Step 5: 创建 ai_client.py**

```python
from openai import OpenAI
from app.shared.config import settings

client = OpenAI(
    api_key=settings.qwen_api_key,
    base_url=settings.qwen_api_base,
)


def call_qwen_vision(prompt: str, image_data: bytes, model: str | None = None) -> str:
    """调用 Qwen 多模态模型，图片以 base64 格式传入"""
    import base64

    b64 = base64.b64encode(image_data).decode("utf-8")
    data_url = f"data:image/jpeg;base64,{b64}"

    resp = client.chat.completions.create(
        model=model or settings.qwen_model,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": data_url}},
                ],
            }
        ],
        response_format={"type": "json_object"},
    )
    return resp.choices[0].message.content or ""


def call_qwen_text(prompt: str, model: str | None = None) -> str:
    """纯文本调用（用于出题、分析等不需要图片的场景）"""
    resp = client.chat.completions.create(
        model=model or settings.qwen_model,
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
    )
    return resp.choices[0].message.content or ""
```

- [ ] **Step 6: 创建 main.py**

```python
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path

from app.shared.database import init_db

app = FastAPI(title="错题本", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静态文件（上传的图片等）
static_dir = Path(__file__).parent / "static" / "uploads"
static_dir.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir.parent)), name="static")


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/api/health")
def health():
    return {"status": "ok"}
```

- [ ] **Step 7: 创建 .gitignore**

```gitignore
__pycache__/
*.pyc
.env
*.db
app/static/uploads/*
!app/static/uploads/.gitkeep
node_modules/
dist/
```

- [ ] **Step 8: 初始化虚拟环境并验证启动**

```bash
cd D:/mistake-knowledge-base/backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -e ".[dev]"
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
# 访问 http://localhost:8000/api/health → {"status":"ok"}
```

- [ ] **Step 9: 提交**

```bash
git init
git add .
git commit -m "feat: project scaffolding with FastAPI + SQLAlchemy + Qwen AI client"
```

---

### Task 2: 知识点模块 + 数据库模型

**Files:**
- Create: `backend/app/modules/__init__.py`
- Create: `backend/app/modules/knowledge/__init__.py`
- Create: `backend/app/modules/knowledge/models.py`
- Create: `backend/app/modules/knowledge/schemas.py`
- Create: `backend/app/modules/knowledge/service.py`
- Create: `backend/app/modules/knowledge/router.py`
- Modify: `backend/app/main.py`（注册路由 + 创建表）
- Create: `backend/tests/__init__.py`
- Create: `backend/tests/conftest.py`
- Create: `backend/tests/test_knowledge.py`

- [ ] **Step 1: 创建 knowledge/models.py**

```python
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.shared.database import Base


class Subject(Base):
    __tablename__ = "subjects"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)  # 语文/数学/英语
    icon = Column(String(20), default="")       # emoji 图标
    sort_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)


class KnowledgePoint(Base):
    __tablename__ = "knowledge_points"

    id = Column(Integer, primary_key=True)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    name = Column(String(100), nullable=False)
    parent_id = Column(Integer, ForeignKey("knowledge_points.id"), nullable=True)
    level = Column(Integer, default=1)           # 层级 1/2/3
    sort_order = Column(Integer, default=0)

    parent = relationship("KnowledgePoint", remote_side="KnowledgePoint.id", backref="children")
```

- [ ] **Step 2: 创建 service.py 和 schemas.py**

```python
# service.py
from sqlalchemy.orm import Session
from app.modules.knowledge.models import Subject, KnowledgePoint


def get_subjects(db: Session) -> list[Subject]:
    return db.query(Subject).order_by(Subject.sort_order).all()


def get_knowledge_points(db: Session, subject_id: int) -> list[KnowledgePoint]:
    return (
        db.query(KnowledgePoint)
        .filter(KnowledgePoint.subject_id == subject_id)
        .order_by(KnowledgePoint.level, KnowledgePoint.sort_order)
        .all()
    )
```

```python
# schemas.py
from pydantic import BaseModel


class SubjectOut(BaseModel):
    id: int
    name: str
    icon: str

    model_config = {"from_attributes": True}


class KnowledgePointOut(BaseModel):
    id: int
    subject_id: int
    name: str
    parent_id: int | None = None
    level: int

    model_config = {"from_attributes": True}
```

- [ ] **Step 3: 创建 router.py**

```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.shared.database import get_db
from app.modules.knowledge import service, schemas

router = APIRouter(prefix="/api/knowledge", tags=["knowledge"])


@router.get("/subjects", response_model=list[schemas.SubjectOut])
def list_subjects(db: Session = Depends(get_db)):
    return service.get_subjects(db)


@router.get("/subjects/{subject_id}/points", response_model=list[schemas.KnowledgePointOut])
def list_knowledge_points(subject_id: int, db: Session = Depends(get_db)):
    return service.get_knowledge_points(db, subject_id)
```

- [ ] **Step 4: 创建 conftest.py**

```python
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.shared.database import Base, get_db
from app.main import app

TEST_DATABASE_URL = "sqlite:///./test.db"


@pytest.fixture
def db_session():
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    TestSession = sessionmaker(bind=engine)
    session = TestSession()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(db_session):
    def override_get_db():
        yield db_session
    app.dependency_overrides[get_db] = override_get_db
    from httpx import ASGITransport, AsyncClient
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://test")


@pytest.fixture
def seed_subjects(db_session):
    from app.modules.knowledge.models import Subject
    subjects = [
        Subject(name="语文", icon="📘", sort_order=1),
        Subject(name="数学", icon="🧮", sort_order=2),
        Subject(name="英语", icon="🔤", sort_order=3),
    ]
    db_session.add_all(subjects)
    db_session.commit()
    return subjects
```

- [ ] **Step 5: 创建 test_knowledge.py**

```python
import pytest


@pytest.mark.asyncio
async def test_list_subjects(client, seed_subjects):
    resp = await client.get("/api/knowledge/subjects")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 3
    assert data[0]["name"] == "语文"


@pytest.mark.asyncio
async def test_subject_response_shape(client, seed_subjects):
    resp = await client.get("/api/knowledge/subjects")
    item = resp.json()[0]
    assert "id" in item
    assert "name" in item
    assert "icon" in item
```

- [ ] **Step 6: 注册路由到 main.py**

在 `app/main.py` 中添加：

```python
from app.modules.knowledge.router import router as knowledge_router

app.include_router(knowledge_router)
```

同时给 `on_startup` 添加种子数据逻辑：

```python
from app.modules.knowledge.models import Subject

@app.on_event("startup")
def on_startup():
    init_db()
    # 初始化三科
    db = SessionLocal()
    if not db.query(Subject).count():
        db.add_all([
            Subject(name="语文", icon="📘", sort_order=1),
            Subject(name="数学", icon="🧮", sort_order=2),
            Subject(name="英语", icon="🔤", sort_order=3),
        ])
        db.commit()
    db.close()
```

- [ ] **Step 7: 运行测试**

```bash
cd D:/mistake-knowledge-base/backend
pytest tests/test_knowledge.py -v
# Expected: 2 passed
```

- [ ] **Step 8: 提交**

```bash
git add backend/app/modules/knowledge/ backend/app/modules/__init__.py backend/tests/ backend/app/main.py
git commit -m "feat: add knowledge module with subjects and knowledge points"
```

---

### Task 3: 认证模块 — QR 扫码登录

**Files:**
- Create: `backend/app/modules/auth/__init__.py`
- Create: `backend/app/modules/auth/models.py`
- Create: `backend/app/modules/auth/schemas.py`
- Create: `backend/app/modules/auth/service.py`
- Create: `backend/app/modules/auth/router.py`
- Modify: `backend/app/main.py`（注册路由）
- Create: `backend/tests/test_auth.py`

- [ ] **Step 1: 创建 auth/models.py**

```python
import uuid
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from app.shared.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    role = Column(String(20), default="parent")  # parent / child
    nickname = Column(String(50), default="")
    avatar = Column(String(200), default="")


class LoginSession(Base):
    """扫码登录会话"""
    __tablename__ = "login_sessions"

    id = Column(Integer, primary_key=True)
    session_id = Column(String(36), unique=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(Integer, nullable=True)
    status = Column(String(20), default="pending")  # pending / scanned / confirmed
    created_at = Column(DateTime, default=datetime.now)
    expires_at = Column(DateTime)
```

- [ ] **Step 2: 创建 service.py**

```python
import uuid
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.modules.auth.models import User, LoginSession


def get_or_create_default_user(db: Session) -> User:
    """第一版：自动创建默认用户"""
    user = db.query(User).first()
    if not user:
        user = User(role="parent", nickname="家长")
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


def create_qr_session(db: Session) -> LoginSession:
    session = LoginSession(
        session_id=str(uuid.uuid4()),
        status="pending",
        expires_at=datetime.now() + timedelta(minutes=5),
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def verify_session(db: Session, session_id: str) -> User | None:
    ls = db.query(LoginSession).filter(
        LoginSession.session_id == session_id,
        LoginSession.status == "pending",
        LoginSession.expires_at > datetime.now(),
    ).first()
    if not ls:
        return None
    user = get_or_create_default_user(db)
    ls.user_id = user.id
    ls.status = "confirmed"
    db.commit()
    return user
```

- [ ] **Step 3: 创建 router.py**

```python
import io
import qrcode
import base64
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session
from app.shared.database import get_db
from app.modules.auth import service as auth_service

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/qr/create")
def create_qr(base_url: str = Query("http://localhost:8000"), db: Session = Depends(get_db)):
    """PC 端：生成登录二维码"""
    session = auth_service.create_qr_session(db)
    login_url = f"{base_url}/scan?session_id={session.session_id}"

    qr = qrcode.make(login_url)
    buf = io.BytesIO()
    qr.save(buf, format="PNG")
    img_b64 = base64.b64encode(buf.getvalue()).decode()

    return {
        "session_id": session.session_id,
        "qr_image": f"data:image/png;base64,{img_b64}",
        "login_url": login_url,
        "expires_at": session.expires_at.isoformat(),
    }


@router.post("/qr/verify/{session_id}")
def verify_qr(session_id: str, db: Session = Depends(get_db)):
    """手机端：扫码后验证"""
    user = auth_service.verify_session(db, session_id)
    if not user:
        raise HTTPException(418, "会话已过期或无效")
    return {"user_id": user.id, "role": user.role, "nickname": user.nickname}


@router.get("/qr/status/{session_id}")
def qr_status(session_id: str, db: Session = Depends(get_db)):
    """PC 端：轮询查询二维码状态"""
    from app.modules.auth.models import LoginSession
    ls = db.query(LoginSession).filter(
        LoginSession.session_id == session_id
    ).first()
    if not ls:
        raise HTTPException(404, "会话不存在")
    return {"status": ls.status}
```

- [ ] **Step 4: 创建 test_auth.py**

```python
import pytest


@pytest.mark.asyncio
async def test_create_qr(client):
    resp = await client.post("/api/auth/qr/create?base_url=http://localhost:8000")
    assert resp.status_code == 200
    data = resp.json()
    assert "session_id" in data
    assert "qr_image" in data
    assert data["qr_image"].startswith("data:image/png;base64,")


@pytest.mark.asyncio
async def test_verify_nonexistent_session(client):
    resp = await client.post("/api/auth/qr/verify/nonexistent")
    assert resp.status_code == 418


@pytest.mark.asyncio
async def test_full_qr_flow(client):
    # 创建二维码
    resp = await client.post("/api/auth/qr/create")
    session_id = resp.json()["session_id"]

    # 验证状态是 pending
    status_resp = await client.get(f"/api/auth/qr/status/{session_id}")
    assert status_resp.json()["status"] == "pending"

    # 手机扫码验证
    verify_resp = await client.post(f"/api/auth/qr/verify/{session_id}")
    assert verify_resp.status_code == 200

    # 状态变为 confirmed
    status_resp2 = await client.get(f"/api/auth/qr/status/{session_id}")
    assert status_resp2.json()["status"] == "confirmed"
```

- [ ] **Step 5: 注册路由并运行测试**

```python
# main.py
from app.modules.auth.router import router as auth_router
app.include_router(auth_router)
```

```bash
pytest tests/test_auth.py -v
# Expected: 3 passed
```

- [ ] **Step 6: 提交**

```bash
git add backend/app/modules/auth/ backend/app/main.py backend/tests/test_auth.py
git commit -m "feat: add QR code login module"
```

---

### Task 4: 上传模块 — 文件存储 + 二维码 + 手机上传页

**Files:**
- Create: `backend/app/modules/upload/__init__.py`
- Create: `backend/app/modules/upload/models.py`
- Create: `backend/app/modules/upload/schemas.py`
- Create: `backend/app/modules/upload/service.py`
- Create: `backend/app/modules/upload/router.py`
- Modify: `backend/app/main.py`（注册路由）
- Create: `backend/tests/test_upload.py`

- [ ] **Step 1: 创建 upload/models.py**

```python
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from app.shared.database import Base


class UploadSession(Base):
    __tablename__ = "upload_sessions"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    source_type = Column(String(20), default="photo")  # photo / file
    status = Column(String(20), default="pending")      # pending / processing / done
    created_at = Column(DateTime, default=datetime.now)


class SourceFile(Base):
    __tablename__ = "source_files"

    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey("upload_sessions.id"))
    file_name = Column(String(200))
    file_path = Column(Text)
    file_type = Column(String(20))  # jpg / png / pdf / docx
    page_count = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.now)
```

- [ ] **Step 2: 创建 upload/service.py**

```python
import uuid
from pathlib import Path
from sqlalchemy.orm import Session
from fastapi import UploadFile
from app.shared.config import settings
from app.modules.upload.models import UploadSession, SourceFile


def create_session(db: Session, user_id: int, subject_id: int) -> UploadSession:
    session = UploadSession(user_id=user_id, subject_id=subject_id)
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


async def save_upload_file(
    db: Session, session_id: int, file: UploadFile
) -> SourceFile:
    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)

    ext = file.filename.split(".")[-1] if "." in file.filename else "jpg"
    unique_name = f"{uuid.uuid4()}.{ext}"
    file_path = upload_dir / unique_name

    content = await file.read()
    file_path.write_bytes(content)

    sf = SourceFile(
        session_id=session_id,
        file_name=file.filename or unique_name,
        file_path=str(file_path),
        file_type=ext,
    )
    db.add(sf)
    db.commit()
    db.refresh(sf)
    return sf
```

- [ ] **Step 3: 创建 router.py**

```python
from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.shared.database import get_db
from app.modules.upload import service as upload_service

router = APIRouter(prefix="/api/upload", tags=["upload"])


@router.post("/session")
def create_session(subject_id: int = Form(...), user_id: int = Form(1), db: Session = Depends(get_db)):
    session = upload_service.create_session(db, user_id, subject_id)
    return {"session_id": session.id, "subject_id": subject_id}


@router.post("/files")
async def upload_files(
    session_id: int = Form(...),
    files: list[UploadFile] = File(...),
    db: Session = Depends(get_db),
):
    results = []
    for f in files:
        sf = await upload_service.save_upload_file(db, session_id, f)
        results.append({"file_id": sf.id, "file_name": sf.file_name})
    return {"session_id": session_id, "files": results}
```

- [ ] **Step 4: 提交**

```bash
git add backend/app/modules/upload/
git commit -m "feat: add upload module with session and file storage"
```

---

### Task 5: OCR + AI 识别模块

**Files:**
- Create: `backend/app/modules/ocr/__init__.py`
- Create: `backend/app/modules/ocr/models.py`
- Create: `backend/app/modules/ocr/schemas.py`
- Create: `backend/app/modules/ocr/prompts.py`
- Create: `backend/app/modules/ocr/service.py`
- Create: `backend/app/modules/ocr/router.py`
- Modify: `backend/app/main.py`（注册路由）
- Create: `backend/tests/test_ocr.py`

- [ ] **Step 1: 创建 ocr/models.py**

```python
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, Float, Boolean
from app.shared.database import Base


class OcrResult(Base):
    __tablename__ = "ocr_results"

    id = Column(Integer, primary_key=True)
    source_file_id = Column(Integer, ForeignKey("source_files.id"))
    page_number = Column(Integer, default=1)
    raw_text = Column(Text, default="")
    structured_data = Column(Text, default="")  # JSON: 逐题结构化数据
    status = Column(String(20), default="pending")  # pending / done / failed
    confidence = Column(Float, default=0.0)
    processing_time = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.now)


class AiCorrection(Base):
    __tablename__ = "ai_corrections"

    id = Column(Integer, primary_key=True)
    ocr_result_id = Column(Integer, ForeignKey("ocr_results.id"))
    question_number = Column(String(20))
    question_content = Column(Text, default="")
    student_answer = Column(Text, default="")
    is_correct = Column(Boolean, nullable=True)
    correct_answer = Column(Text, default="")
    error_type = Column(String(50), default="")  # 粗心/概念不清/审题错误/计算错误/未作答
    ai_analysis = Column(Text, default="")  # JSON: 解题思路
    knowledge_point = Column(String(100), default="")
```

- [ ] **Step 2: 创建 prompts.py**

```python
OCR_PROMPT = """你是一个小学错题本助手。请识别图片中的试卷/作业内容，按以下 JSON 格式返回：

{
  "questions": [
    {
      "number": "1",
      "content": "题目的文字内容，数学公式用 LaTeX 格式",
      "student_answer": "学生写的答案（如空白则为空字符串）",
      "blank_exists": true
    }
  ],
  "subject_type": "数学/语文/英语"
}

注意：
- 逐题拆解，不要遗漏任何一题
- 学生手写答案要尽力识别
- 数学公式用 LaTeX：$32 \\times 15 = ?$
- 如果学生没有作答，student_answer 留空字符串"""

CORRECTION_PROMPT = """你是一个小学错题本助手。请分析以下题目，按 JSON 格式返回判错结果：

{
  "is_correct": true/false,
  "correct_answer": "标准答案",
  "error_type": "正确/粗心/概念不清/审题错误/计算错误/未作答",
  "analysis": "用小学生能理解的语言写出解题步骤，要求详细、耐心、鼓励性",
  "knowledge_point": "本题所属知识点名称"
}

题目：{question_content}
学生答案：{student_answer}"""
```

- [ ] **Step 3: 创建 ocr/service.py**

```python
import time
import json
from pathlib import Path
from sqlalchemy.orm import Session
from app.shared.ai_client import call_qwen_vision, call_qwen_text
from app.modules.ocr.models import OcrResult, AiCorrection
from app.modules.ocr.prompts import OCR_PROMPT, CORRECTION_PROMPT
from app.modules.question.models import Question, MistakeRecord


def process_image(db: Session, source_file_id: int, image_path: str) -> OcrResult:
    """处理一张图片：OCR → 逐题判错 → 返回结果"""
    t0 = time.time()
    image_bytes = Path(image_path).read_bytes()

    # Step 1: OCR 识别
    ocr_raw = call_qwen_vision(OCR_PROMPT, image_bytes)
    ocr_data = json.loads(ocr_raw)
    t1 = time.time()

    result = OcrResult(
        source_file_id=source_file_id,
        raw_text=ocr_raw,
        structured_data=json.dumps(ocr_data, ensure_ascii=False),
        status="done",
        confidence=0.9,
        processing_time=t1 - t0,
    )
    db.add(result)
    db.commit()
    db.refresh(result)

    # Step 2: 逐题判错
    for q in ocr_data.get("questions", []):
        if not q.get("student_answer"):
            # 未作答
            correction = AiCorrection(
                ocr_result_id=result.id,
                question_number=q["number"],
                question_content=q["content"],
                student_answer="",
                is_correct=False,
                error_type="未作答",
                correct_answer="",
                ai_analysis="",
                knowledge_point="",
            )
            db.add(correction)
            continue

        prompt = CORRECTION_PROMPT.format(
            question_content=q["content"],
            student_answer=q["student_answer"],
        )
        correction_raw = call_qwen_text(prompt)
        correction_data = json.loads(correction_raw)

        correction = AiCorrection(
            ocr_result_id=result.id,
            question_number=q["number"],
            question_content=q["content"],
            student_answer=q["student_answer"],
            is_correct=correction_data["is_correct"],
            correct_answer=correction_data["correct_answer"],
            error_type=correction_data["error_type"],
            ai_analysis=json.dumps(correction_data, ensure_ascii=False),
            knowledge_point=correction_data.get("knowledge_point", ""),
        )
        db.add(correction)

    db.commit()
    return result
```

- [ ] **Step 4: 创建 router.py**

```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.shared.database import get_db
from app.modules.ocr import service as ocr_service
from app.modules.ocr.models import OcrResult, AiCorrection

router = APIRouter(prefix="/api/ocr", tags=["ocr"])


@router.post("/process/{source_file_id}")
def process_file(source_file_id: int, db: Session = Depends(get_db)):
    from app.modules.upload.models import SourceFile
    sf = db.query(SourceFile).filter(SourceFile.id == source_file_id).first()
    if not sf:
        return {"error": "file not found"}, 404
    result = ocr_service.process_image(db, source_file_id, sf.file_path)
    return {"ocr_result_id": result.id, "status": result.status}


@router.get("/results/{ocr_result_id}")
def get_result(ocr_result_id: int, db: Session = Depends(get_db)):
    result = db.query(OcrResult).filter(OcrResult.id == ocr_result_id).first()
    corrections = db.query(AiCorrection).filter(
        AiCorrection.ocr_result_id == ocr_result_id
    ).all()
    return {
        "ocr": {
            "id": result.id,
            "structured_data": json.loads(result.structured_data) if result.structured_data else {},
            "status": result.status,
        },
        "corrections": [
            {
                "id": c.id,
                "question_number": c.question_number,
                "question_content": c.question_content,
                "student_answer": c.student_answer,
                "is_correct": c.is_correct,
                "correct_answer": c.correct_answer,
                "error_type": c.error_type,
                "ai_analysis": json.loads(c.ai_analysis) if c.ai_analysis else {},
                "knowledge_point": c.knowledge_point,
            }
            for c in corrections
        ],
    }
```

- [ ] **Step 5: 提交**

```bash
git add backend/app/modules/ocr/
git commit -m "feat: add OCR module with Qwen vision AI processing"
```

---

### Task 6: 题库模块 — 错题入库与查询

**Files:**
- Create: `backend/app/modules/question/__init__.py`
- Create: `backend/app/modules/question/models.py`
- Create: `backend/app/modules/question/schemas.py`
- Create: `backend/app/modules/question/service.py`
- Create: `backend/app/modules/question/router.py`
- Modify: `backend/app/main.py`（注册路由）
- Create: `backend/tests/test_question.py`

- [ ] **Step 1: 创建 question/models.py**

```python
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, Float, Boolean, ForeignKey
from app.shared.database import Base


class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    knowledge_point_id = Column(Integer, ForeignKey("knowledge_points.id"), nullable=True)
    question_type = Column(String(30), default="填空题")  # 选择题/填空题/计算题/应用题/作文
    content = Column(Text, default="")  # JSON: {text, image_url, latex}
    answer = Column(Text, default="")
    difficulty = Column(Integer, default=1)  # 1-5
    source_file_id = Column(Integer, nullable=True)
    source_page = Column(Integer, default=1)
    tags = Column(Text, default="")  # JSON array
    status = Column(String(20), default="active")
    created_at = Column(DateTime, default=datetime.now)


class MistakeRecord(Base):
    __tablename__ = "mistake_records"

    id = Column(Integer, primary_key=True)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    student_answer = Column(Text, default="")
    is_correct = Column(Boolean, nullable=True)
    error_type = Column(String(50), default="")
    ai_error_analysis = Column(Text, default="")  # JSON
    corrected_count = Column(Integer, default=0)
    last_wrong_at = Column(DateTime, default=datetime.now)
    created_at = Column(DateTime, default=datetime.now)


class QuestionImage(Base):
    __tablename__ = "question_images"

    id = Column(Integer, primary_key=True)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    image_type = Column(String(20), default="original")  # original / annotated / solution
    image_path = Column(Text, default="")
```

- [ ] **Step 2: 创建 question/service.py**

```python
from sqlalchemy.orm import Session
from app.modules.question.models import Question, MistakeRecord


def create_question_from_correction(
    db: Session,
    subject_id: int,
    correction_data: dict,
    source_file_id: int | None = None,
) -> Question:
    q = Question(
        subject_id=subject_id,
        question_type="填空题",
        content=correction_data.get("question_content", ""),
        answer=correction_data.get("correct_answer", ""),
        source_file_id=source_file_id,
        difficulty=3,
    )
    db.add(q)
    db.commit()
    db.refresh(q)

    mr = MistakeRecord(
        question_id=q.id,
        student_answer=correction_data.get("student_answer", ""),
        is_correct=correction_data.get("is_correct"),
        error_type=correction_data.get("error_type", ""),
        ai_error_analysis=correction_data.get("ai_analysis", ""),
        corrected_count=0,
    )
    db.add(mr)
    db.commit()
    return q


def bulk_confirm(
    db: Session,
    subject_id: int,
    corrections: list[dict],
    source_file_id: int | None = None,
) -> list[Question]:
    """批量确认入库"""
    questions = []
    for c in corrections:
        q = create_question_from_correction(db, subject_id, c, source_file_id)
        questions.append(q)
    return questions


def list_questions(
    db: Session,
    subject_id: int | None = None,
    error_type: str | None = None,
    knowledge_point_id: int | None = None,
    status: str = "active",
    limit: int = 50,
    offset: int = 0,
) -> list[Question]:
    query = db.query(Question).filter(Question.status == status)
    if subject_id:
        query = query.filter(Question.subject_id == subject_id)
    if knowledge_point_id:
        query = query.filter(Question.knowledge_point_id == knowledge_point_id)
    return query.order_by(Question.created_at.desc()).offset(offset).limit(limit).all()
```

- [ ] **Step 3: 创建 router.py**

```python
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.shared.database import get_db
from app.modules.question import service as question_service
from app.modules.question.models import MistakeRecord

router = APIRouter(prefix="/api/questions", tags=["questions"])


@router.post("/confirm")
def confirm_questions(
    subject_id: int = Query(...),
    corrections: list[dict] = [],
    source_file_id: int | None = Query(None),
    db: Session = Depends(get_db),
):
    questions = question_service.bulk_confirm(db, subject_id, corrections, source_file_id)
    return {"confirmed": len(questions), "question_ids": [q.id for q in questions]}


@router.get("")
def list_questions(
    subject_id: int | None = Query(None),
    error_type: str | None = Query(None),
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    questions = question_service.list_questions(db, subject_id, error_type, limit=limit, offset=offset)
    return [
        {
            "id": q.id,
            "subject_id": q.subject_id,
            "content": q.content,
            "answer": q.answer,
            "difficulty": q.difficulty,
            "created_at": q.created_at.isoformat(),
            "mistake": _get_latest_mistake(db, q.id),
        }
        for q in questions
    ]


def _get_latest_mistake(db: Session, question_id: int) -> dict | None:
    mr = db.query(MistakeRecord).filter(
        MistakeRecord.question_id == question_id
    ).order_by(MistakeRecord.created_at.desc()).first()
    if not mr:
        return None
    return {
        "student_answer": mr.student_answer,
        "is_correct": mr.is_correct,
        "error_type": mr.error_type,
        "corrected_count": mr.corrected_count,
    }
```

- [ ] **Step 4: 提交**

```bash
git add backend/app/modules/question/
git commit -m "feat: add question module with mistake records"
```

---

### Task 7: Vue 3 前端搭建 + 基础页面

**Files:**
- Create: `frontend/package.json`
- Create: `frontend/vite.config.ts`
- Create: `frontend/tsconfig.json`
- Create: `frontend/index.html`
- Create: `frontend/src/main.ts`
- Create: `frontend/src/App.vue`
- Create: `frontend/src/router/index.ts`
- Create: `frontend/src/api/client.ts`
- Create: `frontend/src/style.css`
- Create: `frontend/src/views/Home.vue`
- Create: `frontend/src/views/Upload.vue`
- Create: `frontend/src/views/Questions.vue`

- [ ] **Step 1: 初始化前端项目**

```bash
cd D:/mistake-knowledge-base
npm create vite@latest frontend -- --template vue-ts
cd frontend
npm install
npm install vue-router@4 axios
```

- [ ] **Step 2: 配置 vite.config.ts**

```typescript
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
```

- [ ] **Step 3: 创建 API 客户端**

```typescript
// src/api/client.ts
import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
})

export default api

// API 方法
export const knowledgeApi = {
  getSubjects: () => api.get('/knowledge/subjects'),
  getKnowledgePoints: (subjectId: number) =>
    api.get(`/knowledge/subjects/${subjectId}/points`),
}

export const authApi = {
  createQr: (baseUrl?: string) =>
    api.post(`/auth/qr/create?base_url=${baseUrl || 'http://localhost:8000'}`),
  qrStatus: (sessionId: string) =>
    api.get(`/auth/qr/status/${sessionId}`),
}

export const uploadApi = {
  createSession: (subjectId: number, userId = 1) =>
    api.post('/upload/session', { subject_id: subjectId, user_id: userId }),
  uploadFiles: (sessionId: number, files: File[]) => {
    const form = new FormData()
    form.append('session_id', String(sessionId))
    files.forEach(f => form.append('files', f))
    return api.post('/upload/files', form)
  },
}

export const questionApi = {
  list: (params?: Record<string, any>) =>
    api.get('/questions', { params }),
  confirm: (subjectId: number, corrections: any[], sourceFileId?: number) =>
    api.post('/questions/confirm', null, {
      params: { subject_id: subjectId, source_file_id: sourceFileId },
      data: { corrections },
    }),
}
```

- [ ] **Step 4: 创建 Home.vue（三科概览）**

```vue
<template>
  <div class="home">
    <header>
      <h1>📘 错题本</h1>
      <p class="subtitle">选择科目查看和管理错题</p>
    </header>
    <div class="subject-grid">
      <div
        v-for="subject in subjects"
        :key="subject.id"
        class="subject-card"
        @click="$router.push(`/questions?subject_id=${subject.id}`)"
      >
        <span class="subject-icon">{{ subject.icon }}</span>
        <h3>{{ subject.name }}</h3>
        <!-- 统计数字等后续加 -->
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { knowledgeApi } from '../api/client'

const subjects = ref<any[]>([])

onMounted(async () => {
  const { data } = await knowledgeApi.getSubjects()
  subjects.value = data
})
</script>
```

- [ ] **Step 5: 提交**

```bash
git add frontend/
git commit -m "feat: scaffold Vue 3 frontend with router, API client, and home page"
```

---

### Task 8: 前端录入与确认页面

**Files:**
- Create: `frontend/src/views/ConfirmUpload.vue`
- Modify: `frontend/src/router/index.ts`（添加路由）
- Modify: `frontend/src/views/Upload.vue`（二维码 + 文件列表）

- [ ] **Step 1: 创建 Upload.vue**

```vue
<template>
  <div class="upload-page">
    <header>
      <h1>📥 录入错题</h1>
    </header>
    <div class="upload-content">
      <div class="qr-section" v-if="qrData">
        <h3>用手机扫码上传</h3>
        <img :src="qrData.qr_image" alt="QR Code" class="qr-code" />
        <p class="hint">手机扫码 → 选择科目 → 拍照 → 自动识别</p>
        <p class="session-id">会话ID: {{ qrData.session_id }}</p>
        <p class="expires">有效期至: {{ qrData.expires_at }}</p>
      </div>
      <button @click="createQr" class="btn-primary" :disabled="loading">
        {{ loading ? '生成中...' : '生成二维码' }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { authApi } from '../api/client'

const qrData = ref<any>(null)
const loading = ref(false)

async function createQr() {
  loading.value = true
  try {
    const { data } = await authApi.createQr()
    qrData.value = data
  } finally {
    loading.value = false
  }
}
</script>
```

- [ ] **Step 2: 创建 ConfirmUpload.vue**

```vue
<template>
  <div class="confirm-page">
    <header>
      <h1>✅ 确认入库</h1>
    </header>
    <div v-if="!ocrResult" class="empty">
      <p>暂无可确认的识别结果，请先上传并处理图片</p>
    </div>
    <template v-else>
      <div v-for="c in ocrResult.corrections" :key="c.id" class="correction-card"
        :class="{ correct: c.is_correct, wrong: !c.is_correct && c.error_type !== '未作答' }">
        <div class="card-header">
          <span class="q-number">#{{ c.question_number }}</span>
          <span class="q-status" :class="c.is_correct ? 'tag-correct' : 'tag-wrong'">
            {{ c.is_correct ? '✓ 正确' : c.error_type }}
          </span>
        </div>
        <p class="q-content">{{ c.question_content }}</p>
        <div class="q-detail">
          <span>学生答: {{ c.student_answer || '未作答' }}</span>
          <span v-if="!c.is_correct">正解: {{ c.correct_answer }}</span>
        </div>
        <div v-if="c.ai_analysis" class="q-analysis">
          <strong>分析：</strong>{{ c.ai_analysis.analysis }}
        </div>
      </div>
      <button @click="confirmAll" class="btn-primary">
        确认入库 ({{ ocrResult.corrections.length }}题)
      </button>
    </template>
  </div>
</template>
```

- [ ] **Step 3: 配置路由**

```typescript
// router/index.ts
const routes = [
  { path: '/', component: () => import('../views/Home.vue') },
  { path: '/upload', component: () => import('../views/Upload.vue') },
  { path: '/confirm/:sessionId', component: () => import('../views/ConfirmUpload.vue') },
  { path: '/questions', component: () => import('../views/Questions.vue') },
]
```

- [ ] **Step 4: 提交**

```bash
git add frontend/src/views/Upload.vue frontend/src/views/ConfirmUpload.vue frontend/src/router/index.ts
git commit -m "feat: add upload QR code and confirm upload pages"
```

---

### Task 9: 出题模块 — 相似题 + 模拟卷

**Files:**
- Create: `backend/app/modules/generate/__init__.py`
- Create: `backend/app/modules/generate/models.py`
- Create: `backend/app/modules/generate/schemas.py`
- Create: `backend/app/modules/generate/prompts.py`
- Create: `backend/app/modules/generate/service.py`
- Create: `backend/app/modules/generate/router.py`
- Modify: `backend/app/main.py`（注册路由）
- Create: `frontend/src/views/Generate.vue`

- [ ] **Step 1: 创建 generate/models.py**

```python
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey
from app.shared.database import Base


class ExamPaper(Base):
    __tablename__ = "exam_papers"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    title = Column(String(200), default="")
    question_ids = Column(Text, default="[]")  # JSON array
    total_score = Column(Integer, default=100)
    difficulty = Column(Integer, default=3)
    duration_minutes = Column(Integer, default=60)
    status = Column(String(20), default="draft")  # draft / published / done
    created_at = Column(DateTime, default=datetime.now)


class PracticeResult(Base):
    __tablename__ = "practice_results"

    id = Column(Integer, primary_key=True)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    student_answer = Column(Text, default="")
    is_correct = Column(Boolean, nullable=True)
    source = Column(String(50), default="")  # similar / exam / review
    time_spent = Column(Integer, default=0)  # seconds
    created_at = Column(DateTime, default=datetime.now)
```

- [ ] **Step 2: 创建 prompts.py**

```python
SIMILAR_QUESTION_PROMPT = """你是一个小学出题老师。请基于下面的题目，生成 3 道相似的练习题。

要求：
- 相同的知识点和难度级别
- 题型类似但数字/内容不同
- 适合小学生理解
- 附上答案和解题步骤

原题：{question_content}
正确答案：{correct_answer}
知识点：{knowledge_point}

按以下 JSON 格式返回：
{
  "questions": [
    {
      "content": "题目内容",
      "answer": "答案",
      "solution": "解题步骤"
    }
  ]
}"""

EXAM_PAPER_PROMPT = """你是一个小学出题老师。请生成一份{subject_name}模拟试卷。

要求：
- 年级：{grade}
- 包含题型：{question_types}
- 总题数：{question_count}
- 难度：{difficulty}/5
- 适合小学生理解

按以下 JSON 格式返回：
{
  "title": "试卷标题",
  "questions": [
    {
      "number": 1,
      "type": "填空题/选择题/计算题/应用题",
      "content": "题目内容",
      "answer": "答案",
      "score": 5,
      "difficulty": 3
    }
  ],
  "total_score": 100
}"""
```

- [ ] **Step 3: 创建 service.py**

```python
import json
from sqlalchemy.orm import Session
from app.shared.ai_client import call_qwen_text
from app.modules.generate.prompts import SIMILAR_QUESTION_PROMPT, EXAM_PAPER_PROMPT
from app.modules.generate.models import ExamPaper


def generate_similar(db: Session, question_id: int) -> list[dict]:
    from app.modules.question.models import Question
    q = db.query(Question).filter(Question.id == question_id).first()
    if not q:
        return []

    prompt = SIMILAR_QUESTION_PROMPT.format(
        question_content=q.content,
        correct_answer=q.answer,
        knowledge_point="",
    )
    raw = call_qwen_text(prompt)
    data = json.loads(raw)
    return data.get("questions", [])


def generate_exam_paper(
    db: Session,
    subject_name: str,
    grade: str = "三年级",
    question_types: str = "填空、计算、应用",
    question_count: int = 10,
    difficulty: int = 3,
) -> dict:
    prompt = EXAM_PAPER_PROMPT.format(
        subject_name=subject_name,
        grade=grade,
        question_types=question_types,
        question_count=question_count,
        difficulty=difficulty,
    )
    raw = call_qwen_text(prompt)
    return json.loads(raw)
```

- [ ] **Step 4: 创建 router.py**

```python
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.shared.database import get_db
from app.modules.generate import service as gen_service

router = APIRouter(prefix="/api/generate", tags=["generate"])


@router.post("/similar/{question_id}")
def generate_similar(question_id: int, db: Session = Depends(get_db)):
    questions = gen_service.generate_similar(db, question_id)
    return {"original_question_id": question_id, "similar_questions": questions}


@router.post("/exam-paper")
def generate_exam_paper(
    subject: str = Query(...),
    grade: str = "三年级",
    types: str = "填空、计算、应用",
    count: int = 10,
    db: Session = Depends(get_db),
):
    paper = gen_service.generate_exam_paper(db, subject, grade, types, count)
    return paper
```

- [ ] **Step 5: 提交**

```bash
git add backend/app/modules/generate/
git commit -m "feat: add generate module with similar questions and exam papers"
```

---

### Task 10: 分析模块 — 统计 API

**Files:**
- Create: `backend/app/modules/analysis/__init__.py`
- Create: `backend/app/modules/analysis/models.py`
- Create: `backend/app/modules/analysis/service.py`
- Create: `backend/app/modules/analysis/router.py`
- Modify: `backend/app/main.py`

- [ ] **Step 1: 创建 analysis/service.py**

```python
from datetime import datetime, timedelta
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.modules.question.models import Question, MistakeRecord
import json


def get_subject_trend(db: Session, subject_id: int, days: int = 30) -> list[dict]:
    """获取近N天每日正确率"""
    since = datetime.now() - timedelta(days=days)

    results = (
        db.query(
            func.date(MistakeRecord.created_at).label("date"),
            func.count(MistakeRecord.id).label("total"),
            func.sum(MistakeRecord.is_correct.cast(int)).label("correct"),
        )
        .join(Question)
        .filter(Question.subject_id == subject_id)
        .filter(MistakeRecord.created_at >= since)
        .group_by(func.date(MistakeRecord.created_at))
        .all()
    )

    return [
        {
            "date": str(r.date),
            "total": r.total,
            "correct": r.correct or 0,
            "rate": round((r.correct or 0) / r.total * 100, 1),
        }
        for r in results
    ]


def get_error_distribution(db: Session, subject_id: int) -> list[dict]:
    """错误类型分布"""
    results = (
        db.query(
            MistakeRecord.error_type,
            func.count(MistakeRecord.id).label("count"),
        )
        .join(Question)
        .filter(Question.subject_id == subject_id)
        .filter(MistakeRecord.is_correct == False)
        .group_by(MistakeRecord.error_type)
        .all()
    )

    total = sum(r.count for r in results)
    return [
        {
            "error_type": r.error_type or "未知",
            "count": r.count,
            "percentage": round(r.count / total * 100, 1) if total > 0 else 0,
        }
        for r in results
    ]


def get_weak_points(db: Session, subject_id: int, top_n: int = 5) -> list[dict]:
    """薄弱知识点 TOP N"""
    results = (
        db.query(
            Question.knowledge_point_id,
            func.count(MistakeRecord.id).label("error_count"),
        )
        .join(MistakeRecord)
        .filter(Question.subject_id == subject_id)
        .filter(MistakeRecord.is_correct == False)
        .group_by(Question.knowledge_point_id)
        .order_by(func.count(MistakeRecord.id).desc())
        .limit(top_n)
        .all()
    )

    return [
        {
            "knowledge_point_id": r.knowledge_point_id,
            "error_count": r.error_count,
        }
        for r in results
    ]
```

- [ ] **Step 2: 创建 router.py**

```python
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.shared.database import get_db
from app.modules.analysis import service as analysis_service

router = APIRouter(prefix="/api/analysis", tags=["analysis"])


@router.get("/trend/{subject_id}")
def trend(subject_id: int, days: int = Query(30), db: Session = Depends(get_db)):
    return analysis_service.get_subject_trend(db, subject_id, days)


@router.get("/errors/{subject_id}")
def error_distribution(subject_id: int, db: Session = Depends(get_db)):
    return analysis_service.get_error_distribution(db, subject_id)


@router.get("/weak-points/{subject_id}")
def weak_points(subject_id: int, top_n: int = 5, db: Session = Depends(get_db)):
    return analysis_service.get_weak_points(db, subject_id, top_n)
```

- [ ] **Step 3: 创建前端 Analysis.vue**

```vue
<template>
  <div class="analysis-page">
    <header>
      <h1>📊 学习统计</h1>
      <div class="tabs">
        <button v-for="s in subjects" :key="s.id" @click="selectSubject(s.id)"
          :class="{ active: currentSubject === s.id }">
          {{ s.icon }} {{ s.name }}
        </button>
      </div>
    </header>

    <div class="stats-grid">
      <div class="stat-card">
        <h3>正确率趋势（近30天）</h3>
        <!-- 这里后续用 Chart.js 渲染折线图 -->
        <pre>{{ JSON.stringify(trendData, null, 2) }}</pre>
      </div>

      <div class="stat-card">
        <h3>错误类型分布</h3>
        <div v-for="e in errorDist" :key="e.error_type" class="error-bar">
          <span>{{ e.error_type }}</span>
          <div class="bar-bg">
            <div class="bar-fill" :style="{ width: e.percentage + '%' }"></div>
          </div>
          <span>{{ e.percentage }}%</span>
        </div>
      </div>

      <div class="stat-card">
        <h3>薄弱知识点 TOP 5</h3>
        <ol>
          <li v-for="w in weakPoints" :key="w.knowledge_point_id">
            知识点 #{{ w.knowledge_point_id }} — 错 {{ w.error_count }} 次
          </li>
        </ol>
      </div>
    </div>
  </div>
</template>
```

- [ ] **Step 4: 提交**

```bash
git add backend/app/modules/analysis/ frontend/src/views/Analysis.vue
git commit -m "feat: add analysis module with trend, error distribution, weak points"
```

---

### Task 11: 前端孩子端 — 复习模式

**Files:**
- Create: `frontend/src/views/student/Dashboard.vue`
- Create: `frontend/src/views/student/Review.vue`
- Create: `frontend/src/views/student/Quiz.vue`
- Modify: `frontend/src/router/index.ts`

- [ ] **Step 1: 创建学生端路由**

```typescript
{
  path: '/student',
  component: () => import('../views/student/Dashboard.vue'),
  children: [
    { path: 'review/:subjectId', component: () => import('../views/student/Review.vue') },
    { path: 'quiz/:subjectId', component: () => import('../views/student/Quiz.vue') },
  ],
}
```

- [ ] **Step 2: 创建 Dashboard.vue**

```vue
<template>
  <div class="student-dashboard">
    <header class="student-header">
      <h1>🌟 我的错题本</h1>
      <p class="subtitle">今天也要加油哦！</p>
    </header>
    <div class="subject-cards">
      <div v-for="subject in subjects" :key="subject.id" class="subject-card student-card"
        @click="$router.push(`/student/review/${subject.id}`)">
        <span class="icon">{{ subject.icon }}</span>
        <h2>{{ subject.name }}</h2>
        <!-- 统计信息后续加 -->
        <button class="btn-start">开始复习</button>
      </div>
    </div>
    <div class="progress-section">
      <h3>🔥 连续学习 3 天</h3>
      <div class="stars">⭐⭐⭐</div>
    </div>
  </div>
</template>

<style scoped>
.student-header {
  text-align: center;
  padding: 32px 0;
}
.student-card {
  text-align: center;
  padding: 32px;
  border-radius: 16px;
  cursor: pointer;
  transition: transform 0.2s;
}
.student-card:hover {
  transform: scale(1.02);
}
.student-card .icon {
  font-size: 48px;
}
.btn-start {
  margin-top: 16px;
  padding: 12px 32px;
  border: none;
  border-radius: 24px;
  background: var(--accent, #4a90d9);
  color: white;
  font-size: 16px;
  cursor: pointer;
}
</style>
```

- [ ] **Step 3: 提交**

```bash
git add frontend/src/views/student/
git commit -m "feat: add student mode with dashboard and review pages"
```

---

### Task 12: 集成测试与启动脚本

**Files:**
- Create: `backend/run.py`（一键启动脚本）
- Modify: `backend/tests/test_ocr.py`（集成测试）

- [ ] **Step 1: 创建 run.py**

```python
"""一键启动脚本"""
import uvicorn
import webbrowser
from pathlib import Path

# 确保上传目录存在
Path("app/static/uploads").mkdir(parents=True, exist_ok=True)

if __name__ == "__main__":
    print("📘 错题本启动中...")
    print("PC 端访问: http://localhost:8000")
    print("手机端: 在手机上访问同一局域网 IP + 端口即可")
    print("按 Ctrl+C 停止服务")
    webbrowser.open("http://localhost:8000")
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
```

- [ ] **Step 2: 添加前端构建 + 后端运行说明**

```bash
# 开发模式（前后端分离）
# 终端1：后端
cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 终端2：前端
cd frontend && npm run dev

# 访问 http://localhost:5173
```

- [ ] **Step 3: 提交**

```bash
git add backend/run.py
git commit -m "chore: add run script and integration test"
```

---

### Task 13: 最终验证

- [ ] **Step 1: 运行全部测试**

```bash
cd backend && pytest -v
```

- [ ] **Step 2: 启动后端**

```bash
cd backend && cp .env.example .env
# 编辑 .env 填入真实 API Key
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- [ ] **Step 3: 启动前端（需要另一终端）**

```bash
cd frontend && npm run dev
```

- [ ] **Step 4: 端到端验证**
   - 打开浏览器访问 http://localhost:5173
   - 首页显示三科
   - 录入页生成二维码
   - API 健康检查返回 ok

## 实施顺序概要

| 阶段 | 任务 | 依赖 |
|------|------|------|
| Phase 1: 基础 | Task 1: 脚手架 | - |
|  | Task 2: 知识点模块 | Task 1 |
|  | Task 3: 认证模块 | Task 1 |
| Phase 2: 后端核心 | Task 4: 上传模块 | Task 1, 3 |
|  | Task 5: OCR 模块 | Task 1, 4 |
|  | Task 6: 题库模块 | Task 1, 2, 5 |
| Phase 3: 前端 | Task 7: Vue 基础 | Task 1 |
|  | Task 8: 录入/确认页 | Task 7 |
| Phase 4: 高级功能 | Task 9: 出题模块 | Task 1, 6 |
|  | Task 10: 分析模块 | Task 1, 6 |
|  | Task 11: 学生端 | Task 7 |
| Phase 5: 整合 | Task 12: 集成测试 | 全部 |
|  | Task 13: 最终验证 | Task 12 |
