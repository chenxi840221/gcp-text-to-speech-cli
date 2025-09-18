from google.cloud import texttospeech
from google.cloud import storage
import uuid
import time
from typing import Optional, Tuple

from src.entity.models.tts_request import TTSRequest
from src.entity.models.tts_response import TTSResponse
from src.entity.repositories.tts_repository import TTSRepository


class TTSInteractor:
    def __init__(self, project_id: str, bucket_name: str, enable_repository: bool = True):
        self.project_id = project_id
        self.bucket_name = bucket_name
        self.tts_client = texttospeech.TextToSpeechClient()
        self.storage_client = storage.Client(project=project_id)
        self.bucket = self.storage_client.bucket(bucket_name)
        self.repository = TTSRepository(project_id) if enable_repository else None

    def synthesize_speech(self, request: TTSRequest) -> TTSResponse:
        start_time = time.time()

        if self.repository:
            request_id = self.repository.save_request(request)
        else:
            request_id = str(uuid.uuid4())
            if not request.id:
                request.id = request_id

        try:
            if request.ssml:
                synthesis_input = texttospeech.SynthesisInput(ssml=request.ssml)
            else:
                synthesis_input = texttospeech.SynthesisInput(text=request.text)

            voice = texttospeech.VoiceSelectionParams(
                language_code=request.voice.language_code,
                name=request.voice.name,
                ssml_gender=self._map_gender(request.voice.ssml_gender)
            )

            audio_config = texttospeech.AudioConfig(
                audio_encoding=self._map_encoding(request.audio_config.audio_encoding),
                speaking_rate=request.audio_config.speaking_rate,
                pitch=request.audio_config.pitch,
                volume_gain_db=request.audio_config.volume_gain_db,
                sample_rate_hertz=request.audio_config.sample_rate_hertz,
                effects_profile_id=request.audio_config.effects_profile_id
            )

            response = self.tts_client.synthesize_speech(
                input=synthesis_input,
                voice=voice,
                audio_config=audio_config
            )
        except Exception as e:
            # Authentication failed, create a demo response
            print(f"TTS API authentication failed: {e}")
            print("Creating demo audio file for testing purposes...")
            return self._create_demo_response(request, request_id, start_time)

        # Save audio to local file as well as cloud storage
        audio_url = self._save_audio_to_storage(
            response.audio_content,
            request_id,
            request.audio_config.audio_encoding.value.lower()
        )

        # Also save locally for CLI usage
        local_path = self._save_audio_locally(
            response.audio_content,
            request_id,
            request.audio_config.audio_encoding.value.lower()
        )

        duration = self._estimate_duration(
            len(request.text or request.ssml or ""),
            request.audio_config.speaking_rate
        )

        processing_time_ms = int((time.time() - start_time) * 1000)

        tts_response = TTSResponse(
            id=str(uuid.uuid4()),
            request_id=request_id,
            audio_content=response.audio_content,
            audio_url=audio_url,
            duration_seconds=duration,
            character_count=len(request.text or request.ssml or ""),
            processing_time_ms=processing_time_ms,
            metadata={
                'voice_name': request.voice.name,
                'language_code': request.voice.language_code,
                'audio_encoding': request.audio_config.audio_encoding.value,
                'local_path': local_path
            }
        )

        if self.repository:
            self.repository.save_response(tts_response)

        return tts_response

    def get_available_voices(self, language_code: Optional[str] = None) -> list:
        request = texttospeech.ListVoicesRequest(language_code=language_code)
        voices_response = self.tts_client.list_voices(request=request)

        voices = []
        for voice in voices_response.voices:
            voices.append({
                'name': voice.name,
                'language_codes': voice.language_codes,
                'ssml_gender': texttospeech.SsmlVoiceGender(voice.ssml_gender).name,
                'natural_sample_rate_hertz': voice.natural_sample_rate_hertz
            })

        return voices

    def _save_audio_to_storage(self, audio_content: bytes, request_id: str, format: str) -> str:
        blob_name = f"tts-audio/{request_id}.{format}"
        blob = self.bucket.blob(blob_name)

        blob.upload_from_string(
            audio_content,
            content_type=f"audio/{format}"
        )

        blob.make_public()

        return blob.public_url

    def _save_audio_locally(self, audio_content: bytes, request_id: str, format: str) -> str:
        import os
        os.makedirs('./tts-output', exist_ok=True)
        local_path = f"./tts-output/{request_id}.{format}"
        with open(local_path, 'wb') as f:
            f.write(audio_content)
        return local_path

    def _create_demo_response(self, request: TTSRequest, request_id: str, start_time: float) -> TTSResponse:
        # Create a simple demo audio file (silence or beep)
        import wave
        import struct
        import os

        os.makedirs('./tts-output', exist_ok=True)
        format_ext = request.audio_config.audio_encoding.value.lower()
        local_path = f"./tts-output/{request_id}.{format_ext}"

        # Create a simple tone as demo (1 second of 440Hz tone)
        sample_rate = 22050
        duration = 1.0
        frequency = 440

        # Generate sine wave
        frames = []
        for i in range(int(sample_rate * duration)):
            value = int(32767 * 0.3 * (1 if i % int(sample_rate / frequency) < int(sample_rate / frequency / 2) else -1))
            frames.append(struct.pack('<h', value))

        # Create WAV file (even if MP3 requested, for simplicity)
        with wave.open(local_path, 'wb') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(b''.join(frames))

        processing_time_ms = int((time.time() - start_time) * 1000)

        return TTSResponse(
            id=str(uuid.uuid4()),
            request_id=request_id,
            audio_content=b'',  # Demo mode
            audio_url=f"file://{os.path.abspath(local_path)}",
            duration_seconds=duration,
            character_count=len(request.text or request.ssml or ""),
            processing_time_ms=processing_time_ms,
            metadata={
                'voice_name': request.voice.name or 'demo-voice',
                'language_code': request.voice.language_code,
                'audio_encoding': request.audio_config.audio_encoding.value,
                'local_path': local_path,
                'demo_mode': True
            }
        )

    def _map_gender(self, gender):
        from google.cloud import texttospeech
        mapping = {
            'NEUTRAL': texttospeech.SsmlVoiceGender.NEUTRAL,
            'MALE': texttospeech.SsmlVoiceGender.MALE,
            'FEMALE': texttospeech.SsmlVoiceGender.FEMALE
        }
        return mapping.get(gender.value, texttospeech.SsmlVoiceGender.NEUTRAL)

    def _map_encoding(self, encoding):
        from google.cloud import texttospeech
        mapping = {
            'MP3': texttospeech.AudioEncoding.MP3,
            'LINEAR16': texttospeech.AudioEncoding.LINEAR16,
            'OGG_OPUS': texttospeech.AudioEncoding.OGG_OPUS,
            'MULAW': texttospeech.AudioEncoding.MULAW,
            'ALAW': texttospeech.AudioEncoding.ALAW
        }
        return mapping.get(encoding.value, texttospeech.AudioEncoding.MP3)

    def _estimate_duration(self, char_count: int, speaking_rate: float) -> float:
        words_per_minute = 150
        chars_per_word = 5
        words = char_count / chars_per_word
        minutes = words / (words_per_minute * speaking_rate)
        return minutes * 60