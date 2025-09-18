"""
Batch processing commands for TTS CLI
"""

import click
import json
import csv
import os
from pathlib import Path
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed


@click.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.option('--output-dir', '-o', type=click.Path(), default='./batch_output',
              help='Output directory for generated audio files')
@click.option('--format', 'input_format', type=click.Choice(['txt', 'csv', 'json']),
              help='Input file format (auto-detected if not specified)')
@click.option('--language', '-l', default='en-US',
              help='Default language code')
@click.option('--voice', help='Default voice name')
@click.option('--audio-format', type=click.Choice(['MP3', 'LINEAR16', 'OGG_OPUS']),
              default='MP3', help='Audio output format')
@click.option('--workers', type=int, default=3,
              help='Number of concurrent workers')
@click.option('--continue-on-error', is_flag=True,
              help='Continue processing even if some items fail')
@click.pass_context
def batch(ctx, input_file, output_dir, input_format, language, voice,
          audio_format, workers, continue_on_error):
    """Process multiple texts in batch mode

    Input formats:
    - txt: One text per line
    - csv: Columns: text, language, voice, output_name
    - json: Array of objects with text, language, voice, output_name

    Examples:
        gcp-tts batch texts.txt
        gcp-tts batch data.csv --format csv --workers 5
        gcp-tts batch batch.json --output-dir ./audio
    """
    tts_manager = ctx.obj['tts_manager']
    config = ctx.obj['config']
    verbose = config['verbose']

    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Auto-detect format if not specified
    if not input_format:
        file_ext = Path(input_file).suffix.lower()
        if file_ext == '.csv':
            input_format = 'csv'
        elif file_ext == '.json':
            input_format = 'json'
        else:
            input_format = 'txt'

    # Load batch data
    try:
        batch_items = load_batch_data(input_file, input_format, language, voice)
        click.echo(f"Loaded {len(batch_items)} items for processing")
    except Exception as e:
        click.echo(f"Error loading batch data: {str(e)}", err=True)
        return

    # Process items
    results = []
    failed_items = []

    if verbose:
        click.echo(f"Processing with {workers} workers...")

    with ThreadPoolExecutor(max_workers=workers) as executor:
        # Submit all tasks
        future_to_item = {}
        for i, item in enumerate(batch_items):
            future = executor.submit(process_batch_item, tts_manager, item, output_path, i, verbose)
            future_to_item[future] = item

        # Collect results
        with click.progressbar(as_completed(future_to_item), length=len(batch_items),
                              label='Processing texts') as bar:
            for future in bar:
                item = future_to_item[future]
                try:
                    result = future.result()
                    results.append(result)
                    if verbose and result['success']:
                        click.echo(f"✓ {result['output_file']}")
                except Exception as e:
                    failed_items.append({'item': item, 'error': str(e)})
                    if not continue_on_error:
                        click.echo(f"Error processing item: {str(e)}", err=True)
                        break
                    elif verbose:
                        click.echo(f"✗ Failed: {str(e)}")

    # Summary
    successful = len([r for r in results if r.get('success', False)])
    failed = len(failed_items)

    click.echo(f"\nBatch processing completed:")
    click.echo(f"  ✓ Successful: {successful}")
    click.echo(f"  ✗ Failed: {failed}")
    click.echo(f"  📁 Output directory: {output_dir}")

    # Save results log
    save_batch_results(results, failed_items, output_path)

    if failed_items and not continue_on_error:
        ctx.exit(1)


def load_batch_data(file_path: str, format_type: str, default_language: str,
                   default_voice: str) -> List[Dict[str, Any]]:
    """Load batch data from file"""
    items = []

    if format_type == 'txt':
        with open(file_path, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f):
                text = line.strip()
                if text:
                    items.append({
                        'text': text,
                        'language': default_language,
                        'voice': default_voice,
                        'output_name': f'batch_{i:04d}'
                    })

    elif format_type == 'csv':
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader):
                items.append({
                    'text': row.get('text', ''),
                    'language': row.get('language', default_language),
                    'voice': row.get('voice', default_voice),
                    'output_name': row.get('output_name', f'batch_{i:04d}')
                })

    elif format_type == 'json':
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, list):
                for i, item in enumerate(data):
                    items.append({
                        'text': item.get('text', ''),
                        'language': item.get('language', default_language),
                        'voice': item.get('voice', default_voice),
                        'output_name': item.get('output_name', f'batch_{i:04d}')
                    })

    return items


