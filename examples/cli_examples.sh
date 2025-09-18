#!/bin/bash

# Google Cloud Text-to-Speech CLI Examples
# Demonstrates various CLI usage patterns and features

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}Google Cloud Text-to-Speech CLI Examples${NC}"
echo "============================================"
echo ""

# Check if CLI is installed
if ! command -v gcp-tts &> /dev/null; then
    echo "Error: gcp-tts CLI not found. Please install first:"
    echo "./scripts/install-cli.sh"
    exit 1
fi

# Create output directory
mkdir -p ./cli_examples_output

echo -e "${GREEN}1. Basic Text-to-Speech${NC}"
echo "Converting simple text to speech..."
gcp-tts synthesize "Hello, world! This is a test of the Google Cloud Text-to-Speech CLI." \
    --output ./cli_examples_output/basic_hello.mp3

echo ""
echo -e "${GREEN}2. Custom Voice and Language${NC}"
echo "Using Spanish language with Neural2 voice..."
gcp-tts synthesize "¡Hola, mundo! Bienvenidos al servicio de síntesis de voz." \
    --language es-ES \
    --voice es-ES-Neural2-A \
    --output ./cli_examples_output/spanish_hello.mp3

echo ""
echo -e "${GREEN}3. Adjusting Speech Parameters${NC}"
echo "Faster speech with higher pitch..."
gcp-tts synthesize "This text is spoken faster and with a higher pitch." \
    --speed 1.5 \
    --pitch 3.0 \
    --voice en-US-Neural2-A \
    --output ./cli_examples_output/fast_high.mp3

echo ""
echo -e "${GREEN}4. SSML Example${NC}"
echo "Using Speech Synthesis Markup Language..."
cat > ./cli_examples_output/sample.ssml << 'EOF'
<speak>
  Welcome to our <emphasis level="strong">advanced</emphasis> text-to-speech service.
  <break time="1s"/>
  This sentence has a <prosody rate="slow">slow section</prosody> and a
  <prosody rate="fast">fast section</prosody>.
  <break time="2s"/>
  We can also change the <prosody pitch="+5st">pitch</prosody> of our voice.
</speak>
EOF

gcp-tts synthesize --file ./cli_examples_output/sample.ssml \
    --ssml \
    --voice en-US-Neural2-A \
    --output ./cli_examples_output/ssml_demo.mp3

echo ""
echo -e "${GREEN}5. File Processing${NC}"
echo "Converting text file to speech..."
cat > ./cli_examples_output/sample_text.txt << 'EOF'
The Google Cloud Text-to-Speech API enables developers to synthesize natural-sounding
speech with hundreds of voices, available in multiple languages and variants.
It applies DeepMind's groundbreaking research in WaveNet and Google's powerful
neural networks to deliver the highest fidelity possible.
EOF

gcp-tts synthesize --file ./cli_examples_output/sample_text.txt \
    --voice en-US-Neural2-C \
    --output ./cli_examples_output/file_processing.mp3

echo ""
echo -e "${GREEN}6. Batch Processing${NC}"
echo "Creating batch input files and processing..."

# Create CSV batch file
cat > ./cli_examples_output/batch_input.csv << 'EOF'
text,language,voice,output_name
"Welcome to our service",en-US,en-US-Neural2-A,welcome
"Bienvenido a nuestro servicio",es-ES,es-ES-Neural2-B,bienvenido
"Bienvenue à notre service",fr-FR,fr-FR-Neural2-A,bienvenue
"Willkommen bei unserem Service",de-DE,de-DE-Neural2-A,willkommen
EOF

gcp-tts batch ./cli_examples_output/batch_input.csv \
    --output-dir ./cli_examples_output/batch_results \
    --workers 2

echo ""
echo -e "${GREEN}7. Different Audio Formats${NC}"
echo "Generating audio in different formats..."

# MP3 (default)
gcp-tts synthesize "This is MP3 format" \
    --format MP3 \
    --output ./cli_examples_output/format_mp3.mp3

# WAV (LINEAR16)
gcp-tts synthesize "This is WAV format" \
    --format LINEAR16 \
    --output ./cli_examples_output/format_wav.wav

# OGG Opus
gcp-tts synthesize "This is OGG format" \
    --format OGG_OPUS \
    --output ./cli_examples_output/format_ogg.ogg

echo ""
echo -e "${GREEN}8. Voice Discovery${NC}"
echo "Listing available voices..."

# List Neural2 voices for English
echo "Neural2 voices for English (US):"
gcp-tts voices --language en-US --type neural2

echo ""
echo "All supported languages:"
gcp-tts languages

echo ""
echo -e "${GREEN}9. Advanced SSML Features${NC}"
echo "Creating advanced SSML with multiple features..."
cat > ./cli_examples_output/advanced.ssml << 'EOF'
<speak>
  <par>
    <media xml:id="question" soundLevel="+2.28dB">
      <speak>
        <prosody rate="medium" pitch="+2st">
          Did you know that you can control multiple aspects of speech synthesis?
        </prosody>
      </speak>
    </media>
  </par>
  <break time="1s"/>
  <seq>
    <media begin="0.5s">
      <speak>
        You can control <emphasis level="moderate">emphasis</emphasis>,
        <prosody rate="slow">speaking rate</prosody>,
        <prosody pitch="-2st">pitch</prosody>,
        and even add <break time="500ms"/> pauses.
      </speak>
    </media>
  </seq>
  <break time="1s"/>
  <prosody rate="fast" pitch="+1st">
    This opens up many possibilities for creating engaging audio content!
  </prosody>
</speak>
EOF

gcp-tts synthesize --file ./cli_examples_output/advanced.ssml \
    --ssml \
    --voice en-US-Neural2-A \
    --output ./cli_examples_output/advanced_ssml.mp3

echo ""
echo -e "${GREEN}10. News-Style Voice${NC}"
echo "Using news-style voice for professional content..."
cat > ./cli_examples_output/news_content.txt << 'EOF'
Good evening. In technology news today, artificial intelligence continues to advance
at a rapid pace. Google Cloud's Text-to-Speech service now offers even more natural
sounding voices, making it easier than ever to create professional audio content.
Back to you in the studio.
EOF

gcp-tts synthesize --file ./cli_examples_output/news_content.txt \
    --voice en-US-News-K \
    --output ./cli_examples_output/news_broadcast.mp3

echo ""
echo -e "${GREEN}11. Multiple Text Files Conversion${NC}"
echo "Converting multiple text files..."
mkdir -p ./cli_examples_output/multiple_texts

# Create multiple text files
echo "Chapter 1: Introduction to AI" > ./cli_examples_output/multiple_texts/chapter1.txt
echo "Chapter 2: Machine Learning Basics" > ./cli_examples_output/multiple_texts/chapter2.txt
echo "Chapter 3: Deep Learning Applications" > ./cli_examples_output/multiple_texts/chapter3.txt

gcp-tts convert-files ./cli_examples_output/multiple_texts/ \
    --pattern "*.txt" \
    --voice en-US-Neural2-A \
    --output-dir ./cli_examples_output/converted_chapters

echo ""
echo -e "${GREEN}12. Configuration Check${NC}"
echo "Checking current CLI configuration..."
gcp-tts config

echo ""
echo -e "${YELLOW}Examples completed!${NC}"
echo ""
echo "Generated files:"
echo "=================="
find ./cli_examples_output -name "*.mp3" -o -name "*.wav" -o -name "*.ogg" | sort

echo ""
echo "Batch processing results:"
if [ -f ./cli_examples_output/batch_results/batch_results.json ]; then
    echo "Batch processing log saved to: ./cli_examples_output/batch_results/batch_results.json"
    echo "Number of files in batch output:"
    find ./cli_examples_output/batch_results -name "*.mp3" | wc -l
fi

echo ""
echo "To listen to the generated audio files:"
echo "========================================="
echo "# Play with system default player (Linux/macOS/Windows)"
echo "gcp-tts synthesize \"Test playback\" --play"
echo ""
echo "# Or manually open the files:"
echo "ls -la ./cli_examples_output/*.mp3"
echo ""
echo "For more examples and documentation, see:"
echo "- docs/CLI_USAGE.md"
echo "- examples/batch_samples/"