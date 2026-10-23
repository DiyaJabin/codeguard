import json
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, DateTime, Text
from ..db import Base
class Review(Base):
    __tablename__ = "reviews"
    review_id = Column(String(36), primary_key=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    language = Column(String(20), nullable=False)
    filename = Column(String(255), default="untitled", nullable=False)
    analysis_provider = Column(String(50), nullable=False)
    summary = Column(Text, nullable=False)
    total_issues = Column(Integer, default=0, nullable=False)
    severity_counts_json = Column(Text, default="{}", nullable=False)
    category_counts_json = Column(Text, default="{}", nullable=False)
    findings_json = Column(Text, default="[]", nullable=False)
    def to_dict(self):
        return {"review_id": self.review_id, "created_at": self.created_at.isoformat(), "language": self.language, "filename": self.filename, "analysis_provider": self.analysis_provider, "summary": self.summary, "total_issues": self.total_issues, "severity_counts": json.loads(self.severity_counts_json), "category_counts": json.loads(self.category_counts_json), "findings": json.loads(self.findings_json)}
