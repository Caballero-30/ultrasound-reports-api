# Veterinary Reports API

[![Python](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-available-brightgreen)](https://fastapi.tiangolo.com/)

## Overview
A small FastAPI service that processes veterinary ultrasound PDF reports using Google Document AI, extracts key fields, saves report metadata to Firestore, and uploads extracted images to Google Cloud Storage (GCS). The API exposes endpoints to create a report from a PDF and to fetch a saved report with signed image URLs.

## Table of contents

- [Key features](#key-features)
- [Prerequisites](#prerequisites)
- [Environment variables](#environment-variables)
- [Installation](#installation)
- [Running the API (development)](#running-the-api-development)
- [Authentication](#authentication)
- [API examples](#api-examples)
- [Project structure (high level)](#project-structure-high-level)
- [Google Cloud notes](#google-cloud-notes)
- [Docker](#docker)

## Key features

- Upload a PDF report and automatically extract structured fields (patient, owner, veterinarian, diagnosis, recommendations).
- Extract ultrasound images from the PDF and store them in GCS.
- Persist report metadata in Firestore.
- Signed, time-limited URLs for stored images.

## Prerequisites

- Python 3.11+.
- Google Cloud project with:
  - Document AI processor configured and ready to process PDFs.
  - Firestore database.
  - GCS bucket for report images.
- Service account JSON credentials with permissions for Document AI, Firestore, and Cloud Storage (do not commit credentials to the repo).

## Environment variables

Set these before running the service:

| Variable                         | Description                                                                                        |
|----------------------------------|----------------------------------------------------------------------------------------------------|
| `GOOGLE_APPLICATION_CREDENTIALS` | Path to your service account JSON key file (optional if running on GCP with attached credentials). |
| `DOCUMENT_AI_PROJECT_ID`         | Google Cloud project id used for Document AI.                                                      |
| `DOCUMENT_AI_LOCATION`           | Document AI location (e.g. `us`, `eu`, or the processor region).                                   |
| `DOCUMENT_AI_PROCESSOR_ID`       | Document AI processor id used to parse the PDFs.                                                   |
| `GCS_BUCKET_NAME`                | GCS bucket where extracted images will be uploaded.                                                |
| `API_KEY`                        | Simple API key used to protect endpoints (sent in the `Authorization` header).                     |

> Note: The repository does not include a service account JSON key file. If you have one, set `GOOGLE_APPLICATION_CREDENTIALS` to its path on the machine running the service, except if running on GCP with attached credentials.

## Installation

1. Create and activate a virtual environment (PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
pip install -r requirements.txt
```

## Running the API (development)

Run the FastAPI app with Uvicorn from the project root:

```powershell
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

By default the app exposes:

- `GET /health` — simple healthcheck
- `POST /reports` — upload a PDF to create a report (requires `Authorization` header)
- `GET /reports/{report_id}` — retrieve a saved report (requires `Authorization` header)

## Authentication

A simple API key is used via the `Authorization` header. Set the API key in the environment variable `API_KEY`.

Example header:

```
Authorization: replace-with-secret
```

## API examples

Create a report (multipart form upload):

```bash
curl -X POST "http://localhost:8000/reports/" \
  -H "Authorization: replace-with-secret" \
  -F "file=@/path/to/ultrasound-report.pdf;type=application/pdf"
```

Successful response:

```json
{
  "id": "<uuid>"
}
```

Get a saved report:

```bash
curl -X GET "http://localhost:8000/reports/<uuid>" \
  -H "Authorization: replace-with-secret"
```

The response body contains the extracted fields and an array of images with signed URLs and `expires_in` (in milliseconds).

## Project structure (high level)

- `app/main.py` — FastAPI application entrypoint
- `app/api/routes/reports.py` — API routes for reports
- `app/services` — services for Firestore, GCS, and Document AI processing
- `app/models` — Pydantic models used by the API
- `requirements.txt` — pinned dependencies

## Google Cloud notes

- Ensure the service account JSON key has roles to call Document AI, read/write Firestore documents, and upload blobs to the configured GCS bucket.
- Document AI processors have quotas and may require enabling billing.
- If running outside GCP, set `GOOGLE_APPLICATION_CREDENTIALS` to the path of your service account file.

## Docker

A `Dockerfile` is present in the repo root.

Build and run (example):

```powershell
# Build
docker build -t ultrasound-reports-api:latest .

# Run
docker run -e API_KEY=replace-with-secret -p 8000:8000 ultrasound-reports-api:latest
```

