from fastapi import FastAPI,WebSocket,WebSocketDisconnect
from fastapi import APIRouter
from app.services.streaming import stream_rag_response


router=APIRouter()


@router.websocket("/ws/echo")
async def websocket_echo(websocket:WebSocket):

    await websocket.accept()
    print("Client Connected")

    try:
        while True:
            message=await websocket.receive_text()
            print(f"📤 Recieved: {message}")

            response=f"Echo: {message}"
            await websocket.send_text(response)
            print(f"📤 Sent: {response}")
    
    except WebSocketDisconnect:
        print("❌ Client disconnected")

@router.websocket("/ws/chat")
async def websocket_chat(websocket:WebSocket):
    await websocket.accept()
    print("✅ Client connected to chat WebSocket")

    conversation_history = []

    try:
        while True:

            data=await websocket.receive_json()
            print(f"Recieved: {data}")

            message=data.get("message","")
            if not message:
                await websocket.send_json({
                        "type": "error",
                        "message": "No message provided"
                    })
                continue

            result = await stream_rag_response(
                user_message=message,
                conversation_history=conversation_history,
                websocket=websocket
            )   
            conversation_history=result.get("conversation_history",[])

            print(f"✅ Completed response for: {message}")
    
    except WebSocketDisconnect:
        print("❌ Client disconnected from chat")
    
    except Exception as e:
        print(f"❌ Error in chat WebSocket: {str(e)}")
        try:
            await websocket.send_json({
                "type": "error",
                "message": str(e)
            })
        except:
            pass
