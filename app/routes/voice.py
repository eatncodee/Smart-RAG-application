from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.services.rag import chat_with_function_calling
from gtts import gTTS
import io


router=APIRouter()


async def procces_with_rag(user_text:str):
    response=chat_with_function_calling(user_message=user_text,conversation_history=None,temprature=0.9)

    if response:
        return response["answer"]
    

async def text_to_speech(text:str):
    tts =gTTS(text=text, lang='en', slow=False)

    audio_file = io.BytesIO()
    tts.write_to_fp(audio_file)
    
    audio_file.seek(0)
    audio_bytes = audio_file.read()

    return audio_bytes


async def voice_pipeline(text_1):
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
            data = await websocket.receive_json()
            user_text=data.get("text","")
            print(f"📥 Received {len(user_text)}")
            if not user_text:
                continue
            
            response_audio = await voice_pipeline(user_text)
            if response_audio:
                await websocket.send_bytes(response_audio)
                print(f"📤 Sent {len(response_audio)} bytes")
        
    except WebSocketDisconnect:
        print("❌ Voice client disconnected")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

