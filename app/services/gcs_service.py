from datetime import timedelta
from google.auth import compute_engine
from google.cloud import storage
import google.auth
from google.auth.transport import requests


class GCSService:
    def __init__(self, bucket_name: str):
        self.bucket_name = bucket_name
        self.client = storage.Client()
        self.bucket = self.client.bucket(bucket_name)

    def upload_bytes(
        self,
        content: bytes,
        destination_path: str,
        content_type: str,
    ) -> str:
        blob = self.bucket.blob(destination_path)
        blob.upload_from_string(content, content_type=content_type)

        return f"gs://{self.bucket_name}/{destination_path}"

    def generate_signed_url(
        self,
        blob_path: str,
        expires_minutes: int = 60,
    ) -> str:
        credentials, _ = google.auth.default()
        blob = self.bucket.blob(blob_path)
        auth_request = requests.Request()
        credentials.refresh(auth_request)

        signing_credentials = compute_engine.IDTokenCredentials(
            auth_request,
            "",
            service_account_email=credentials.service_account_email
        )

        return blob.generate_signed_url(
            version="v4",
            expiration=timedelta(minutes=expires_minutes),
            method="GET",
            credentials=signing_credentials
        )
