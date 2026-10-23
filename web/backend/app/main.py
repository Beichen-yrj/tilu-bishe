"""FastAPI 应用装配：CORS、路由注册、启动生命周期（建表、兼容迁移、默认管理员）与健康检查。"""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import inspect, text
from sqlalchemy.orm import Session

from . import models  # noqa: F401  （导入实体以注册元数据）
from .api.v1 import ai, assessments, auth, feedback, hazard_assessments
from .core.config import get_settings
from .core.database import Base, engine, get_db
from .schemas import HealthResponse
from .services.auth_service import ensure_default_admin


def ensure_schema_compatibility() -> None:
    inspector = inspect(engine)
    tables = set(inspector.get_table_names())
    if "users" in tables and "avatar_data" not in {column["name"] for column in inspector.get_columns("users")}:
        column_type = "LONGTEXT" if engine.dialect.name == "mysql" else "TEXT"
        with engine.begin() as connection:
            connection.execute(text(f"ALTER TABLE users ADD COLUMN avatar_data {column_type} NULL"))
    if "hazard_assessments" in tables and "bureau" not in {column["name"] for column in inspector.get_columns("hazard_assessments")}:
        with engine.begin() as connection:
            connection.execute(text("ALTER TABLE hazard_assessments ADD COLUMN bureau VARCHAR(80) NOT NULL DEFAULT ''"))
    if "hazard_assessments" in tables:
        columns = {column["name"] for column in inspector.get_columns("hazard_assessments")}
        additions = {
            "rectification_photo_name": "VARCHAR(180) NOT NULL DEFAULT ''",
            "rectification_photo_data": "LONGTEXT NULL" if engine.dialect.name == "mysql" else "TEXT NULL",
            "review_result": "VARCHAR(20) NOT NULL DEFAULT ''",
            "review_measured_value": "VARCHAR(100) NOT NULL DEFAULT ''",
            "review_standard_value": "VARCHAR(160) NOT NULL DEFAULT ''",
            "rectification_log": "JSON NULL" if engine.dialect.name == "mysql" else "TEXT NULL",
            "workflow_version": "INTEGER NOT NULL DEFAULT 0",
        }
        missing = {name: definition for name, definition in additions.items() if name not in columns}
        if missing:
            with engine.begin() as connection:
                for name, definition in missing.items():
                    connection.execute(text(f"ALTER TABLE hazard_assessments ADD COLUMN {name} {definition}"))


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    ensure_schema_compatibility()
    ensure_default_admin()
    yield


settings = get_settings()
app = FastAPI(
    title="铁路危险货物运输双重预防机制平台 API",
    version="0.1.0",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=list(settings.cors_origins),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)
app.include_router(auth.router)
app.include_router(feedback.router)
app.include_router(assessments.router)
app.include_router(hazard_assessments.router)
app.include_router(ai.router)


@app.get("/api/health", response_model=HealthResponse, tags=["system"])
def health(db: Session = Depends(get_db)) -> HealthResponse:
    db.execute(text("SELECT 1"))
    return HealthResponse(status="ok", database="connected")
