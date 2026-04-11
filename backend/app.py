from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from schema import Parameters
import cv2
import asyncio
import json

from utils import get_image_bytes, DisplayReader

app = FastAPI()
reader = DisplayReader()

VIDEO_PATH = "C:/Users/user/Documents/GitHub/DisplayReaderPythonReactFastAPI/images/output.mp4"

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"message": "Markovka"}


async def send_frame(websocket: WebSocket, frame_type: int, frame):
    """
    Отправляем сначала JSON-метку, потом сами bytes картинки.
    Так фронт сможет понять, что именно пришло.
    """

    image_bytes = get_image_bytes(frame, frame_type)
    if image_bytes is None:
        return

    await websocket.send_bytes(image_bytes)



@app.post("/parameters/send")
def parameters_send(parameters: Parameters):
    reader.parameters_changing(parameters)
    return parameters

async def command_listener(websocket: WebSocket, state):
    while True:
        data = await websocket.receive_text()
        if data == "start":
            state["is_streaming"] = True
        elif data == "stop":
            state["is_streaming"] = False

            if state["cap"] is not None:
                state["cap"].release()
                state["cap"]  = None
            await websocket.send_text(
                json.dumps(
                    {"type":"status", "message":"video_stopped"}
                )
            )
        else:
            await websocket.send_text(
                json.dumps(
                    {"type":"echo", "message":f"Unknown command {data}"}
                )
            )

async def stream_video(websocket: WebSocket, state):
    while True:
        if not state["is_streaming"]:
            await asyncio.sleep(0.05)
            continue
        if state["cap"] is None or not state["cap"].isOpened():
            state["cap"] = cv2.VideoCapture(VIDEO_PATH)

            if not state["cap"].isOpened():
                await websocket.send_text(
                    json.dumps(
                        {"type":"status", "message": "Cannot open the video"}
                    )
                ) 
                state["is_streaming"] = False
                await asyncio.sleep(0.5)
                continue
        ok, frame = state["cap"].read()
        if not ok:
            await websocket.send_text(
                json.dumps(
                    {"type":"status", "message": "Video is finished"}
                )
            )
            state["cap"].release()
            state["cap"] = None
            state["is_streaming"] = False
            continue
        reader.displayReader(frame)
        await send_frame(websocket, 1, reader.getPureImage())
        await send_frame(websocket, 2, reader.getCannyImage())
        await send_frame(websocket, 3, reader.getImageContours())
        if reader.getMarkedDisplayImage() is not None:
            await websocket.send_text(
                json.dumps(
                    {"type": "displayStatus", "message":"true"}
                )
            )
            await send_frame(websocket, 4, reader.getMarkedDisplayImage())
        else: 
            await websocket.send_text(
                json.dumps(
                    {"type":"displayStatus", "message":"false"}
                )
            )
        await asyncio.sleep(0.03)

@app.websocket("/ws")
async def websocket_connection(websocket: WebSocket):
    await websocket.accept()
    state = {"is_streaming": False, "cap":None}

    try:
       await asyncio.gather(command_listener(websocket, state), stream_video(websocket, state))
    except WebSocketDisconnect:
        print("Client disconnected")

    except Exception as e:
        print("WebSocket error:", e)

    finally:
        if state["cap"] is not None:
            state["cap"].release()