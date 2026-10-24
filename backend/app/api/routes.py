import os
from fastapi import APIRouter, HTTPException, Query, UploadFile, File, Form
from pydantic import BaseModel, Field, field_validator

from ..core.config import settings
from ..providers.mock import MockReviewProvider
from ..repositories.reviews import DynamoReviewRepository


router = APIRouter(prefix="/api")
LANGUAGES = {"Python", "Java"}


class ReviewRequest(BaseModel):
    code: str = Field(min_length=1)
    language: str
    filename: str = Field(default="untitled", max_length=255)

    @field_validator("language")
    @classmethod
    def valid_language(cls, v):
        if v not in LANGUAGES:
            raise ValueError("language must be Python or Java")
        return v

    @field_validator("code")
    @classmethod
    def valid_size(cls, v):
        if len(v.encode()) > settings.max_code_bytes:
            raise ValueError("code exceeds 100 KB limit")
        return v


def get_repository():
    if settings.app_env == "cloud":
        return DynamoReviewRepository()

    return None


def save_review(req, result):
    repository = get_repository()

    if repository is None:
        raise RuntimeError(
            "Local SQLite repository is temporarily disabled during cloud migration."
        )

    return repository.save(req, result)


@router.get("/config")
def config():
    return {
        "environment": settings.app_env,
        "ai_provider": settings.ai_provider,
        "bedrock_enabled": settings.bedrock_enabled,
        "supported_languages": sorted(LANGUAGES),
        "version": "1.0.0",
        "max_code_bytes": settings.max_code_bytes,
    }


@router.post("/reviews")
def create(req: ReviewRequest):
    result = MockReviewProvider().analyze(req.code, req.language)
    return save_review(req, result)


@router.post("/reviews/upload")
async def upload(
    language: str = Form(...),
    file: UploadFile = File(...)
):
    suffix = ".py" if language == "Python" else ".java"

    if (
        language not in LANGUAGES
        or not file.filename
        or not file.filename.lower().endswith(suffix)
    ):
        raise HTTPException(422, "unsupported file type")

    data = await file.read(settings.max_code_bytes + 1)

    if len(data) > settings.max_code_bytes:
        raise HTTPException(413, "file exceeds 100 KB limit")

    try:
        code = data.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(422, "file must be UTF-8 text")

    req = ReviewRequest(
        code=code,
        language=language,
        filename=file.filename
    )

    result = MockReviewProvider().analyze(code, language)
    return save_review(req, result)


@router.get("/reviews")
def listing(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: str = "",
    severity: str = ""
):
    repository = get_repository()

    if repository is None:
        raise HTTPException(503, "Cloud repository is not configured")

    return repository.list(
        page=page,
        page_size=page_size,
        search=search,
        severity=severity
    )


@router.get("/reviews/{review_id}")
def get_one(review_id: str):
    repository = get_repository()

    if repository is None:
        raise HTTPException(503, "Cloud repository is not configured")

    review = repository.get(review_id)

    if not review:
        raise HTTPException(404, "review not found")

    return review


@router.delete("/reviews/{review_id}")
def delete(review_id: str):
    repository = get_repository()

    if repository is None:
        raise HTTPException(503, "Cloud repository is not configured")

    review = repository.delete(review_id)

    if not review:
        raise HTTPException(404, "review not found")

    return {"deleted": review_id}


@router.get("/stats")
def stats():
    repository = get_repository()

    if repository is None:
        raise HTTPException(503, "Cloud repository is not configured")

    return repository.stats()