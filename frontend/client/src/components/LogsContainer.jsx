import { useEffect, useState,useRef } from "react";
import { useLogsContext } from "../contexts/LogsContext";
import "../styles/LogsContainer.css";

function LogsContainer() {
  const logsDiv = useRef(null);
  const resDiv = useRef(null);
  const {logs,results} = useLogsContext();
  const clear_logs = ()=>{
    logsDiv.current.innerHTML = " ";
  }
  const clear_results = ()=>{
    resDiv.current.innerHTML = " ";
  }
  return (
    <div className="logs-container">
      <div className="title-box">
        <span>Logs</span>
        <button onClick={clear_logs} style={{marginLeft:20+"px"}} className="btn">Clear</button>
      </div>
      <div ref={logsDiv} className="logs-body">
        {logs.map((log, index) => (
          <div  key={index}>{log}</div>
        ))}
      </div>
      <div className="title-box">
        <span>Results</span>
        <button onClick={clear_results} style={{marginLeft:20+"px"}} className="btn">Clear</button>
      </div>
      <div ref={resDiv} style={{overflowX: "hidden"}} className="logs-body">
        {results.map((res, index)=>(<div key={index}>{res}</div>))}
      </div>
    </div>
  );
}

export default LogsContainer;