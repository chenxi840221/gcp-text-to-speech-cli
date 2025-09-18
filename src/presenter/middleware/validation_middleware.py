from functools import wraps
from typing import Dict, Any, Optional
import re


class ValidationMiddleware:
    @staticmethod
    def validate_tts_request(request_data: Dict[str, Any]) -> Dict[str, Any]:
        errors = {}

        text = request_data.get('text', '')
        ssml = request_data.get('ssml', '')

        if not text and not ssml:
            errors['text'] = 'Either text or SSML content is required'

        if text and len(text) > 5000:
            errors['text'] = 'Text must be 5000 characters or less'

        if ssml and not ValidationMiddleware._is_valid_ssml(ssml):
            errors['ssml'] = 'Invalid SSML format'

        language_code = request_data.get('language_code', 'en-US')
        if not ValidationMiddleware._is_valid_language_code(language_code):
            errors['language_code'] = 'Invalid language code format'

        audio_encoding = request_data.get('audio_encoding', 'MP3')
        valid_encodings = ['MP3', 'LINEAR16', 'OGG_OPUS', 'MULAW', 'ALAW']
        if audio_encoding not in valid_encodings:
            errors['audio_encoding'] = f'Audio encoding must be one of: {", ".join(valid_encodings)}'

        ssml_gender = request_data.get('ssml_gender', 'NEUTRAL')
        valid_genders = ['NEUTRAL', 'MALE', 'FEMALE']
        if ssml_gender not in valid_genders:
            errors['ssml_gender'] = f'SSML gender must be one of: {", ".join(valid_genders)}'

        speaking_rate = request_data.get('speaking_rate', 1.0)
        if not isinstance(speaking_rate, (int, float)) or speaking_rate < 0.25 or speaking_rate > 4.0:
            errors['speaking_rate'] = 'Speaking rate must be between 0.25 and 4.0'

        pitch = request_data.get('pitch', 0.0)
        if not isinstance(pitch, (int, float)) or pitch < -20.0 or pitch > 20.0:
            errors['pitch'] = 'Pitch must be between -20.0 and 20.0'

        return errors

    @staticmethod
    def validate_voices_request(request_data: Dict[str, Any]) -> Dict[str, Any]:
        errors = {}

        language_code = request_data.get('language_code')
        if language_code and not ValidationMiddleware._is_valid_language_code(language_code):
            errors['language_code'] = 'Invalid language code format'

        return errors

    @staticmethod
    def validate_history_request(request_data: Dict[str, Any]) -> Dict[str, Any]:
        errors = {}

        user_id = request_data.get('user_id')
        if not user_id or not isinstance(user_id, str) or len(user_id.strip()) == 0:
            errors['user_id'] = 'User ID is required and must be a non-empty string'

        limit = request_data.get('limit', 10)
        if not isinstance(limit, int) or limit < 1 or limit > 100:
            errors['limit'] = 'Limit must be an integer between 1 and 100'

        return errors

    @staticmethod
    def _is_valid_language_code(language_code: str) -> bool:
        pattern = r'^[a-z]{2}(-[A-Z]{2})?$'
        return bool(re.match(pattern, language_code))

    @staticmethod
    def _is_valid_ssml(ssml: str) -> bool:
        required_tags = ['<speak>', '</speak>']
        for tag in required_tags:
            if tag not in ssml:
                return False

        invalid_chars = ['<script', '<iframe', '<object', '<embed']
        for char in invalid_chars:
            if char.lower() in ssml.lower():
                return False

        return True


def validate_request(validation_func):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            from flask import request, jsonify
            from src.presenter.formatters.response_formatter import ResponseFormatter

            try:
                request_data = request.get_json() or {}

                if hasattr(request, 'form') and request.form:
                    request_data.update(request.form.to_dict())

                if hasattr(request, 'args') and request.args:
                    request_data.update(request.args.to_dict())

                errors = validation_func(request_data)

                if errors:
                    response = ResponseFormatter.format_validation_error(errors)
                    return jsonify(response), response['status_code']

                return f(*args, **kwargs)

            except Exception as e:
                response = ResponseFormatter.format_error_response(
                    error=f"Validation error: {str(e)}",
                    error_type="ValidationError",
                    status_code=400
                )
                return jsonify(response), 400

        return decorated_function
    return decorator