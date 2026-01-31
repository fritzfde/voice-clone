#!/usr/bin/env python3
"""
Persistent TTS server - keeps model loaded in memory
Multi-language support for voice cloning
"""

import sys
import json
from flask import Flask, request, send_file
from TTS.api import TTS
import os
import tempfile
import argparse

app = Flask(__name__)

# Load model once at startup (this takes ~5-10 seconds)
print("🔄 Loading XTTS v2 model (one-time setup)...", file=sys.stderr)
tts = TTS(
    model_name="tts_models/multilingual/multi-dataset/xtts_v2",
    gpu=False  # M1 Mac uses CPU
)
print("✅ Model loaded and ready!", file=sys.stderr)

# Supported languages
SUPPORTED_LANGUAGES = [
    'en', 'es', 'fr', 'de', 'it', 'pt', 'pl', 'tr',
    'ru', 'nl', 'cs', 'ar', 'zh-cn', 'ja', 'ko', 'hu'
]


@app.route('/tts', methods=['POST'])
def generate_speech():
    """Generate speech from JSON request with language support"""
    try:
        data = request.get_json()
        voice_file = data.get('voice')
        text = data.get('text')
        language = data.get('language', 'en')  # Default to English

        if not voice_file or not text:
            return {'error': 'Missing voice or text'}, 400

        if not os.path.exists(voice_file):
            return {'error': f'Voice file not found: {voice_file}'}, 404

        # Validate language
        if language not in SUPPORTED_LANGUAGES:
            print(f"⚠️ Language '{language}' not supported, using 'en'", file=sys.stderr)
            language = 'en'

        # Create temp output file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
        output_path = temp_file.name
        temp_file.close()

        print(f"🎙️ Generating [{language.upper()}]: '{text[:50]}...'", file=sys.stderr)

        # Generate speech with specified language
        tts.tts_to_file(
            text=text,
            speaker_wav=voice_file,
            language=language,
            file_path=output_path
        )

        print(f"✅ Generated!", file=sys.stderr)

        # Send the file
        response = send_file(
            output_path,
            mimetype='audio/wav',
            as_attachment=False
        )

        # Clean up temp file after sending
        @response.call_on_close
        def cleanup():
            try:
                os.unlink(output_path)
            except:
                pass

        return response

    except Exception as e:
        import traceback
        print(f"❌ Error: {str(e)}", file=sys.stderr)
        traceback.print_exc()
        return {'error': str(e)}, 500


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return {
        'status': 'ready',
        'model': 'xtts_v2',
        'supported_languages': SUPPORTED_LANGUAGES
    }


@app.route('/languages', methods=['GET'])
def list_languages():
    """List all supported languages"""
    return {
        'languages': SUPPORTED_LANGUAGES,
        'language_names': {
            'en': 'English',
            'es': 'Spanish',
            'fr': 'French',
            'de': 'German',
            'it': 'Italian',
            'pt': 'Portuguese',
            'pl': 'Polish',
            'tr': 'Turkish',
            'ru': 'Russian',
            'nl': 'Dutch',
            'cs': 'Czech',
            'ar': 'Arabic',
            'zh-cn': 'Chinese',
            'ja': 'Japanese',
            'ko': 'Korean',
            'hu': 'Hungarian'
        }
    }


def cli_mode():
    """CLI mode for testing voice generation"""
    parser = argparse.ArgumentParser(description="XTTS Voice Test")
    parser.add_argument("--voice", type=str, help="Path to voice wav file")
    parser.add_argument("--text", type=str, help="Text to synthesize")
    parser.add_argument("--language", type=str, default="en", help="Language code (en, de, es, etc.)")
    parser.add_argument("--output", type=str, default="output.wav", help="Output file path")

    args, _ = parser.parse_known_args()

    if not args.voice or not args.text:
        return False  # Not CLI mode

    print("🎙️ CLI TTS MODE", file=sys.stderr)
    print(f"   Voice   : {args.voice}", file=sys.stderr)
    print(f"   Text    : {args.text}", file=sys.stderr)
    print(f"   Language: {args.language}", file=sys.stderr)
    print(f"   Output  : {args.output}", file=sys.stderr)

    if not os.path.exists(args.voice):
        print("❌ Voice file not found", file=sys.stderr)
        sys.exit(1)

    if args.language not in SUPPORTED_LANGUAGES:
        print(f"⚠️ Warning: '{args.language}' may not be supported", file=sys.stderr)
        print(f"   Supported: {', '.join(SUPPORTED_LANGUAGES)}", file=sys.stderr)

    print(f"\n🔄 Generating speech in {args.language}...", file=sys.stderr)

    tts.tts_to_file(
        text=args.text,
        speaker_wav=args.voice,
        language=args.language,
        file_path=args.output
    )

    print(f"✅ Saved to {args.output}", file=sys.stderr)
    sys.exit(0)


if __name__ == '__main__':
    # Check if we should run in CLI mode first
    is_cli = cli_mode()

    # If not CLI mode, start the server
    if not is_cli:
        print("\n🚀 Starting Multi-Language TTS Server...", file=sys.stderr)
        print(f"📡 Server: http://localhost:5000", file=sys.stderr)
        print(f"🌍 Languages: {len(SUPPORTED_LANGUAGES)} supported", file=sys.stderr)
        print(f"   {', '.join(SUPPORTED_LANGUAGES)}\n", file=sys.stderr)
        app.run(host='127.0.0.1', port=5000, debug=False)