from pydantic import BaseModel, Field
from typing import List

class UrlStitchRequest(BaseModel):
    image_urls: List[str] = Field(..., description="Array of chronologically ordered image URLs. Filenames must begin with HHMMSS_fff format.")
    fps: int = Field(default=30, ge=1, le=120)
    width: int = Field(default=1280, ge=320, le=3840)
    height: int = Field(default=720, ge=240, le=2160)
    mse_threshold: float = Field(default=5.0, ge=0.0, description="Mean Squared Error tolerance for frame deduplication.")
    max_idle_ms: int = Field(default=10000, ge=1000, description="Maximum artificial padding injected for idle layout states.")