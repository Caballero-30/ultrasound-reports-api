from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from uuid import UUID


class ReportImage(BaseModel):
    path: str
    url: Optional[str] = None
    expires_in: Optional[int] = None

class FirestoreVeterinaryReport(BaseModel):
    id: Optional[UUID] = None
    patient: Optional[str] = None
    owner: Optional[str] = None
    veterinarian: Optional[str] = None
    diagnosis: Optional[str] = None
    recommendations: Optional[str] = None
    images: List[ReportImage] = Field(default_factory=list)
    created_at: Optional[datetime] = None
