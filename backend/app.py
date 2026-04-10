from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import cv2
import asyncio
import json

from utils import get_image_bytes, DisplayReader

app = FastAPI()
reader = DisplayReader()

VIDEO_PATH = "/Users/aida/Documents/GitHub/DisplayReaderPythonReactFastAPI/images/output.mp4"

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


@app.websocket("/ws")
async def websocket_connection(websocket: WebSocket):
    await websocket.accept()
    cap = None

    try:
        while True:
            data = await websocket.receive_text()

            if data == "start":
                if cap is None or not cap.isOpened():
                    cap = cv2.VideoCapture(VIDEO_PATH)

                if not cap.isOpened():
                    await websocket.send_text(
                        json.dumps(
                            {"type": "error", "message": "Cannot open video file"}
                        )
                    )
                    continue

                while True:
                    ok, frame = cap.read()

                    if not ok:
                        await websocket.send_text(
                            json.dumps(
                                {"type": "status", "message": "video_finished"}
                            )
                        )
                        break

                    reader.displayReader(frame)

                    await send_frame(websocket, 1, reader.getPureImage())
                    await send_frame(websocket, 2, reader.getCannyImage())
                    await send_frame(websocket, 3, reader.getImageContours())
                    if (reader.getMarkedDisplayImage() is not None):
                        await send_frame(websocket, 4, reader.getMarkedDisplayImage())

                    # Небольшая пауза, чтобы не забить websocket и CPU
                    await asyncio.sleep(0.03)

            elif data == "restart":
                if cap is not None:
                    cap.release()
                cap = cv2.VideoCapture(VIDEO_PATH)
                await websocket.send_text(
                    json.dumps({"type": "status", "message": "video_restarted"})
                )

            elif data == "stop":
                if cap is not None:
                    cap.release()
                    cap = None
                await websocket.send_text(
                    json.dumps({"type": "status", "message": "video_stopped"})
                )

            else:
                await websocket.send_text(
                    json.dumps({"type": "echo", "message": f"Unknown command: {data}"})
                )

    except WebSocketDisconnect:
        print("Client disconnected")

    except Exception as e:
        print("WebSocket error:", e)

    finally:
        if cap is not None:
            cap.release()