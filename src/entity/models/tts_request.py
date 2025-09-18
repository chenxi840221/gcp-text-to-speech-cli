from dataclasses import dataclass
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum


class VoiceGender(Enum):
    NEUTRAL = "NEUTRAL"
    MALE = "MALE"
    FEMALE = "FEMALE"


class AudioEncoding(Enum):
    MP3 = "MP3"
    LINEAR16 = "LINEAR16"
    OGG_OPUS = "OGG_OPUS"
    MULAW = "MULAW"
    ALAW = "ALAW"


@dataclass
class VoiceConfig:
    language_code: str = "en-US"
    name: Optional[str] = None
    ssml_gender: VoiceGender = VoiceGender.NEUTRAL


@dataclass
class AudioConfig:
    audio_encoding: AudioEncoding = AudioEncoding.MP3
    speaking_rate: float = 1.0
    pitch: float = 0.0
    volume_gain_db: float = 0.0
    sample_rate_hertz: Optional[int] = None
    effects_profile_id: Optional[list] = None


@dataclass
class TTSRequest:
    id: Optional[str] = None
    text: str = ""
    ssml: Optional[str] = None
    voice: VoiceConfig = None
    audio_config: AudioConfig = None
    user_id: Optional[str] = None
    created_at: datetime = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.voice is None:
            self.voice = VoiceConfig()
        if self.audio_config is None:
            self.audio_config = AudioConfig()
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.metadata is None:
            self.metadata = {}