"""
Text file processing commands for TTS CLI
Handles long documents, automatic chunking, and batch text processing
"""

import click
import os
from pathlib import Path
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed


@click.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.option('--output-dir', '-o', type=click.Path(), default='./text_output',
              help='Output directory for audio files')
@click.option('--language', '-l', default='en-US',
              help='Language code')
@click.option('--voice', help='Voice name')
@click.option('--audio-format', type=click.Choice(['MP3', 'LINEAR16', 'OGG_OPUS']),
              default='MP3', help='Audio output format')
@click.option('--chunk-size', type=int, default=4500,
              help='Maximum characters per chunk')
@click.option('--preserve-sentences', is_flag=True, default=True,
              help='Try to keep sentences intact when chunking')
@click.option('--combine-output', is_flag=True,
              help='Combine all chunks into a single audio file')
@click.option('--workers', type=int, default=3,
              help='Number of concurrent workers')
@click.option('--preview', is_flag=True,
              help='Preview chunks without processing')
@click.pass_context
def process_text_file(ctx, input_file, output_dir, language, voice, audio_format,
                     chunk_size, preserve_sentences, combine_output, workers, preview):
    """Process long text files with automatic chunking

    This command is designed for processing long documents like books, articles,
    or documentation that exceed the 5000 character limit for single TTS requests.

    Examples:
        gcp-tts process-text-file document.txt
        gcp-tts process-text-file book.txt --chunk-size 3000 --combine-output
        gcp-tts process-text-file article.md --preview
    """
    from src.cli.utils import (validate_text_file, read_text_file, clean_text_for_tts,
                              split_text_into_chunks, preview_text_chunks,
                              create_output_filename, format_file_size)

    config = ctx.obj['config']
    tts_manager = ctx.obj['tts_manager']
    verbose = config['verbose']

    # Validate input file
    if not validate_text_file(input_file):
        return

    # Read and process text
    if verbose:
        file_size = os.path.getsize(input_file)
        click.echo(f"Processing file: {input_file} ({format_file_size(file_size)})")

    text = read_text_file(input_file)
    text = clean_text_for_tts(text)

    if not text:
        click.echo("Error: File is empty or contains no readable text")
        return

    # Split into chunks
    chunks = split_text_into_chunks(text, max_length=chunk_size,
                                   preserve_sentences=preserve_sentences)

    # Preview mode
    if preview:
        preview_text_chunks(chunks, max_preview=10)
        return

    click.echo(f"Text file will be processed in {len(chunks)} chunk(s)")

    if len(chunks) > 10:
        if not click.confirm("Processing many chunks may take significant time. Continue?"):
            return

    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Process chunks
    results = []
    failed_chunks = []

    if combine_output:
        # Process chunks sequentially for combining
        audio_files = []

        for i, chunk in enumerate(chunks):
            try:
                if verbose:
                    click.echo(f"Processing chunk {i+1}/{len(chunks)}...")

                result = process_text_chunk(tts_manager, chunk, language, voice, audio_format, i)

                if result['success']:
                    # Download and store audio file path
                    chunk_file = output_path / f"chunk_{i:04d}.{audio_format.lower()}"
                    download_audio_from_url(result['audio_url'], str(chunk_file))
                    audio_files.append(str(chunk_file))
                    results.append(result)
                else:
                    failed_chunks.append({'chunk_index': i, 'error': result['error']})

            except Exception as e:
                failed_chunks.append({'chunk_index': i, 'error': str(e)})

        # Combine audio files if successful
        if audio_files and not failed_chunks:
            output_file = create_output_filename(input_file, output_dir, audio_format, "combined")
            if combine_audio_files(audio_files, output_file, audio_format):
                click.echo(f"✓ Combined audio saved to: {output_file}")

                # Clean up individual chunk files
                for chunk_file in audio_files:
                    os.remove(chunk_file)
            else:
                click.echo("⚠ Failed to combine audio files, keeping individual chunks")

    else:
        # Process chunks in parallel
        with ThreadPoolExecutor(max_workers=workers) as executor:
            # Submit all tasks
            future_to_chunk = {}
            for i, chunk in enumerate(chunks):
                future = executor.submit(process_text_chunk, tts_manager, chunk,
                                       language, voice, audio_format, i)
                future_to_chunk[future] = {'index': i, 'chunk': chunk}

            # Collect results with progress bar
            with click.progressbar(as_completed(future_to_chunk), length=len(chunks),
                                  label='Processing chunks') as bar:
                for future in bar:
                    chunk_info = future_to_chunk[future]
                    chunk_index = chunk_info['index']

                    try:
                        result = future.result()
                        if result['success']:
                            # Download audio file
                            chunk_file = output_path / f"chunk_{chunk_index:04d}.{audio_format.lower()}"
                            download_audio_from_url(result['audio_url'], str(chunk_file))
                            results.append(result)
                            if verbose:
                                click.echo(f"✓ Chunk {chunk_index + 1}: {chunk_file}")
                        else:
                            failed_chunks.append({'chunk_index': chunk_index, 'error': result['error']})
                    except Exception as e:
                        failed_chunks.append({'chunk_index': chunk_index, 'error': str(e)})

    # Summary
    successful = len(results)
    failed = len(failed_chunks)

    click.echo(f"\nProcessing completed:")
    click.echo(f"  ✓ Successful chunks: {successful}")
    click.echo(f"  ✗ Failed chunks: {failed}")

    if failed_chunks:
        click.echo(f"\nFailed chunks:")
        for failed in failed_chunks[:5]:  # Show first 5 failures
            click.echo(f"  Chunk {failed['chunk_index'] + 1}: {failed['error']}")
        if len(failed_chunks) > 5:
            click.echo(f"  ... and {len(failed_chunks) - 5} more")

    # Save processing log
    save_processing_log(results, failed_chunks, input_file, output_path)

    if successful > 0:
        click.echo(f"\n📁 Audio files saved to: {output_dir}")


