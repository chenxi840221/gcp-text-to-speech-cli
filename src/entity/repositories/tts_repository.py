from typing import List, Optional
from google.cloud import firestore
from datetime import datetime
import uuid

from src.entity.models.tts_request import TTSRequest
from src.entity.models.tts_response import TTSResponse


class TTSRepository:
    def __init__(self, project_id: str):
        self.db = firestore.Client(project=project_id)
        self.requests_collection = self.db.collection('tts_requests')
        self.responses_collection = self.db.collection('tts_responses')

    def save_request(self, request: TTSRequest) -> str:
        if not request.id:
            request.id = str(uuid.uuid4())

        doc_ref = self.requests_collection.document(request.id)
        doc_ref.set({
            'id': request.id,
            'text': request.text,
            'ssml': request.ssml,
            'voice': {
                'language_code': request.voice.language_code,
                'name': request.voice.name,
                'ssml_gender': request.voice.ssml_gender.value
            },
            'audio_config': {
                'audio_encoding': request.audio_config.audio_encoding.value,
                'speaking_rate': request.audio_config.speaking_rate,
                'pitch': request.audio_config.pitch,
                'volume_gain_db': request.audio_config.volume_gain_db,
                'sample_rate_hertz': request.audio_config.sample_rate_hertz,
                'effects_profile_id': request.audio_config.effects_profile_id
            },
            'user_id': request.user_id,
            'created_at': request.created_at,
            'metadata': request.metadata
        })

        return request.id

    def save_response(self, response: TTSResponse) -> str:
        doc_ref = self.responses_collection.document(response.id)
        doc_ref.set({
            'id': response.id,
            'request_id': response.request_id,
            'audio_url': response.audio_url,
            'duration_seconds': response.duration_seconds,
            'character_count': response.character_count,
            'created_at': response.created_at,
            'processing_time_ms': response.processing_time_ms,
            'metadata': response.metadata
        })

        return response.id

    def get_request(self, request_id: str) -> Optional[TTSRequest]:
        doc_ref = self.requests_collection.document(request_id)
        doc = doc_ref.get()

        if doc.exists:
            data = doc.to_dict()
            return self._dict_to_request(data)
        return None

    def get_user_requests(self, user_id: str, limit: int = 10) -> List[TTSRequest]:
        query = self.requests_collection.where('user_id', '==', user_id)\
            .order_by('created_at', direction=firestore.Query.DESCENDING)\
            .limit(limit)

        requests = []
        for doc in query.stream():
            data = doc.to_dict()
            requests.append(self._dict_to_request(data))

        return requests

    def _dict_to_request(self, data: dict) -> TTSRequest:
        from src.entity.models.tts_request import VoiceConfig, AudioConfig, VoiceGender, AudioEncoding

        voice = VoiceConfig(
            language_code=data['voice']['language_code'],
            name=data['voice'].get('name'),
            ssml_gender=VoiceGender(data['voice']['ssml_gender'])
        )

        audio_config = AudioConfig(
            audio_encoding=AudioEncoding(data['audio_config']['audio_encoding']),
            speaking_rate=data['audio_config']['speaking_rate'],
            pitch=data['audio_config']['pitch'],
            volume_gain_db=data['audio_config']['volume_gain_db'],
            sample_rate_hertz=data['audio_config'].get('sample_rate_hertz'),
            effects_profile_id=data['audio_config'].get('effects_profile_id')
        )

        return TTSRequest(
            id=data['id'],
            text=data['text'],
            ssml=data.get('ssml'),
            voice=voice,
            audio_config=audio_config,
            user_id=data.get('user_id'),
            created_at=data['created_at'],
            metadata=data.get('metadata', {})
        )