from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydub.generators import Sine
from app.services.rag import chat_with_function_calling

router=APIRouter()


async def speech_to_text(audio_bytes):
    l="hi i am demo text from spech"
    return l

async def procces_with_rag(user_text:str):
    response=chat_with_function_calling(user_message=user_text,conversation_history=None,temprature=0.9)

    if response:
        return response["answer"]
    

async def text_to_speech(text:str):
    audio = Sine(440).to_audio_segment(duration=1000)
    audio_bytes=audio.raw_data

    return audio_bytes


async def voice_pipeline(audio_input):
    text_1=await speech_to_text(audio_input)
    answer_t=await procces_with_rag(text_1)
    if answer_t:
        audio_output=await text_to_speech(answer_t)
    return audio_output

@router.websocket("/ws/voice")
async def voice_chat(websocket: WebSocket):
    await websocket.accept()
    print("✅ Voice client connected")
    
    try:
        while True:
            audio_bytes = await websocket.receive_bytes()
            print(f"📥 Received {len(audio_bytes)} bytes")
            
            response_audio = await voice_pipeline(audio_bytes)
            if response_audio:
                await websocket.send_bytes(response_audio)
                print(f"📤 Sent {len(response_audio)} bytes")
        
    except WebSocketDisconnect:
        print("❌ Voice client disconnected")



