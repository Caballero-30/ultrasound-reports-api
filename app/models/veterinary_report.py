from dataclasses import dataclass
from typing import Optional


@dataclass
class VeterinaryReport:
    patient: Optional[str] = None
    owner: Optional[str] = None
    veterinarian: Optional[str] = None
    diagnosis: Optional[str] = None
    recommendations: Optional[str] = None