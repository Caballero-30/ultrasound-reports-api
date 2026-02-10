import os
from pydantic import Field
from pydantic_settings import BaseSettings


class EnvSettings(BaseSettings):
    project_id: str = Field(env="DOCUMENT_AI_PROJECT_ID", default=os.environ.get("DOCUMENT_AI_PROJECT_ID"))
    location: str = Field(env="DOCUMENT_AI_LOCATION", default=os.environ.get("DOCUMENT_AI_LOCATION"))
    processor_id: str = Field(env="DOCUMENT_AI_PROCESSOR_ID", default=os.environ.get("DOCUMENT_AI_PROCESSOR_ID"))
    bucket_name: str = Field(env="GCS_BUCKET_NAME", default=os.environ.get("GCS_BUCKET_NAME"))
    api_key: str = Field(env="API_KEY", default=os.environ.get("API_KEY"))
