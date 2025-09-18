#!/usr/bin/env python3
"""
Google Cloud Text-to-Speech CLI Tool

A command-line interface for the Google Cloud Text-to-Speech application
following VIPER architecture patterns.
"""

import click
import os
import sys
import json
from typing import Optional, Dict, Any
from pathlib import Path
from dotenv import load_dotenv

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

# Load environment variables early
load_dotenv()

from src.interactor.business_logic.tts_manager import TTSManager
from src.shared.config.gcp_config import GCPConfig


@click.group()
@click.version_option(version='1.0.0', prog_name='gcp-tts')
@click.option('--project-id', envvar='GOOGLE_CLOUD_PROJECT',
              help='Google Cloud Project ID')
@click.option('--bucket-name', envvar='TTS_BUCKET_NAME',
              help='Cloud Storage bucket for audio files')
@click.option('--location', envvar='VERTEX_AI_LOCATION', default='us-central1',
              help='Google Cloud region')
@click.option('--credentials', envvar='GOOGLE_APPLICATION_CREDENTIALS',
              help='Path to service account JSON file')
@click.option('--environment', envvar='ENVIRONMENT', default='development',
              type=click.Choice(['development', 'staging', 'production']),
              help='Environment to use (affects project selection)')
@click.option('--env-file', type=click.Path(exists=True),
              help='Path to .env file to load')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.pass_context
