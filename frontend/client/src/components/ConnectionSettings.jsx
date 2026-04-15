import { useState, useEffect, useRef } from "react";
import "../styles/ConnectionSettings.css";
import InformationPanel from "./InformationPanel";
import LogsContainer from "./LogsContainer";
import {  useLogsContext } from "../contexts/LogsContext";
function ConnectionSettings() {
  const [websocket, setWebsocket] = useState(null);
  const [connection, setConnection] = useState("connecting");
  ///------Logs-----///
  const {logs, addLog, results, addRes} = useLogsContext();
  
  ///------DisplayStatus and NumbersFromDisplay------///
  const [numbersFromDisplay, setNumbersFromDisplay] = useState(null);
  const [displayFoundStatus, setDisplayFoundStatus] = useState(null);
  //------Huge Canvas-------//
  const [currentClickedCanvas, setCurrentClickedCanvas] = useState(null);
  ///-------Canvas Refs------/////
  const pureImageCanvasRef = useRef(null);
  const cannyImageCanvasRef = useRef(null);
  const imageContoursCanvasRef = useRef(null);
  const markedImageCanvasRef = useRef(null);
  ///------Last Blobs Refs-----////
  const pureImageLastBlobRef = useRef(null);
  const cannyImageLastBlobRef = useRef(null);
  const imageContoursLastBlobRef = useRef(null);
  const markedImageLastBlobRef = useRef(null);
  const drawLastBlob = async (blob, currentCanvas)=>{
    if(!blob || !currentCanvas) return;
    console.log("Blob: ", blob);
    const bitmap = await createImageBitmap(blob);
    const canvas = currentCanvas;
    const ctx = canvas.getContext("2d");
    ctx.clearRect(0,0, canvas.width, canvas.height);
    ctx.drawImage(bitmap, 0,0,canvas.width, canvas.height);
    bitmap.close();
  }
  ///------------CanvasClick() handler------------//////////
  const canvasClick = (name)=>{
   setCurrentClickedCanvas((prev)=>prev === name ? null : name);
   console.log(
    currentClickedCanvas
   )
  }
  
  ///------------DisplayState ->console.log() --------//////
  useEffect(() => {
  console.log("displayFoundStatus changed:", displayFoundStatus);
  }, [displayFoundStatus]);
  ///---------------CanvasSize handler--------------/////
  useEffect(()=>{
    const reset_canvas = (canvas, blob)=>{
      if(!canvas)return;
      canvas.width = 400;
      canvas.height = 200;
      canvas.className = "canvas";

      drawLastBlob(blob, canvas);
    }
    reset_canvas(pureImageCanvasRef.current, pureImageLastBlobRef.current);
    reset_canvas(cannyImageCanvasRef.current, cannyImageLastBlobRef.current);
    reset_canvas(imageContoursCanvasRef.current, imageContoursLastBlobRef.current);
    reset_canvas(markedImageCanvasRef.current, markedImageLastBlobRef.current);

    const make_huge = (canvas, lastBlob)=>{
      if(!canvas) return;
      canvas.width = 1280;
      canvas.height = 720;
      canvas.className = "huge-canvas";

      drawLastBlob(lastBlob, canvas);
    }

    if(currentClickedCanvas === "pure") make_huge(pureImageCanvasRef.current, pureImageLastBlobRef.current);
    if(currentClickedCanvas === "canny") make_huge(cannyImageCanvasRef.current, cannyImageLastBlobRef.current);
    if(currentClickedCanvas === "contours") make_huge(imageContoursCanvasRef.current, imageContoursLastBlobRef.current);
    if(currentClickedCanvas === "marked") make_huge(markedImageCanvasRef.current, markedImageLastBlobRef.current);
  },[currentClickedCanvas])
  ////------Connection handlers-----------////
  const open_connection = () => {
    const socket = new WebSocket("ws://127.0.0.1:8000/ws");
    socket.binaryType = "arraybuffer";
    setWebsocket(socket);
  };
  const close_connection = () => {
    if (websocket && websocket.readyState === WebSocket.OPEN) {
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
  const stop_translation = ()=>{
    if(connection !== "Connected")alert("Connection is closed!");
      else{
        websocket.send("stop");
    }
  }

  
  ///----------Websocket handler------------/////
  useEffect(()=>{
    if(!websocket)return;
    websocket.onopen = ()=>{
      setConnection("Connected");
      addLog("Connected");
    }
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
          pureImageLastBlobRef.current = blob;
          drawLastBlob(blob, pureImageCanvasRef.current);
        }else if(frame_type == 2){
          cannyImageLastBlobRef.current = blob;
          drawLastBlob(blob, cannyImageCanvasRef.current);
        }else if(frame_type == 3){
          imageContoursLastBlobRef.current = blob;
          drawLastBlob(blob, imageContoursCanvasRef.current);
        }else if(frame_type == 4){
          markedImageLastBlobRef.current=blob;
          drawLastBlob(blob, markedImageCanvasRef.current);
        }
      }else{ 
        const parsed_data = JSON.parse(event.data);
        console.log(parsed_data);
        addLog(event.data);
        if(parsed_data.type == "displayStatus"){
          if (parsed_data.message == "false"){
          console.log("False");
          setDisplayFoundStatus(false);
          }else if(parsed_data.message == "true"){
          setDisplayFoundStatus(true);
          }
        }else if(parsed_data.type=="whole_digit"){
          setNumbersFromDisplay(parsed_data.message);
          addRes(parsed_data.message);
        }
      }
    };
    websocket.onclose = () => {
      setConnection("Disconnected");
      addLog("Disconnected");
  }
  }, [websocket])
 
///------EventHandler-------////
  useEffect(()=>{
    function keyhandler(event) {
      if(event.key === "t"){
        if(connection === "Connected"){
          console.log("Sended");
          websocket.send("image");
        }else{
          alert(connection);
        }
      }
    }
    document.addEventListener('keydown', keyhandler );

    return ()=>{
      document.removeEventListener('keydown', keyhandler)
    }
  }, [connection, websocket])
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
        <button onClick={stop_translation} className="translation-btn">Stop translation</button>
      </div>
      <div className="canvas-container">
        <canvas
          ref={pureImageCanvasRef}
          width={400}
          height={200}
          className="canvas"
          onClick={()=>canvasClick("pure")}
        ></canvas>
        <canvas
          ref={cannyImageCanvasRef}
          width={400}
          height={200}
          className="canvas"
          onClick={()=>canvasClick("canny")}
        ></canvas>
        <canvas
          ref={imageContoursCanvasRef}
          width={400}
          height={200}
          className="canvas"
          onClick={()=>canvasClick("contours")}
        ></canvas>
        <canvas
          ref={markedImageCanvasRef}
          width={400}
          height={200}
          className="canvas"
          onClick={()=>canvasClick("marked")}
        ></canvas>
      </div>
      <InformationPanel numbersFromDisplay = {numbersFromDisplay} displayStatus={displayFoundStatus}/>
      <LogsContainer />
    </div>
  );
}

export default ConnectionSettings;
