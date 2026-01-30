#!/usr/bin/env python3
"""
Persistent TTS server - keeps model loaded in memory
Much faster than loading model for each request!
"""

import sys
import json
from flask import Flask, request, send_file
from TTS.api import TTS
import os
import tempfile

app = Flask(__name__)

# Load model once at startup (this takes ~5-10 seconds)
print("🔄 Loading XTTS v2 model (one-time setup)...", file=sys.stderr)
tts = TTS(
    model_name="tts_models/multilingual/multi-dataset/xtts_v2",
    gpu=False  # M1 Mac uses CPU
)
print("✅ Model loaded and ready!", file=sys.stderr)


@app.route('/tts', methods=['POST'])
def generate_speech():
    """Generate speech from JSON request"""
    try:
        data = request.get_json()
        voice_file = data.get('voice')
        text = data.get('text')
        
        if not voice_file or not text:
            return {'error': 'Missing voice_file or text'}, 400
        
        if not os.path.exists(voice_file):
            return {'error': f'Voice file not found: {voice_file}'}, 404
        
        # Create temp output file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
        output_path = temp_file.name
        temp_file.close()
        
        print(f"🎙️ Generating: '{text[:50]}...'", file=sys.stderr)
        
        # Generate speech (model already loaded - FAST!)
        tts.tts_to_file(
            text=text,
            speaker_wav=voice_file,
            language="en",
            file_path=output_path
        )
        
        print(f"✅ Generated in <1 second!", file=sys.stderr)
        
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
    return {'status': 'ready', 'model': 'xtts_v2'}


if __name__ == '__main__':
    print("\n🚀 TTS Server Starting on http://localhost:5000", file=sys.stderr)
    print("📡 Ready to receive requests...\n", file=sys.stderr)
    app.run(host='127.0.0.1', port=5000, debug=False)
