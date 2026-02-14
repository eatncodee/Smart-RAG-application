from fastapi import FastAPI,WebSocket,WebSocketDisconnect
from fastapi import APIRouter

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
