from typing import List, Optional, Dict, Any
import logging
from datetime import datetime, timedelta

from src.entity.models.tts_request import TTSRequest, VoiceConfig, AudioConfig
from src.entity.models.tts_response import TTSResponse
from src.interactor.ai_services.tts_interactor import TTSInteractor


class TTSManager:
    def __init__(self, project_id: str, bucket_name: str, enable_repository: bool = True):
        self.project_id = project_id
        self.bucket_name = bucket_name
        self.tts_interactor = TTSInteractor(project_id, bucket_name, enable_repository)
        self.logger = logging.getLogger(__name__)

    def process_text_to_speech(
        self,
        text: str,
        language_code: str = "en-US",
        voice_name: Optional[str] = None,
        ssml_gender: str = "NEUTRAL",
        audio_encoding: str = "MP3",
        speaking_rate: float = 1.0,
        pitch: float = 0.0,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:

        try:
            from src.entity.models.tts_request import VoiceGender, AudioEncoding

            voice_config = VoiceConfig(
                language_code=language_code,
                name=voice_name,
                ssml_gender=VoiceGender[ssml_gender.upper()]
            )

            audio_config = AudioConfig(
                audio_encoding=AudioEncoding[audio_encoding.upper()],
                speaking_rate=speaking_rate,
                pitch=pitch
            )

            request = TTSRequest(
                text=text,
                voice=voice_config,
                audio_config=audio_config,
                user_id=user_id
            )

            response = self.tts_interactor.synthesize_speech(request)

            return {
                'success': True,
                'request_id': response.request_id,
                'audio_url': response.audio_url,
                'duration_seconds': response.duration_seconds,
                'character_count': response.character_count,
                'processing_time_ms': response.processing_time_ms,
                'metadata': response.metadata
            }

        except Exception as e:
            self.logger.error(f"TTS processing failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'error_type': type(e).__name__
            }

    def process_ssml_to_speech(
        self,
        ssml: str,
        language_code: str = "en-US",
        voice_name: Optional[str] = None,
        audio_encoding: str = "MP3",
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:

        try:
            from src.entity.models.tts_request import VoiceGender, AudioEncoding, VoiceConfig, AudioConfig

            voice_config = VoiceConfig(
                language_code=language_code,
                name=voice_name,
                ssml_gender=VoiceGender.NEUTRAL
            )

            audio_config = AudioConfig(
                audio_encoding=AudioEncoding[audio_encoding.upper()]
            )

            request = TTSRequest(
                ssml=ssml,
                voice=voice_config,
                audio_config=audio_config,
                user_id=user_id
            )

            response = self.tts_interactor.synthesize_speech(request)

            return {
                'success': True,
                'request_id': response.request_id,
                'audio_url': response.audio_url,
                'duration_seconds': response.duration_seconds,
                'character_count': response.character_count,
                'processing_time_ms': response.processing_time_ms,
                'metadata': response.metadata
            }

        except Exception as e:
            self.logger.error(f"SSML TTS processing failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'error_type': type(e).__name__
            }

    def get_available_voices(self, language_code: Optional[str] = None) -> Dict[str, Any]:
        try:
            voices = self.tts_interactor.get_available_voices(language_code)

            categorized_voices = {
                'standard': [],
                'wavenet': [],
                'neural2': [],
                'news': [],
                'studio': []
            }

            for voice in voices:
                voice_name = voice['name']
                if 'Wavenet' in voice_name:
                    categorized_voices['wavenet'].append(voice)
                elif 'Neural2' in voice_name:
                    categorized_voices['neural2'].append(voice)
                elif 'News' in voice_name:
                    categorized_voices['news'].append(voice)
                elif 'Studio' in voice_name:
                    categorized_voices['studio'].append(voice)
                else:
                    categorized_voices['standard'].append(voice)

            return {
                'success': True,
                'total_voices': len(voices),
                'voices': categorized_voices
            }

        except Exception as e:
            self.logger.error(f"Failed to get available voices: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    def get_user_history(self, user_id: str, limit: int = 10) -> Dict[str, Any]:
        try:
            requests = self.tts_interactor.repository.get_user_requests(user_id, limit)

            history = []
            for req in requests:
                history.append({
                    'request_id': req.id,
                    'text': req.text[:100] + '...' if len(req.text) > 100 else req.text,
                    'language_code': req.voice.language_code,
                    'voice_name': req.voice.name,
                    'created_at': req.created_at.isoformat() if req.created_at else None
                })

            return {
                'success': True,
                'user_id': user_id,
                'history': history,
                'count': len(history)
            }

        except Exception as e:
            self.logger.error(f"Failed to get user history: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }