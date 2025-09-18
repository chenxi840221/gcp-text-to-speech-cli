from dataclasses import dataclass
from typing import Optional, Dict, Any
from datetime import datetime


@dataclass
class TTSResponse:
    id: str
    request_id: str
    audio_content: bytes
    audio_url: Optional[str] = None
    duration_seconds: Optional[float] = None
    character_count: int = 0
    created_at: datetime = None
    processing_time_ms: Optional[int] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.metadata is None:
            self.metadata = {}