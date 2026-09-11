import io
import wave

from sarvamai import AsyncSarvamAI

from app.config import settings


sarvam_client = AsyncSarvamAI(api_subscription_key=settings.SARVAM_API_KEY)


async def speech_to_text(audio_bytes: bytes) -> dict:
    wav_buffer = io.BytesIO()
    with wave.open(wav_buffer, "wb") as wf:
        wf.setnchannels(1)        # mono
        wf.setsampwidth(2)        # 16-bit
        wf.setframerate(16000)    # 16kHz — Sarvam requires this
        wf.writeframes(audio_bytes)
    wav_buffer.seek(0)

    response = await sarvam_client.speech_to_text.transcribe(
        file=("audio.wav", wav_buffer, "audio/wav"),
        model="saarika:v2.5",
        language_code="unknown",
    )
    return {
        "transcript": response.transcript,
        "language_code": response.language_code,
    }
