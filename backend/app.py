from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from schema import Parameters
import cv2
import asyncio
import json

from utils import get_image_bytes, DisplayReader

app = FastAPI()
reader = DisplayReader()

VIDEO_PATH = "/Users/aida/Documents/GitHub/DisplayReaderPythonReactFastAPI/images/output.mp4"
IMAGE_PATH= "/Users/aida/Documents/GitHub/DisplayReaderPythonReactFastAPI/images/display.jpg"

state = {"is_streaming": False, "cap":None, "last_frame": None}
state_image = {"is_streaming" : False, "img": None}

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
    state["is_streaming"] = False
    state_image["img"] = state["last_frame"]
    state_image["is_streaming"] = True
    return parameters

async def command_listener(websocket: WebSocket, state, state_image):
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
                ))
        elif data == "image":
            if state["cap"] is not None: 
                state_image["is_streaming"] = True
                state_image["img"] = state["last_frame"]    
                state["is_streaming"] = False
                if state["cap"] is not None:
                    state["cap"].release()
                    state["cap"] = None 
                await websocket.send_text(
                    json.dumps(
                        {"type":"status", "message":"VideoCapturing is stopped. ImagePhase is started!"}
                    )
                )   
        else:
            await websocket.send_text(
                json.dumps(
                    {"type":"echo", "message":f"Unknown command {data}"}
                )
            )

async def image_analys(websocket: WebSocket, state_image):
    while True:
        if not state_image["is_streaming"]:
            await asyncio.sleep(0.05)
            continue

        if state_image["img"] is None:
            await websocket.send_text(
                json.dumps({"type": "status", "message": "IMG is none"})
            )
            state_image["is_streaming"] = False
            await asyncio.sleep(0.05)
            continue

        reader.displayReader(state_image["img"])
        await send_frame(websocket, 1, reader.getPureImage())
        await send_frame(websocket, 2, reader.getCannyImage())
        await send_frame(websocket, 3, reader.getImageContours())

        if reader.getMarkedDisplayImage() is not None:
            await websocket.send_text(
                json.dumps({"type": "displayStatus", "message": "true"})
            )
            await websocket.send_text(
                json.dumps({"type": "whole_digit", "message": reader.whole_digit})
            )
            await send_frame(websocket, 4, reader.getMarkedDisplayImage())
        else:
            await websocket.send_text(
                json.dumps({"type": "displayStatus", "message": "false"})
            )

        state_image["is_streaming"] = False
        state_image["img"] = None

        await websocket.send_text(
            json.dumps(
                {
                    "type": "status",
                    "message": "The image was passed through the displayReader"
                }
            )
        ) 
async def stream_video(websocket: WebSocket, state):
    while True:
        if not state["is_streaming"]:
            await asyncio.sleep(0.05)
            continue
        #-------VideoCapture-------#
        if state["cap"] is None or not state["cap"].isOpened():
            state["cap"] = cv2.VideoCapture(0)

        #------Image------#
        # if state["img"] is None:
        #     state["img"] = cv2.imread(IMAGE_PATH);

        #------VideoCapture-----#
            if not state["cap"].isOpened():
                await websocket.send_text(
                    json.dumps(
                        {"type":"status", "message": "Cannot open the video"}
                    )
                ) 
                state["is_streaming"] = False
                await asyncio.sleep(0.5)
                continue

            #-----Image------#
            # if state["img"] is None:
            #     await websocket.send_text(json.dumps({
            #         "type":"status","message":"Cannot open the Image" 
            #     }))
            #     state["is_streaming"] = False
            #     await asyncio.sleep(0.5)
            #     continue
            
        #-----VideoCapture----#    
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
        state["last_frame"] = frame.copy()
        reader.displayReader(frame)

        #------Image--------#
        # reader.displayReader(state["img"])
        await send_frame(websocket, 1, reader.getPureImage())
        await send_frame(websocket, 2, reader.getCannyImage())
        await send_frame(websocket, 3, reader.getImageContours())
        if reader.getMarkedDisplayImage() is not None:
            await websocket.send_text(
                json.dumps(
                    {"type": "displayStatus", "message":"true"}
                )
            )
            await websocket.send_text(
                json.dumps(
                    {"type": "whole_digit", "message": reader.whole_digit}
                )
            )
            await send_frame(websocket, 4, reader.getMarkedDisplayImage())
        elif(reader.getMarkedDisplayImage() is None): 
            await websocket.send_text(
                json.dumps(
                    {"type":"displayStatus", "message":"false"}
                )
            )
        #----Image-----#
        # state["is_streaming"] = False    
        await asyncio.sleep(0.03)

@app.websocket("/ws")
async def websocket_connection(websocket: WebSocket):
    await websocket.accept()

    try:
       await asyncio.gather(command_listener(websocket, state,state_image), stream_video(websocket, state), image_analys(websocket, state_image))
    except WebSocketDisconnect:
        print("Client disconnected")

    except Exception as e:
        print("WebSocket error:", e)

    finally:
        #------VideoCapture------#
        if state["cap"] is not None:
            state["cap"].release()