def process_batch_item(tts_manager, item: Dict[str, Any], output_dir: Path,
                      index: int, verbose: bool) -> Dict[str, Any]:
    """Process a single batch item"""
    try:
        text = item['text']
        if not text.strip():
            return {'success': False, 'error': 'Empty text', 'item_index': index}

        # Generate speech
        result = tts_manager.process_text_to_speech(
            text=text,
            language_code=item['language'],
            voice_name=item['voice'],
            user_id='batch-cli'
        )

        if not result['success']:
            return {
                'success': False,
                'error': result['error'],
                'item_index': index
            }

        # Download audio file
        audio_url = result['audio_url']
        output_name = item['output_name']
        output_file = output_dir / f"{output_name}.mp3"

        download_audio_from_url(audio_url, str(output_file))

        return {
            'success': True,
            'item_index': index,
            'output_file': str(output_file),
            'duration': result['duration_seconds'],
            'characters': result['character_count'],
            'processing_time': result['processing_time_ms']
        }

    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'item_index': index
        }


def download_audio_from_url(url: str, output_path: str) -> None:
    """Download audio file from URL"""
    import requests

    response = requests.get(url, stream=True)
    response.raise_for_status()

    with open(output_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)


def save_batch_results(results: List[Dict], failed_items: List[Dict],
                      output_dir: Path) -> None:
    """Save batch processing results to log file"""
    log_file = output_dir / 'batch_results.json'

    log_data = {
        'total_items': len(results) + len(failed_items),
        'successful': len([r for r in results if r.get('success', False)]),
        'failed': len(failed_items),
        'results': results,
        'failed_items': failed_items,
        'timestamp': click.DateTime().convert(click.DateTime().name, None, None)
    }

    with open(log_file, 'w', encoding='utf-8') as f:
        json.dump(log_data, f, indent=2, default=str)

    click.echo(f"Results saved to: {log_file}")


@click.command()
@click.argument('directory', type=click.Path(exists=True))
@click.option('--pattern', default='*.txt', help='File pattern to match')
@click.option('--output-dir', '-o', type=click.Path(), default='./converted_files',
              help='Output directory for audio files')
@click.option('--language', '-l', default='en-US', help='Language code')
@click.option('--voice', help='Voice name')
@click.option('--recursive', '-r', is_flag=True, help='Process subdirectories')
@click.pass_context
def convert_files(ctx, directory, pattern, output_dir, language, voice, recursive):
    """Convert all text files in a directory to speech

    Examples:
        gcp-tts convert-files ./texts/
        gcp-tts convert-files ./docs/ --pattern "*.md" --recursive
    """
    from glob import glob
    import fnmatch

    tts_manager = ctx.obj['tts_manager']
    config = ctx.obj['config']
    verbose = config['verbose']

    # Find matching files
    files_to_process = []
    directory_path = Path(directory)

    if recursive:
        for file_path in directory_path.rglob(pattern):
            if file_path.is_file():
                files_to_process.append(file_path)
    else:
        for file_path in directory_path.glob(pattern):
            if file_path.is_file():
                files_to_process.append(file_path)

    if not files_to_process:
        click.echo(f"No files found matching pattern '{pattern}'")
        return

    click.echo(f"Found {len(files_to_process)} files to process")

    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Process each file
    for file_path in files_to_process:
        try:
            if verbose:
                click.echo(f"Processing: {file_path}")

            # Read file content
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read().strip()

            if not text:
                if verbose:
                    click.echo(f"Skipping empty file: {file_path}")
                continue

            # Generate speech
            result = tts_manager.process_text_to_speech(
                text=text,
                language_code=language,
                voice_name=voice,
                user_id='convert-cli'
            )

            if result['success']:
                # Download audio
                output_file = output_path / f"{file_path.stem}.mp3"
                download_audio_from_url(result['audio_url'], str(output_file))

                if verbose:
                    click.echo(f"✓ Created: {output_file}")
            else:
                click.echo(f"✗ Failed to process {file_path}: {result['error']}")

        except Exception as e:
            click.echo(f"✗ Error processing {file_path}: {str(e)}")

    click.echo(f"File conversion completed. Output saved to: {output_dir}")