from pydub import AudioSegment
import os

def mp3_to_wav(input_file,output_file):
    audio=AudioSegment.from_mp3(input_file)
    print(f"Input : {len(audio)}ms,  {audio.frame_rate} Hz , {audio.channel}")

    audio.export(output_file, format="wav")
    print(f"Saved to {output_file}\n")


def change_sample_rate(input_file,output_file,new_rate=16000):
    audio=AudioSegment.from_file(input_file)

    print(f"Original {audio.frame_rate}")

    audio.set_frame_rate(new_rate)
    
    print(f"New : {audio.frame_rate}")

    audio.export(output_file)
    print(f"Saved to: {output_file}\n")

def convert_to_mono(input_file, output_file):
    audio = AudioSegment.from_file(input_file)
    
    print(f"Original: {audio.channels} channels")
    audio = audio.set_channels(1)
    
    print(f"New: {audio.channels} channels")
    
    audio.export(output_file, format="wav")
    
    print(f"Saved to: {output_file}\n")


def prepare_for_speech_api(input_file, output_file):
    audio = AudioSegment.from_file(input_file)

    audio = audio.set_frame_rate(16000)  
    audio = audio.set_channels(1)        
    audio = audio.set_sample_width(2)   
    
    print(f"Output format:")
    print(f"  Duration: {len(audio)}ms")
    print(f"  Sample rate: {audio.frame_rate}Hz")
    print(f"  Channels: {audio.channels}")
    print(f"  Sample width: {audio.sample_width} bytes\n")
    
    audio.export(output_file, format="wav")
    
    print(f"✅ Saved to: {output_file}")
    print("Ready for Speech-to-Text API!")


if __name__ == "__main__":
    print("Choose conversion:")
    print("1. MP3 to WAV")
    print("2. Change sample rate")
    print("3. Convert to mono")
    print("4. Prepare for Speech API (full pipeline)")
    
    choice = input("\nEnter choice (1-4): ")
    
    if choice == "1":
        mp3_to_wav("input.mp3", "output.wav")
    elif choice == "2":
        change_sample_rate("input.wav", "output_16k.wav", 16000)
    elif choice == "3":
        convert_to_mono("input.wav", "output_mono.wav")
    elif choice == "4":
        prepare_for_speech_api("input.mp3", "output_ready.wav")
    else:
        print("Invalid choice!")