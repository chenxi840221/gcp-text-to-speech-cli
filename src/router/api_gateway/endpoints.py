from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import logging

from src.interactor.business_logic.tts_manager import TTSManager
from src.presenter.formatters.response_formatter import ResponseFormatter
from src.presenter.middleware.validation_middleware import (
    ValidationMiddleware,
    validate_request
)

app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PROJECT_ID = os.getenv('GOOGLE_CLOUD_PROJECT', 'your-project-id')
BUCKET_NAME = os.getenv('TTS_BUCKET_NAME', 'your-tts-bucket')

tts_manager = TTSManager(PROJECT_ID, BUCKET_NAME)


@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy",
        "service": "Text-to-Speech API",
        "version": "1.0.0"
    })


@app.route('/api/v1/tts/synthesize', methods=['POST'])
@validate_request(ValidationMiddleware.validate_tts_request)
def synthesize_speech():
    try:
        data = request.get_json()

        result = tts_manager.process_text_to_speech(
            text=data.get('text', ''),
            language_code=data.get('language_code', 'en-US'),
            voice_name=data.get('voice_name'),
            ssml_gender=data.get('ssml_gender', 'NEUTRAL'),
            audio_encoding=data.get('audio_encoding', 'MP3'),
            speaking_rate=data.get('speaking_rate', 1.0),
            pitch=data.get('pitch', 0.0),
            user_id=data.get('user_id')
        )

        response = ResponseFormatter.format_tts_response(result)
        return jsonify(response), response['status_code']

    except Exception as e:
        logger.error(f"Error in synthesize_speech: {str(e)}")
        response = ResponseFormatter.format_error_response(
            error="Internal server error occurred",
            error_type="InternalError",
            status_code=500
        )
        return jsonify(response), 500


@app.route('/api/v1/tts/synthesize-ssml', methods=['POST'])
@validate_request(ValidationMiddleware.validate_tts_request)
def synthesize_ssml():
    try:
        data = request.get_json()

        result = tts_manager.process_ssml_to_speech(
            ssml=data.get('ssml', ''),
            language_code=data.get('language_code', 'en-US'),
            voice_name=data.get('voice_name'),
            audio_encoding=data.get('audio_encoding', 'MP3'),
            user_id=data.get('user_id')
        )

        response = ResponseFormatter.format_tts_response(result)
        return jsonify(response), response['status_code']

    except Exception as e:
        logger.error(f"Error in synthesize_ssml: {str(e)}")
        response = ResponseFormatter.format_error_response(
            error="Internal server error occurred",
            error_type="InternalError",
            status_code=500
        )
        return jsonify(response), 500


@app.route('/api/v1/tts/voices', methods=['GET'])
@validate_request(ValidationMiddleware.validate_voices_request)
def get_voices():
    try:
        language_code = request.args.get('language_code')

        result = tts_manager.get_available_voices(language_code)

        response = ResponseFormatter.format_voices_response(result)
        return jsonify(response), response['status_code']

    except Exception as e:
        logger.error(f"Error in get_voices: {str(e)}")
        response = ResponseFormatter.format_error_response(
            error="Internal server error occurred",
            error_type="InternalError",
            status_code=500
        )
        return jsonify(response), 500


@app.route('/api/v1/tts/history/<user_id>', methods=['GET'])
def get_user_history(user_id):
    try:
        limit = int(request.args.get('limit', 10))

        validation_errors = ValidationMiddleware.validate_history_request({
            'user_id': user_id,
            'limit': limit
        })

        if validation_errors:
            response = ResponseFormatter.format_validation_error(validation_errors)
            return jsonify(response), response['status_code']

        result = tts_manager.get_user_history(user_id, limit)

        response = ResponseFormatter.format_history_response(result)
        return jsonify(response), response['status_code']

    except Exception as e:
        logger.error(f"Error in get_user_history: {str(e)}")
        response = ResponseFormatter.format_error_response(
            error="Internal server error occurred",
            error_type="InternalError",
            status_code=500
        )
        return jsonify(response), 500


@app.route('/api/v1/tts/languages', methods=['GET'])
def get_supported_languages():
    try:
        languages = [
            {'code': 'en-US', 'name': 'English (US)', 'region': 'United States'},
            {'code': 'en-GB', 'name': 'English (UK)', 'region': 'United Kingdom'},
            {'code': 'en-AU', 'name': 'English (AU)', 'region': 'Australia'},
            {'code': 'es-ES', 'name': 'Spanish (Spain)', 'region': 'Spain'},
            {'code': 'es-US', 'name': 'Spanish (US)', 'region': 'United States'},
            {'code': 'fr-FR', 'name': 'French (France)', 'region': 'France'},
            {'code': 'fr-CA', 'name': 'French (Canada)', 'region': 'Canada'},
            {'code': 'de-DE', 'name': 'German (Germany)', 'region': 'Germany'},
            {'code': 'it-IT', 'name': 'Italian (Italy)', 'region': 'Italy'},
            {'code': 'pt-BR', 'name': 'Portuguese (Brazil)', 'region': 'Brazil'},
            {'code': 'ja-JP', 'name': 'Japanese (Japan)', 'region': 'Japan'},
            {'code': 'ko-KR', 'name': 'Korean (South Korea)', 'region': 'South Korea'},
            {'code': 'zh-CN', 'name': 'Chinese (Simplified)', 'region': 'China'},
            {'code': 'hi-IN', 'name': 'Hindi (India)', 'region': 'India'},
            {'code': 'ar-XA', 'name': 'Arabic', 'region': 'Multi-region'}
        ]

        response = ResponseFormatter.format_success_response(
            data={'languages': languages, 'total': len(languages)},
            message="Supported languages retrieved successfully"
        )
        return jsonify(response), 200

    except Exception as e:
        logger.error(f"Error in get_supported_languages: {str(e)}")
        response = ResponseFormatter.format_error_response(
            error="Internal server error occurred",
            error_type="InternalError",
            status_code=500
        )
        return jsonify(response), 500


@app.errorhandler(404)
def not_found(error):
    response = ResponseFormatter.format_error_response(
        error="Endpoint not found",
        error_type="NotFoundError",
        status_code=404
    )
    return jsonify(response), 404


@app.errorhandler(405)
def method_not_allowed(error):
    response = ResponseFormatter.format_error_response(
        error="Method not allowed",
        error_type="MethodNotAllowedError",
        status_code=405
    )
    return jsonify(response), 405


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)