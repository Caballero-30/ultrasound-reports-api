from functools import lru_cache
from app.config.dependencies import get_env_settings
from app.services.firestore_client import get_firestore_client
from app.services.gcs_service import GCSService
from app.services.report_service import ReportService
from app.services.veterinary_document_service import VeterinaryDocumentService


@lru_cache
def get_veterinary_document_service() -> VeterinaryDocumentService:
    env_settings = get_env_settings()
    return VeterinaryDocumentService(env_settings)


@lru_cache
def get_gcs_service() -> GCSService:
    env_settings = get_env_settings()
    return GCSService(bucket_name=env_settings.bucket_name)


@lru_cache
def get_report_service() -> ReportService:
    return ReportService(
        firestore_client=get_firestore_client(),
        gcs_service=get_gcs_service(),
        document_service=get_veterinary_document_service(),
    )