def process_text_chunk(tts_manager, chunk_text: str, language: str, voice: str,
                      audio_format: str, chunk_index: int) -> Dict[str, Any]:
    """Process a single text chunk"""
    try:
        result = tts_manager.process_text_to_speech(
            text=chunk_text,
            language_code=language,
            voice_name=voice,
            audio_encoding=audio_format,
            user_id='text-file-cli'
        )

        if result['success']:
            return {
                'success': True,
                'chunk_index': chunk_index,
                'audio_url': result['audio_url'],
                'duration': result['duration_seconds'],
                'characters': result['character_count'],
                'processing_time': result['processing_time_ms']
            }
        else:
            return {
                'success': False,
                'chunk_index': chunk_index,
                'error': result['error']
            }

    except Exception as e:
        return {
            'success': False,
            'chunk_index': chunk_index,
            'error': str(e)
        }


def download_audio_from_url(url: str, output_path: str) -> None:
    """Download audio file from URL"""
    import requests

    response = requests.get(url, stream=True)
    response.raise_for_status()

    with open(output_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)


def combine_audio_files(audio_files: List[str], output_file: str, audio_format: str) -> bool:
    """Combine multiple audio files into one"""
    try:
        # Try using pydub for audio combination
        from pydub import AudioSegment

        combined = AudioSegment.empty()

        for audio_file in audio_files:
            if audio_format == 'MP3':
                segment = AudioSegment.from_mp3(audio_file)
            elif audio_format == 'LINEAR16':
                segment = AudioSegment.from_wav(audio_file)
            elif audio_format == 'OGG_OPUS':
                segment = AudioSegment.from_ogg(audio_file)
            else:
                segment = AudioSegment.from_file(audio_file)

            combined += segment

        # Export combined audio
        if audio_format == 'MP3':
            combined.export(output_file, format="mp3")
        elif audio_format == 'LINEAR16':
            combined.export(output_file, format="wav")
        elif audio_format == 'OGG_OPUS':
            combined.export(output_file, format="ogg")

        return True

    except ImportError:
        click.echo("Warning: pydub not installed. Cannot combine audio files.")
        click.echo("Install with: pip install pydub")
        return False
    except Exception as e:
        click.echo(f"Error combining audio files: {str(e)}")
        return False


