import difflib
import io
import re
from typing import Optional, List
import fitz
from PIL import Image
from google.api_core.client_options import ClientOptions
from google.cloud import documentai_v1 as documentai
from app.config.env_settings import EnvSettings
from app.models.veterinary_report import VeterinaryReport


class VeterinaryDocumentService:
    MAX_PAGES_PER_SHARD = 15
    ULTRASOUND_MIN_WIDTH = 1300
    LABEL_ALIASES = {
        "patient": ["Paciente", "Paciente:", "Nombre paciente", "Nombre"],
        "owner": ["Propietario", "Dueño", "Dueña", "Propietario:"],
        "veterinarian": ["Veterinario", "Médico Veterinario", "Veterinario:", "Profesional"],
        "diagnosis": ["Diagnóstico", "Diagnostico", "Impresión", "Impresión Diagnóstica"],
        "recommendations": ["Recomendaciones", "Recomendación", "Indicaciones", "Tratamiento recomendado"]
    }

    def __init__(self, settings: EnvSettings):
        self.client = documentai.DocumentProcessorServiceClient(
            client_options=ClientOptions(
                api_endpoint=f"{settings.location}-documentai.googleapis.com:443"
            )
        )

        self.processor_name = self.client.processor_path(
            settings.project_id,
            settings.location,
            settings.processor_id
        )

    def process_pdf(self, pdf_bytes: bytes) -> VeterinaryReport:
        text = self._process_pdf_sharded(pdf_bytes)

        return self._extract_fields_from_text(text)

    def extract_images(self, pdf_bytes: bytes) -> List[bytes]:
        return self._extract_images_from_pdf(pdf_bytes)

    def _process_pdf_sharded(self, pdf_bytes: bytes) -> str:
        texts = []

        for shard_bytes in self._pdf_shards(pdf_bytes):
            raw_doc = documentai.RawDocument(
                content=shard_bytes,
                mime_type="application/pdf"
            )
            request = documentai.ProcessRequest(
                name=self.processor_name,
                raw_document=raw_doc,
                imageless_mode=True
            )
            res = self.client.process_document(request=request)
            texts.append(res.document.text or "")

        return "\n\n".join(t for t in texts if t).strip()

    def _pdf_shards(self, pdf_bytes: bytes):
        src = fitz.open(stream=pdf_bytes, filetype="pdf")
        total = len(src)

        for start in range(0, total, self.MAX_PAGES_PER_SHARD):
            end = min(start + self.MAX_PAGES_PER_SHARD - 1, total - 1)
            shard = fitz.open()
            shard.insert_pdf(src, from_page=start, to_page=end)
            yield shard.write()
            shard.close()

        src.close()

    def _extract_fields_from_text(self, text: str) -> VeterinaryReport:
        lines = [re.sub(r"\s+", " ", l).strip() for l in text.splitlines()]
        results = {k: None for k in self.LABEL_ALIASES}

        indexed = [(i, l) for i, l in enumerate(lines) if l]

        for idx, line in indexed:
            for field, aliases in self.LABEL_ALIASES.items():
                found = self._best_label_in_line(line, aliases)
                if not found:
                    continue

                same_line = bool(re.search(
                    rf"{re.escape(found)}\s*[:\-]\s*(.+)", line, re.IGNORECASE
                ))

                value = self._extract_after_label(
                    lines, idx, found, same_line
                )

                if value and (
                        not results[field] or len(value) > len(results[field])
                ):
                    results[field] = value

        return VeterinaryReport(**results)

    def _clean_value(self, val: Optional[str]) -> Optional[str]:
        if not val:
            return None

        v = val.strip()
        v = re.sub(r'^[\s\:\-\–\—\•\u2022\·]+', '', v)
        v = re.sub(r'[\s\:\-\–\—\•\u2022\·]+$', '', v)
        v = re.sub(r'\s{2,}', ' ', v)

        return v or None

    def _extract_after_label(
            self,
            lines: List[str],
            label_idx: int,
            label_text: str,
            same_line: bool
    ) -> Optional[str]:
        alias = label_text.strip(":")
        if same_line:
            m = re.search(
                rf"{re.escape(alias)}\s*[:\-]\s*(.+)",
                lines[label_idx],
                re.IGNORECASE
            )
            if m:
                return self._clean_value(m.group(1))

        collected = []
        for i in range(label_idx + 1, min(label_idx + 7, len(lines))):
            ln = lines[i]
            if not ln:
                break
            if ":" in ln:
                break
            collected.append(ln)

        return self._clean_value(" ".join(collected))

    def _best_label_in_line(self, line: str, aliases: List[str]) -> Optional[str]:
        for a in aliases:
            if re.search(rf"\b{re.escape(a.strip(':'))}\b", line, re.IGNORECASE):
                return a

        words = re.findall(r"[A-Za-zÁÉÍÓÚÑáéíóúñ]+", line)
        token = " ".join(words[:2])
        match = difflib.get_close_matches(token, aliases, n=1, cutoff=0.75)
        return match[0] if match else None

    def _is_valid_ultrasound_image(self, base_image: dict) -> bool:
        if not base_image or "image" not in base_image:
            return False

        width = base_image.get("width")

        if width is None:
            try:
                with Image.open(io.BytesIO(base_image["image"])) as im:
                    width = im.width
            except Exception:
                return False

        return width >= self.ULTRASOUND_MIN_WIDTH

    def _extract_images_from_pdf(self, pdf_bytes: bytes) -> List[bytes]:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        images: list[bytes] = []

        for page_index in range(len(doc)):
            for img_index, img in enumerate(doc[page_index].get_images(full=True)):
                try:
                    base_image = doc.extract_image(img[0])

                    if not self._is_valid_ultrasound_image(base_image):
                        continue

                    images.append(base_image.get("image"))

                except Exception:
                    continue

        return images
