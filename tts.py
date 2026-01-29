#!/usr/bin/env python3
"""
CLI-friendly TTS for Node.js integration
Usage: python tts.py --voice voice.wav --text "Hello" --output output.wav
"""

import argparse
import sys
from TTS.api import TTS

def generate_speech(voice_file, text, output_file):
    """Generate speech using voice cloning"""
    try:
        print(f"Loading XTTS model...", file=sys.stderr)
        
        tts = TTS(
            model_name="tts_models/multilingual/multi-dataset/xtts_v2",
            gpu=False  # M1 Mac uses MPS, not CUDA
        )
        
        print(f"Generating: '{text[:50]}...'", file=sys.stderr)
        
        tts.tts_to_file(
            text=text,
            speaker_wav=voice_file,
            language="en",
            file_path=output_file
        )
        
        print(f"✅ Generated: {output_file}", file=sys.stderr)
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}", file=sys.stderr)
        return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate speech using voice cloning')
    parser.add_argument('--voice', required=True, help='Path to reference voice WAV file')
    parser.add_argument('--text', required=True, help='Text to synthesize')
    parser.add_argument('--output', required=True, help='Output WAV file path')
    
    args = parser.parse_args()
    
    success = generate_speech(args.voice, args.text, args.output)
    sys.exit(0 if success else 1)