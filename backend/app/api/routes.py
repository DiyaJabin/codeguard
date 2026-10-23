import json
from uuid import uuid4
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form
from pydantic import BaseModel, Field, field_validator
from sqlalchemy.orm import Session
from ..core.config import settings
from ..db import get_db
from ..models.review import Review
from ..providers.mock import MockReviewProvider
router=APIRouter(prefix="/api"); LANGUAGES={"Python","Java"}
class ReviewRequest(BaseModel):
    code:str=Field(min_length=1); language:str; filename:str=Field(default="untitled",max_length=255)
    @field_validator("language")
    @classmethod
    def valid_language(cls,v):
        if v not in LANGUAGES: raise ValueError("language must be Python or Java")
        return v
    @field_validator("code")
    @classmethod
    def valid_size(cls,v):
        if len(v.encode())>settings.max_code_bytes: raise ValueError("code exceeds 100 KB limit")
        return v
def save(db,req,result):
    r=Review(review_id=str(uuid4()),created_at=datetime.now(timezone.utc),language=req.language,filename=req.filename,analysis_provider=result["analysis_provider"],summary=result["summary"],total_issues=result["total_issues"],severity_counts_json=json.dumps(result["severity_counts"]),category_counts_json=json.dumps(result["category_counts"]),findings_json=json.dumps(result["findings"])); db.add(r); db.commit(); db.refresh(r); return r.to_dict()
@router.get("/config")
def config(): return {"environment":settings.app_env,"ai_provider":settings.ai_provider,"bedrock_enabled":settings.bedrock_enabled,"supported_languages":sorted(LANGUAGES),"version":"1.0.0","max_code_bytes":settings.max_code_bytes}
@router.post("/reviews")
def create(req:ReviewRequest,db:Session=Depends(get_db)): return save(db,req,MockReviewProvider().analyze(req.code,req.language))
@router.post("/reviews/upload")
async def upload(language:str=Form(...),file:UploadFile=File(...),db:Session=Depends(get_db)):
    suffix=".py" if language=="Python" else ".java"
    if language not in LANGUAGES or not file.filename or not file.filename.lower().endswith(suffix): raise HTTPException(422,"unsupported file type")
    data=await file.read(settings.max_code_bytes+1)
    if len(data)>settings.max_code_bytes: raise HTTPException(413,"file exceeds 100 KB limit")
    try: code=data.decode("utf-8")
    except UnicodeDecodeError: raise HTTPException(422,"file must be UTF-8 text")
    req=ReviewRequest(code=code,language=language,filename=file.filename)
    return save(db,req,MockReviewProvider().analyze(code,language))
@router.get("/reviews")
def listing(page:int=Query(1,ge=1),page_size:int=Query(20,ge=1,le=100),search:str="",severity:str="",db:Session=Depends(get_db)):
    q=db.query(Review).order_by(Review.created_at.desc())
    if search:q=q.filter((Review.filename.ilike(f"%{search}%"))|(Review.language.ilike(f"%{search}%")))
    items=[r.to_dict() for r in q.offset((page-1)*page_size).limit(page_size).all()]
    if severity:items=[r for r in items if r["severity_counts"].get(severity,0)>0]
    return {"items":items,"page":page,"page_size":page_size,"has_more":len(items)==page_size}
@router.get("/reviews/{review_id}")
def get_one(review_id:str,db:Session=Depends(get_db)):
    r=db.get(Review,review_id)
    if not r:raise HTTPException(404,"review not found")
    return r.to_dict()
@router.delete("/reviews/{review_id}")
def delete(review_id:str,db:Session=Depends(get_db)):
    r=db.get(Review,review_id)
    if not r:raise HTTPException(404,"review not found")
    db.delete(r);db.commit();return {"deleted":review_id}
@router.get("/stats")
def stats(db:Session=Depends(get_db)):
    rows=[r.to_dict() for r in db.query(Review).all()]; langs={}; sev={s:0 for s in ["Critical","High","Medium","Low","Informational"]}; cats={}; days={}
    for r in rows:
        langs[r["language"]]=langs.get(r["language"],0)+1; day=r["created_at"][:10]; days[day]=days.get(day,0)+1
        for k,v in r["severity_counts"].items():sev[k]=sev.get(k,0)+v
        for k,v in r["category_counts"].items():cats[k]=cats.get(k,0)+v
    total=sum(r["total_issues"] for r in rows)
    return {"total_reviews":len(rows),"total_issues":total,"high_severity_issues":sev.get("High",0)+sev.get("Critical",0),"average_issues_per_review":round(total/len(rows),1) if rows else 0,"by_language":langs,"severity":sev,"categories":cats,"over_time":[{"date":k,"reviews":v} for k,v in sorted(days.items())]}