def cli(ctx, project_id, bucket_name, location, credentials, environment, env_file, verbose):
    """Google Cloud Text-to-Speech CLI Tool

    Convert text to natural-sounding speech using Google Cloud AI.

    Examples:
        gcp-tts synthesize "Hello, world!" --output hello.mp3
        gcp-tts voices --language en-US
        gcp-tts synthesize --file input.txt --voice en-US-Neural2-A

    Environment configuration:
        gcp-tts --environment staging synthesize "Test"
        gcp-tts --env-file .env.prod synthesize "Production test"
    """
    # Ensure context object exists
    ctx.ensure_object(dict)

    # Load additional .env file if specified
    if env_file:
        load_dotenv(env_file, override=True)
        if verbose:
            click.echo(f"Loaded environment from: {env_file}")

    # Initialize GCP configuration
    try:
        gcp_config = GCPConfig(env_file)

        # Override with command line arguments if provided
        if project_id:
            gcp_config.project_id = project_id
        elif environment:
            gcp_config.project_id = gcp_config.get_project_id_for_environment(environment)

        if bucket_name:
            gcp_config.tts_bucket_name = bucket_name
        if location:
            gcp_config.location = location
        if credentials:
            gcp_config.credentials_path = credentials

        # Validate required parameters
        if not gcp_config.project_id or gcp_config.project_id == 'your-project-id':
            click.echo("Error: Google Cloud Project ID is required. Set GOOGLE_CLOUD_PROJECT environment variable or use --project-id", err=True)
            sys.exit(1)

        if verbose:
            click.echo(f"Using project: {gcp_config.project_id}")
            click.echo(f"Using bucket: {gcp_config.tts_bucket_name}")
            click.echo(f"Using region: {gcp_config.location}")
            click.echo(f"Environment: {gcp_config.environment}")

        # Store configuration in context
        ctx.obj['config'] = {
            'project_id': gcp_config.project_id,
            'bucket_name': gcp_config.tts_bucket_name,
            'location': gcp_config.location,
            'credentials': gcp_config.credentials_path,
            'environment': gcp_config.environment,
            'verbose': verbose or gcp_config.cli_verbose,
            'gcp_config': gcp_config
        }

    except Exception as e:
        click.echo(f"Configuration error: {str(e)}", err=True)
        sys.exit(1)

    # Initialize TTS Manager
    try:
        ctx.obj['tts_manager'] = TTSManager(gcp_config.project_id, gcp_config.tts_bucket_name, enable_repository=False)
        if ctx.obj['config']['verbose']:
            click.echo(f"Initialized TTS Manager for project: {gcp_config.project_id}")
    except Exception as e:
        click.echo(f"Error initializing TTS Manager: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('text', required=False)
@click.option('--file', '-f', type=click.Path(exists=True),
              help='Read text from file instead of argument')
@click.option('--output', '-o', type=click.Path(),
              help='Output audio file path (default: auto-generated)')
@click.option('--language', '-l', default='en-US',
              help='Language code (e.g., en-US, es-ES)')
@click.option('--voice', help='Specific voice name (e.g., en-US-Neural2-A)')
@click.option('--gender', type=click.Choice(['NEUTRAL', 'MALE', 'FEMALE']),
              default='NEUTRAL', help='Voice gender')
@click.option('--format', 'audio_format', type=click.Choice(['MP3', 'LINEAR16', 'OGG_OPUS']),
              default='MP3', help='Audio output format')
@click.option('--speed', type=float, default=1.0,
              help='Speaking rate (0.25 to 4.0)')
@click.option('--pitch', type=float, default=0.0,
              help='Pitch adjustment (-20.0 to 20.0)')
@click.option('--ssml', is_flag=True,
              help='Treat input as SSML instead of plain text')
@click.option('--play', is_flag=True,
              help='Play audio after generation (requires audio player)')
@click.pass_context
def synthesize(ctx, text, file, output, language, voice, gender, audio_format,
               speed, pitch, ssml, play):
    """Convert text to speech

    Examples:
        gcp-tts synthesize "Hello, world!"
        gcp-tts synthesize --file input.txt --voice en-US-Neural2-A
        gcp-tts synthesize "Hello" --output greeting.mp3 --speed 1.2
    """
    config = ctx.obj['config']
    tts_manager = ctx.obj['tts_manager']
    verbose = config['verbose']

    # Get input text
    if file:
        from src.cli.utils import validate_text_file, read_text_file, clean_text_for_tts
        from src.cli.utils import split_text_into_chunks, preview_text_chunks

        if not validate_text_file(file):
            sys.exit(1)

        input_text = read_text_file(file)
        input_text = clean_text_for_tts(input_text)

        if verbose:
            click.echo(f"Read {len(input_text)} characters from {file}")

        # Handle long texts by splitting into chunks
        if len(input_text) > 5000:
            chunks = split_text_into_chunks(input_text, max_length=4500)
            if verbose:
                preview_text_chunks(chunks)

            if len(chunks) > 1:
                if not click.confirm(f"Text is long and will be split into {len(chunks)} chunks. Continue?"):
                    sys.exit(0)

                # Process first chunk for now (could be extended to process all chunks)
                click.echo("Processing first chunk only. Use batch processing for multiple chunks.")
                input_text = chunks[0]

    elif text:
        input_text = text
    else:
        click.echo("Error: Either provide text as argument or use --file option", err=True)
        sys.exit(1)

    if not input_text:
        click.echo("Error: No text provided", err=True)
        sys.exit(1)

    # Validate parameters
    if speed < 0.25 or speed > 4.0:
        click.echo("Error: Speed must be between 0.25 and 4.0", err=True)
        sys.exit(1)

    if pitch < -20.0 or pitch > 20.0:
        click.echo("Error: Pitch must be between -20.0 and 20.0", err=True)
        sys.exit(1)

    # Generate audio
    try:
        if verbose:
            click.echo("Generating speech...")
            click.echo(f"Language: {language}")
            click.echo(f"Voice: {voice or 'default'}")
            click.echo(f"Format: {audio_format}")
            click.echo(f"Speed: {speed}x")
            click.echo(f"Pitch: {pitch}")

        if ssml:
            result = tts_manager.process_ssml_to_speech(
                ssml=input_text,
                language_code=language,
                voice_name=voice,
                audio_encoding=audio_format,
                user_id='cli-user'
            )
        else:
            result = tts_manager.process_text_to_speech(
                text=input_text,
                language_code=language,
                voice_name=voice,
                ssml_gender=gender,
                audio_encoding=audio_format,
                speaking_rate=speed,
                pitch=pitch,
                user_id='cli-user'
            )

        if not result['success']:
            click.echo(f"Error: {result['error']}", err=True)
            sys.exit(1)

        # Determine output filename
        if not output:
            extension = audio_format.lower().replace('_', '.')
            if extension == 'linear16':
                extension = 'wav'
            output = f"tts_output_{result['request_id'][:8]}.{extension}"

        # Download audio file
        audio_url = result['audio_url']
        download_audio_file(audio_url, output, verbose)

        # Display results
        click.echo(f"✓ Speech generated successfully!")
        click.echo(f"  Output file: {output}")
        click.echo(f"  Duration: {result['duration_seconds']:.2f} seconds")
        click.echo(f"  Characters: {result['character_count']}")
        click.echo(f"  Processing time: {result['processing_time_ms']}ms")

        # Play audio if requested
        if play:
            play_audio_file(output, verbose)

    except Exception as e:
        click.echo(f"Error generating speech: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--language', '-l', help='Filter by language code (e.g., en-US)')
@click.option('--type', 'voice_type',
              type=click.Choice(['standard', 'wavenet', 'neural2', 'news', 'studio']),
              help='Filter by voice type')
@click.option('--gender', type=click.Choice(['NEUTRAL', 'MALE', 'FEMALE']),
              help='Filter by voice gender')
@click.option('--output-format', type=click.Choice(['table', 'json', 'csv']),
              default='table', help='Output format')
@click.pass_context
def voices(ctx, language, voice_type, gender, output_format):
    """List available voices

    Examples:
        gcp-tts voices
        gcp-tts voices --language en-US
        gcp-tts voices --type neural2 --output-format json
    """
    config = ctx.obj['config']
    tts_manager = ctx.obj['tts_manager']
    verbose = config['verbose']

    try:
        if verbose:
            click.echo("Fetching available voices...")

        result = tts_manager.get_available_voices(language)

        if not result['success']:
            click.echo(f"Error: {result['error']}", err=True)
            sys.exit(1)

        voices_data = result['voices']

        # Flatten and filter voices
        all_voices = []
        for category, voices_list in voices_data.items():
            for voice in voices_list:
                voice['type'] = category
                all_voices.append(voice)

        # Apply filters
        filtered_voices = all_voices

        if voice_type:
            filtered_voices = [v for v in filtered_voices if v['type'] == voice_type]

        if gender:
            filtered_voices = [v for v in filtered_voices if v['ssml_gender'] == gender]

        if language:
            filtered_voices = [v for v in filtered_voices if language in v['language_codes']]

        # Output results
        if output_format == 'json':
            click.echo(json.dumps(filtered_voices, indent=2))
        elif output_format == 'csv':
            if filtered_voices:
                import csv
                import io

                output = io.StringIO()
                writer = csv.DictWriter(output, fieldnames=['name', 'type', 'ssml_gender', 'language_codes'])
                writer.writeheader()

                for voice in filtered_voices:
                    writer.writerow({
                        'name': voice['name'],
                        'type': voice['type'],
                        'ssml_gender': voice['ssml_gender'],
                        'language_codes': ','.join(voice['language_codes'])
                    })

                click.echo(output.getvalue())
        else:  # table format
            if not filtered_voices:
                click.echo("No voices found matching the criteria.")
                return

            click.echo(f"\nFound {len(filtered_voices)} voices:")
            click.echo("-" * 80)
            click.echo(f"{'Name':<30} {'Type':<12} {'Gender':<8} {'Languages':<20}")
            click.echo("-" * 80)

            for voice in filtered_voices:
                languages = ', '.join(voice['language_codes'][:2])  # Show first 2 languages
                if len(voice['language_codes']) > 2:
                    languages += f" (+{len(voice['language_codes']) - 2} more)"

                click.echo(f"{voice['name']:<30} {voice['type']:<12} {voice['ssml_gender']:<8} {languages:<20}")

    except Exception as e:
        click.echo(f"Error fetching voices: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--output-format', type=click.Choice(['table', 'json']),
              default='table', help='Output format')
@click.pass_context
def languages(ctx, output_format):
    """List supported languages

    Examples:
        gcp-tts languages
        gcp-tts languages --output-format json
    """
    # Predefined list of supported languages
    supported_languages = [
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

    if output_format == 'json':
        click.echo(json.dumps(supported_languages, indent=2))
    else:
        click.echo(f"\nSupported Languages ({len(supported_languages)} total):")
        click.echo("-" * 60)
        click.echo(f"{'Code':<8} {'Name':<25} {'Region':<20}")
        click.echo("-" * 60)

        for lang in supported_languages:
            click.echo(f"{lang['code']:<8} {lang['name']:<25} {lang['region']:<20}")


@cli.command()
@click.argument('user_id')
@click.option('--limit', default=10, help='Number of history items to retrieve')
@click.option('--output-format', type=click.Choice(['table', 'json']),
              default='table', help='Output format')
@click.pass_context
def history(ctx, user_id, limit, output_format):
    """Get user synthesis history

    Examples:
        gcp-tts history cli-user
        gcp-tts history user123 --limit 5 --output-format json
    """
    config = ctx.obj['config']
    tts_manager = ctx.obj['tts_manager']
    verbose = config['verbose']

    try:
        if verbose:
            click.echo(f"Fetching history for user: {user_id}")

        result = tts_manager.get_user_history(user_id, limit)

        if not result['success']:
            click.echo(f"Error: {result['error']}", err=True)
            sys.exit(1)

        history_items = result['history']

        if output_format == 'json':
            click.echo(json.dumps(result, indent=2))
        else:
            if not history_items:
                click.echo(f"No history found for user: {user_id}")
                return

            click.echo(f"\nHistory for user: {user_id} ({len(history_items)} items)")
            click.echo("-" * 80)
            click.echo(f"{'Request ID':<20} {'Text Preview':<30} {'Language':<10} {'Voice':<15}")
            click.echo("-" * 80)

            for item in history_items:
                text_preview = item['text'][:27] + "..." if len(item['text']) > 30 else item['text']
                voice_name = item['voice_name'] or 'default'
                voice_short = voice_name[:12] + "..." if len(voice_name) > 15 else voice_name

                click.echo(f"{item['request_id'][:17]:<20} {text_preview:<30} {item['language_code']:<10} {voice_short:<15}")

    except Exception as e:
        click.echo(f"Error fetching history: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
@click.pass_context
def config(ctx):
    """Show current configuration"""
    config = ctx.obj['config']

    click.echo("Current Configuration:")
    click.echo("-" * 40)
    click.echo(f"Project ID:    {config['project_id']}")
    click.echo(f"Bucket Name:   {config['bucket_name']}")
    click.echo(f"Location:      {config['location']}")
    click.echo(f"Credentials:   {config['credentials'] or 'Default credentials'}")
    click.echo(f"Verbose:       {config['verbose']}")


def download_audio_file(url: str, output_path: str, verbose: bool = False) -> None:
    """Download audio file from URL"""
    import requests

    if verbose:
        click.echo(f"Downloading audio to {output_path}...")

    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()

        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        if verbose:
            file_size = os.path.getsize(output_path)
            click.echo(f"Downloaded {file_size:,} bytes")

    except Exception as e:
        click.echo(f"Error downloading audio: {str(e)}", err=True)
        sys.exit(1)


def play_audio_file(file_path: str, verbose: bool = False) -> None:
    """Play audio file using system default player"""
    if verbose:
        click.echo(f"Playing audio file: {file_path}")

    try:
        import subprocess
        import platform

        system = platform.system()

        if system == "Darwin":  # macOS
            subprocess.run(["afplay", file_path])
        elif system == "Linux":
            subprocess.run(["aplay", file_path])
        elif system == "Windows":
            subprocess.run(["start", file_path], shell=True)
        else:
            click.echo("Audio playback not supported on this platform", err=True)

    except Exception as e:
        click.echo(f"Error playing audio: {str(e)}", err=True)


# Register additional commands
from src.cli.commands.text_file import register_text_commands
register_text_commands(cli)

# Register batch commands
from src.cli.commands.batch import batch
cli.add_command(batch)


if __name__ == '__main__':
    cli()