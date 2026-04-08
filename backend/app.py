from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware 
import cv2
from utils import get_image_bytes
from utils import DisplayReader


#------Read image------#
display_image = cv2.imread("C:/Users/user/Desktop/DisplayReaderPythonReactFastAPI-main/images/display.jpg")
reader=DisplayReader()
reader.displayReader(display_image)
if display_image is None:
    print("Cannot read image! Please, check the path!")
    pure_image_bytes=None
else:
    pure_image_bytes = get_image_bytes(reader.getPureImage(),1) 
    canny_image_bytes = get_image_bytes(reader.getCannyImage(),2)
    image_contours_bytes = get_image_bytes(reader.getImageContours(),3)
    marked_image_bytes = get_image_bytes(reader.getMarkedDisplayImage(),4)
app = FastAPI()
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
    return {"Markovka"}

@app.websocket("/ws")
async def websocket_connection(websocket: WebSocket):
    await websocket.accept()
    while True:
       data = await websocket.receive_text()
       await websocket.send_text(f"Message text was: {data}")
       if data == "start":
           if pure_image_bytes is not None:
            await websocket.send_bytes(pure_image_bytes)
            await websocket.send_bytes(canny_image_bytes)
            await websocket.send_bytes(image_contours_bytes)
            await websocket.send_bytes(marked_image_bytes)
           else: 
              await websocket.send_text("pure_image_bytes is none")
