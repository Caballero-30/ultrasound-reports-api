from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4
from fastapi import HTTPException
from google.cloud import firestore
from app.models.firestore_veterinary_report import FirestoreVeterinaryReport, ReportImage
from app.services.gcs_service import GCSService
from uuid import UUID
from app.services.veterinary_document_service import VeterinaryDocumentService


class ReportService:
    GCS_IMG_URL_EXPIRATION_MINUTES = 60

    def __init__(
        self,
        firestore_client: firestore.Client,
        gcs_service: GCSService,
        document_service: VeterinaryDocumentService,
    ):
        self.db = firestore_client
        self.gcs_service = gcs_service
        self.document_service = document_service

    def save_report(self, report: FirestoreVeterinaryReport) -> UUID:
        report_id = report.id or uuid4()
        doc_ref = self.db.collection("reports").document(str(report_id))

        data_to_save = report.model_dump(
            exclude={"id", "images__url", "images__expires_in"}
        )

        for i, img in enumerate(report.images):
            data_to_save["images"][i] = {"path": img.path}

        data_to_save["created_at"] = datetime.now(timezone.utc)
        doc_ref.set(data_to_save)

        return report_id

    def get_report(self, report_id: UUID) -> Optional[FirestoreVeterinaryReport]:
        doc_ref = self.db.collection("reports").document(str(report_id))
        doc = doc_ref.get()
        if not doc.exists:
            raise HTTPException(status_code=404, detail="Report not found")

        report = FirestoreVeterinaryReport(**doc.to_dict(), id=report_id)

        for img in report.images:
            img.url = self.gcs_service.generate_signed_url(img.path, self.GCS_IMG_URL_EXPIRATION_MINUTES)
            img.expires_in = self.GCS_IMG_URL_EXPIRATION_MINUTES * 60 * 1000

        return report

    def create_from_pdf(self, pdf_bytes: bytes) -> UUID:
        report_id = uuid4()

        report = self.document_service.process_pdf(pdf_bytes)
        images = self.document_service.extract_images(pdf_bytes)

        paths = []
        for image_bytes in images:
            destination_path = f"reports/{report_id}/{uuid4()}.png"
            self.gcs_service.upload_bytes(image_bytes, destination_path, "image/png")

            paths.append(destination_path)

        firestore_report = FirestoreVeterinaryReport(
            id=report_id,
            patient=report.patient,
            owner=report.owner,
            veterinarian=report.veterinarian,
            diagnosis=report.diagnosis,
            recommendations=report.recommendations,
            images=[ReportImage(path=path) for path in paths],
        )

        self.save_report(firestore_report)
        return report_id
