import { useState, useEffect, useRef } from "react";
import "../styles/ConnectionSettings.css";
function ConnectionSettings() {
  const [websocket, setWebsocket] = useState(null);
  const [connection, setConnection] = useState("connecting");
  const pureImageCanvasRef = useRef(null);
  const cannyImageCanvasRef = useRef(null);
  const imageContoursCanvasRef = useRef(null);
  const markedImageCanvasRef = useRef(null);

  const open_connection = () => {
    const socket = new WebSocket("http://127.0.0.1:8000/ws");
    socket.binaryType = "arraybuffer";
    setWebsocket(socket);
  };
  const close_connection = () => {
    if (websocket.readyState === WebSocket.OPEN) {
      websocket.close();
    }
  };
  const start_translation = () => {
    if (connection !== "Connected") {
      alert("Connection is closed!");
    } else {
      websocket.send("start");
    }
  };
  if (websocket) {
    websocket.onopen = () => {
      setConnection("Connected");
    };

    websocket.onmessage = async (event) => {
      if (event.data instanceof ArrayBuffer) {
        const uint8 = new Uint8Array(event.data);
        const frame_type = uint8[0];
        const imageBytes = uint8.slice(1);

        const blob = new Blob([imageBytes], {type: "image/jpeg"});
        console.log("RecievedBytes: ", uint8);
        console.log("ImageType: ", frame_type);
        console.log("ImageBytes: ", imageBytes);

        if(frame_type == 1){
          const bitmap = await createImageBitmap(blob);
          const canvas = pureImageCanvasRef.current;
          const ctx = canvas.getContext("2d");

          ctx.clearRect(0, 0, canvas.width, canvas.height);
          ctx.drawImage(bitmap, 0, 0, canvas.width, canvas.height);

          bitmap.close();
        }else if(frame_type == 2){
          const bitmap = await createImageBitmap(blob);
          const canvas = cannyImageCanvasRef.current;
          const ctx = canvas.getContext("2d");

          ctx.clearRect(0, 0, canvas.width, canvas.height);
          ctx.drawImage(bitmap, 0, 0, canvas.width, canvas.height);

          bitmap.close();
        }else if(frame_type == 3){
          const bitmap = await createImageBitmap(blob);
          const canvas = imageContoursCanvasRef.current;
          const ctx = canvas.getContext("2d");

          ctx.clearRect(0, 0, canvas.width, canvas.height);
          ctx.drawImage(bitmap, 0, 0, canvas.width, canvas.height);

          bitmap.close();
        }else if(frame_type == 4){
          const bitmap = await createImageBitmap(blob);
          const canvas = markedImageCanvasRef.current;
          const ctx = canvas.getContext("2d");

          ctx.clearRect(0, 0, canvas.width, canvas.height);
          ctx.drawImage(bitmap, 0, 0, canvas.width, canvas.height);

          bitmap.close();
        }
        /*. #----Drawing on canvas-----#
        const bitmap = await createImageBitmap(event.data);
        const canvas = canvasRef.current;
        const ctx = canvas.getContext("2d");

        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.drawImage(bitmap, 0, 0, canvas.width, canvas.height);

        bitmap.close();
      }
        */
      };
    };
    websocket.onclose = () => {
      setConnection("Disconnected");
    };
  }

  return (
    <div className="main-container">
      <div className="connection-settings-container">
        <button onClick={open_connection} className="connection-btn">
          Connect
        </button>
        <button onClick={close_connection} className="connection-btn">
          Disconnect
        </button>
        <span>
          Status:{" "}
          <span
            className={
              connection === "Connected"
                ? "connection-status-open"
                : "connection-status-close"
            }
          >
            {connection}
          </span>
        </span>
        <button onClick={start_translation} className="translation-btn">
          Start translation
        </button>
      </div>
      <div className="canvas-container">
        <canvas
          ref={pureImageCanvasRef}
          width={400}
          height={200}
          className="canvas"
        ></canvas>
        <canvas
          ref={cannyImageCanvasRef}
          width={400}
          height={200}
          className="canvas"
        ></canvas>
        <canvas
          ref={imageContoursCanvasRef}
          width={400}
          height={200}
          className="canvas"
        ></canvas>
        <canvas
          ref={markedImageCanvasRef}
          width={400}
          height={200}
          className="canvas"
        ></canvas>
      </div>
    </div>
  );
}

export default ConnectionSettings;
