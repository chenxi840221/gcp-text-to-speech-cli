from typing import Dict, Any, Optional
from datetime import datetime
import json


class ResponseFormatter:
    @staticmethod
    def format_success_response(
        data: Any,
        message: str = "Success",
        status_code: int = 200
    ) -> Dict[str, Any]:
        return {
            "success": True,
            "message": message,
            "data": data,
            "timestamp": datetime.utcnow().isoformat(),
            "status_code": status_code
        }

    @staticmethod
    def format_error_response(
        error: str,
        error_type: str = "Error",
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        response = {
            "success": False,
            "error": {
                "message": error,
                "type": error_type,
                "code": status_code
            },
            "timestamp": datetime.utcnow().isoformat(),
            "status_code": status_code
        }

        if details:
            response["error"]["details"] = details

        return response

    @staticmethod
    def format_tts_response(tts_result: Dict[str, Any]) -> Dict[str, Any]:
        if tts_result.get('success'):
            return ResponseFormatter.format_success_response(
                data={
                    "request_id": tts_result.get('request_id'),
                    "audio_url": tts_result.get('audio_url'),
                    "duration_seconds": tts_result.get('duration_seconds'),
                    "character_count": tts_result.get('character_count'),
                    "processing_time_ms": tts_result.get('processing_time_ms'),
                    "metadata": tts_result.get('metadata', {})
                },
                message="Text-to-speech synthesis completed successfully"
            )
        else:
            return ResponseFormatter.format_error_response(
                error=tts_result.get('error', 'Unknown error occurred'),
                error_type=tts_result.get('error_type', 'TTSError'),
                status_code=400
            )

    @staticmethod
    def format_voices_response(voices_result: Dict[str, Any]) -> Dict[str, Any]:
        if voices_result.get('success'):
            return ResponseFormatter.format_success_response(
                data={
                    "total_voices": voices_result.get('total_voices'),
                    "voices": voices_result.get('voices')
                },
                message="Available voices retrieved successfully"
            )
        else:
            return ResponseFormatter.format_error_response(
                error=voices_result.get('error', 'Failed to retrieve voices'),
                error_type="VoicesError",
                status_code=500
            )

    @staticmethod
    def format_history_response(history_result: Dict[str, Any]) -> Dict[str, Any]:
        if history_result.get('success'):
            return ResponseFormatter.format_success_response(
                data={
                    "user_id": history_result.get('user_id'),
                    "history": history_result.get('history'),
                    "count": history_result.get('count')
                },
                message="User history retrieved successfully"
            )
        else:
            return ResponseFormatter.format_error_response(
                error=history_result.get('error', 'Failed to retrieve history'),
                error_type="HistoryError",
                status_code=500
            )

    @staticmethod
    def format_validation_error(errors: Dict[str, Any]) -> Dict[str, Any]:
        return ResponseFormatter.format_error_response(
            error="Request validation failed",
            error_type="ValidationError",
            status_code=400,
            details={"validation_errors": errors}
        )