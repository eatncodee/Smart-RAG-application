import pyaudio
import time
import wave
import os

CHUNK = 1024  # How many samples to read at once
FORMAT = pyaudio.paInt16  # 16-bit audio
CHANNELS = 1  # Mono
RATE = 16000  # 16kHz (good for speech)
RECORD_SECONDS = 5  # Record for 5 seconds
OUTPUT_FILE = "recorded_audio.wav"

def record_audio():
    audio =pyaudio.PyAudio()
    stream = audio.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        input=True, 
        frames_per_buffer=CHUNK
    )

    print(f"Step 3: Recording for {RECORD_SECONDS} seconds...")
    print("🎤 SPEAK NOW!")
    frames = [] 
    
    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)
        
        if i % 10 == 0:
            print(".", end="", flush=True)
    
    print("\n\nStep 4: Recording finished!")
    
    stream.stop_stream()
    stream.close()
    audio.terminate()
    
    print("Step 5: Saving to file...")
    
    with wave.open(OUTPUT_FILE, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(audio.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
    
    print(f"✅ Saved to: {OUTPUT_FILE}")
    print(f"   Duration: {RECORD_SECONDS} seconds")
    print(f"   Sample rate: {RATE} Hz")
    print(f"   Channels: {CHANNELS}")


if __name__ == "__main__":
    try:
        record_audio()
        
        print("\n--- Recording Analysis ---")
        print(f"File size: {os.path.getsize(OUTPUT_FILE)} bytes")
        
        expected_size = RATE * RECORD_SECONDS * CHANNELS * 2 
        print(f"Expected size: ~{expected_size} bytes")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nTroubleshooting:")
        print("- Make sure your microphone is connected")
        print("- Check microphone permissions")
        print("- Try running: pip install pyaudio")