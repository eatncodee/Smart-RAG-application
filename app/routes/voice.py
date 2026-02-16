from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.services.rag import chat_with_function_calling
from gtts import gTTS
import io


router=APIRouter()


async def procces_with_rag(user_text:str,conversation_history :list | None=None):
    response=chat_with_function_calling(user_message=user_text,conversation_history=conversation_history,temprature=0.9)

    if response:
        return response
    

async def text_to_speech(text:str):
    tts =gTTS(text=text, lang='en', slow=False)

    audio_file = io.BytesIO()
    tts.write_to_fp(audio_file)
    
    audio_file.seek(0)
    audio_bytes = audio_file.read()

    return audio_bytes


@router.websocket("/ws/voice")
async def voice_chat(websocket: WebSocket):
    await websocket.accept()
    print("✅ Voice client connected")
    conversation_history=[]
    try:
        while True:
            data = await websocket.receive_json()
            user_text=data.get("text","")
            print(f"📥 Received {len(user_text)}")
            if not user_text:
                continue

            result =await procces_with_rag(user_text,conversation_history)

            if result :
                conversation_history=result.get("conversation_history",[])
                data=result.get("answer","")
                audio_output=await text_to_speech(data)
            if audio_output:
                await websocket.send_bytes(audio_output)
                print(f"📤 Sent {len(audio_output)} bytes")
        
    except WebSocketDisconnect:
        print("❌ Voice client disconnected")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

