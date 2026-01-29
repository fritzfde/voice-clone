import sounddevice as sd
import soundfile as sf

DURATION = 30  # seconds
SAMPLE_RATE = 44100

print("🎙️ Recording... Speak clearly")
audio = sd.rec(
    int(DURATION * SAMPLE_RATE),
    samplerate=SAMPLE_RATE,
    channels=1,
    dtype="float32"
)
sd.wait()

sf.write("voice.wav", audio, SAMPLE_RATE)
print("✅ Saved voice.wav")
x