def save_processing_log(results: List[Dict], failed_chunks: List[Dict],
                       input_file: str, output_dir: Path) -> None:
    """Save processing log"""
    import json
    from datetime import datetime

    log_data = {
        'input_file': input_file,
        'processing_time': datetime.now().isoformat(),
        'total_chunks': len(results) + len(failed_chunks),
        'successful_chunks': len(results),
        'failed_chunks': len(failed_chunks),
        'results': results,
        'failures': failed_chunks
    }

    log_file = output_dir / 'text_processing_log.json'
    with open(log_file, 'w', encoding='utf-8') as f:
        json.dump(log_data, f, indent=2, default=str)

    click.echo(f"Processing log saved to: {log_file}")


@click.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.option('--output', '-o', type=click.Path(),
              help='Output audio file (default: auto-generated)')
@click.option('--language', '-l', default='en-US',
              help='Language code')
@click.option('--voice', help='Voice name')
@click.option('--audio-format', type=click.Choice(['MP3', 'LINEAR16', 'OGG_OPUS']),
              default='MP3', help='Audio output format')
@click.option('--speed', type=float, default=1.0,
              help='Speaking rate (0.25 to 4.0)')
@click.option('--pitch', type=float, default=0.0,
              help='Pitch adjustment (-20.0 to 20.0)')
@click.pass_context
def read_aloud(ctx, input_file, output, language, voice, audio_format, speed, pitch):
    """Convert a text file to speech with single output

    This is a simplified command for quick text-to-speech conversion
    of files under 5000 characters.

    Examples:
        gcp-tts read-aloud document.txt
        gcp-tts read-aloud article.md --voice en-US-Neural2-A --output article.mp3
    """
    from src.cli.utils import validate_text_file, read_text_file, clean_text_for_tts, create_output_filename

    config = ctx.obj['config']
    tts_manager = ctx.obj['tts_manager']
    verbose = config['verbose']

    # Validate input file
    if not validate_text_file(input_file):
        return

    # Read text
    text = read_text_file(input_file)
    text = clean_text_for_tts(text)

    if not text:
        click.echo("Error: File is empty or contains no readable text")
        return

    if len(text) > 5000:
        click.echo(f"Error: Text is too long ({len(text)} characters). Use 'process-text-file' command for long texts.")
        return

    try:
        if verbose:
            click.echo(f"Converting {len(text)} characters to speech...")

        # Generate speech
        result = tts_manager.process_text_to_speech(
            text=text,
            language_code=language,
            voice_name=voice,
            audio_encoding=audio_format,
            speaking_rate=speed,
            pitch=pitch,
            user_id='read-aloud-cli'
        )

        if result['success']:
            # Determine output filename
            if not output:
                output = create_output_filename(input_file, '.', audio_format)

            # Download audio
            download_audio_from_url(result['audio_url'], output)

            click.echo(f"✓ Audio saved to: {output}")
            click.echo(f"  Duration: {result['duration_seconds']:.2f} seconds")
            click.echo(f"  Characters: {result['character_count']}")

        else:
            click.echo(f"Error: {result['error']}")

    except Exception as e:
        click.echo(f"Error processing file: {str(e)}")


# Add commands to main CLI in main.py
def register_text_commands(cli_group):
    """Register text file processing commands"""
    cli_group.add_command(process_text_file, name='process-text-file')
    cli_group.add_command(read_aloud, name='read-aloud')