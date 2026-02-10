from uuid import UUID
from pydantic import BaseModel


class ReportIdResponse(BaseModel):
    id: UUID