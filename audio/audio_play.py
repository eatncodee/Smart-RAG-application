from pydub import AudioSegment
from pydub.playback import play
import time
from pydub.generators import Sine
sample="recorded_audio.wav"


def play_mp3_file():
    audio=AudioSegment.from_mp3(sample)

    print(f"Duration : {len(audio)} miliseconds")
    print(f"Rate : {audio.frame_rate} Hz")
    print(f"Channels :{audio.channels}")
    print(f"Framewidth : {audio.sample_width}")

    print("Playing audio")
    play (audio)
    print("Done")

def generate_tone_example():
    print("3. Generating a tone (440 Hz for 1 second)...")    
    tone = Sine(440).to_audio_segment(duration=1000)
    
    print("4. Playing tone...")
    play(tone)
    print("   Done!\n")

def creating_silence():
    print("creating_silence")

    silence=AudioSegment.silent(duration=2000)

    print(f"Silence created {len(silence)} ms")

if __name__=="__main__":
    print("1. Play MP3 file")
    print("2. Generate and play a tone")
    print("3. Create silence")
    print("4: play a tone")

    choice = input("\nEnter choice (1-4): ")
    
    if choice == "1":
        play_mp3_file()
    elif choice == "2":
        generate_tone_example()
    elif choice == "3":
        creating_silence()
    else:
        print("Invalid choice!")
