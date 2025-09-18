"""
CLI utility functions for text processing and file handling
"""

import os
import click
from pathlib import Path
from typing import List, Optional, Union
import chardet


def detect_file_encoding(file_path: str) -> str:
    """Detect file encoding to handle different text file formats"""
    try:
        with open(file_path, 'rb') as f:
            raw_data = f.read(10000)  # Read first 10KB for detection
            result = chardet.detect(raw_data)
            return result['encoding'] or 'utf-8'
    except Exception:
        return 'utf-8'


def read_text_file(file_path: str, encoding: Optional[str] = None) -> str:
    """Read text file with automatic encoding detection"""
    if not encoding:
        encoding = detect_file_encoding(file_path)

    try:
        with open(file_path, 'r', encoding=encoding) as f:
            content = f.read().strip()
        return content
    except UnicodeDecodeError:
        # Fallback to utf-8 with error handling
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read().strip()
        click.echo(f"Warning: File encoding issue detected, using UTF-8 with replacement characters", err=True)
        return content


def split_text_into_chunks(text: str, max_length: int = 5000, preserve_sentences: bool = True) -> List[str]:
    """Split long text into chunks suitable for TTS processing"""
    if len(text) <= max_length:
        return [text]

    chunks = []

    if preserve_sentences:
        # Split by sentences first
        import re
        sentences = re.split(r'(?<=[.!?])\s+', text)

        current_chunk = ""
        for sentence in sentences:
            if len(current_chunk) + len(sentence) + 1 <= max_length:
                current_chunk += sentence + " "
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                    current_chunk = sentence + " "
                else:
                    # Single sentence too long, split by words
                    word_chunks = split_by_words(sentence, max_length)
                    chunks.extend(word_chunks)

        if current_chunk:
            chunks.append(current_chunk.strip())
    else:
        # Simple character-based splitting
        for i in range(0, len(text), max_length):
            chunks.append(text[i:i + max_length])

    return [chunk for chunk in chunks if chunk.strip()]


def split_by_words(text: str, max_length: int) -> List[str]:
    """Split text by words when sentence splitting isn't sufficient"""
    words = text.split()
    chunks = []
    current_chunk = ""

    for word in words:
        if len(current_chunk) + len(word) + 1 <= max_length:
            current_chunk += word + " "
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = word + " "
            else:
                # Single word too long, force split
                chunks.append(word[:max_length])
                if len(word) > max_length:
                    remaining = word[max_length:]
                    chunks.extend(split_by_words(remaining, max_length))

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks


def validate_text_file(file_path: str) -> bool:
    """Validate if file exists and is readable"""
    path = Path(file_path)

    if not path.exists():
        click.echo(f"Error: File '{file_path}' does not exist", err=True)
        return False

    if not path.is_file():
        click.echo(f"Error: '{file_path}' is not a file", err=True)
        return False

    if path.stat().st_size == 0:
        click.echo(f"Warning: File '{file_path}' is empty", err=True)
        return False

    if path.stat().st_size > 10 * 1024 * 1024:  # 10MB limit
        click.echo(f"Warning: File '{file_path}' is very large ({path.stat().st_size / 1024 / 1024:.1f}MB)", err=True)
        if not click.confirm("Continue processing?"):
            return False

    return True


def get_supported_text_extensions() -> List[str]:
    """Get list of supported text file extensions"""
    return ['.txt', '.md', '.rst', '.log', '.csv', '.json', '.xml', '.html', '.py', '.js', '.ts', '.css', '.sql']


def is_text_file(file_path: str) -> bool:
    """Check if file appears to be a text file based on extension and content"""
    path = Path(file_path)

    # Check extension
    if path.suffix.lower() in get_supported_text_extensions():
        return True

    # Check if file appears to be text by reading first few bytes
    try:
        with open(file_path, 'rb') as f:
            chunk = f.read(1024)
            if b'\x00' in chunk:  # Binary files often contain null bytes
                return False

            # Try to decode as text
            try:
                chunk.decode('utf-8')
                return True
            except UnicodeDecodeError:
                # Try other common encodings
                for encoding in ['latin-1', 'cp1252']:
                    try:
                        chunk.decode(encoding)
                        return True
                    except UnicodeDecodeError:
                        continue
                return False
    except Exception:
        return False


def clean_text_for_tts(text: str) -> str:
    """Clean and prepare text for TTS processing"""
    import re

    # Remove or replace problematic characters
    text = re.sub(r'[^\w\s\.,!?;:\-\(\)\'\"]+', ' ', text)

    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text)

    # Remove excessive punctuation
    text = re.sub(r'[.]{3,}', '...', text)
    text = re.sub(r'[!]{2,}', '!', text)
    text = re.sub(r'[?]{2,}', '?', text)

    return text.strip()


def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


def create_output_filename(input_file: str, output_dir: str, audio_format: str, suffix: str = "") -> str:
    """Create appropriate output filename based on input file"""
    input_path = Path(input_file)

    # Get base name without extension
    base_name = input_path.stem

    # Add suffix if provided
    if suffix:
        base_name += f"_{suffix}"

    # Determine extension based on audio format
    extension_map = {
        'MP3': '.mp3',
        'LINEAR16': '.wav',
        'OGG_OPUS': '.ogg',
        'MULAW': '.wav',
        'ALAW': '.wav'
    }

    extension = extension_map.get(audio_format, '.mp3')

    # Create output path
    output_path = Path(output_dir) / f"{base_name}{extension}"

    # Handle duplicate names
    counter = 1
    original_path = output_path
    while output_path.exists():
        output_path = original_path.parent / f"{original_path.stem}_{counter}{original_path.suffix}"
        counter += 1

    return str(output_path)


def estimate_audio_duration(text: str, speaking_rate: float = 1.0) -> float:
    """Estimate audio duration based on text length and speaking rate"""
    # Average speaking rate is about 150 words per minute
    # Average word length is about 5 characters
    words = len(text) / 5
    minutes = words / (150 * speaking_rate)
    return minutes * 60  # Convert to seconds


def preview_text_chunks(chunks: List[str], max_preview: int = 3) -> None:
    """Preview text chunks that will be processed"""
    click.echo(f"Text will be split into {len(chunks)} chunk(s):")

    for i, chunk in enumerate(chunks[:max_preview]):
        preview = chunk[:100] + "..." if len(chunk) > 100 else chunk
        click.echo(f"  Chunk {i+1}: {preview}")

    if len(chunks) > max_preview:
        click.echo(f"  ... and {len(chunks) - max_preview} more chunk(s)")

    total_duration = sum(estimate_audio_duration(chunk) for chunk in chunks)
    click.echo(f"Estimated total duration: {total_duration:.1f} seconds")