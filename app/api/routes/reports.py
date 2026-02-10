from uuid import UUID
from fastapi import APIRouter, Depends, UploadFile, File
from app.core.auth import verify_token
from app.models.firestore_veterinary_report import FirestoreVeterinaryReport
from app.models.report_id_response import ReportIdResponse
from app.services.dependencies import get_report_service
from app.services.report_service import ReportService

reports_router = APIRouter(prefix="/reports", tags=["reports"])


@reports_router.post("/", dependencies=[Depends(verify_token)], response_model=ReportIdResponse)
async def create_report(
    file: UploadFile = File(...),
    report_service: ReportService = Depends(get_report_service)
):
    file_bytes = await file.read()
    report_id = report_service.create_from_pdf(pdf_bytes=file_bytes)

    return {"id": report_id}


@reports_router.get("/{report_id}", dependencies=[Depends(verify_token)], response_model=FirestoreVeterinaryReport)
def get_report(report_id: UUID, service: ReportService = Depends(get_report_service)):
    return service.get_report(report_id)
