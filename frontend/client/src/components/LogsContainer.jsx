import { useEffect, useState } from "react";
import { useLogsContext } from "../contexts/LogsContext";
import "../styles/LogsContainer.css";

function LogsContainer() {
  const {logs} = useLogsContext();
  return (
    <div className="logs-container">
      <div className="title-box">
        <span>Logs</span>
      </div>
      <div className="logs-body">
        {logs.map((log, index) => (
          <div key={index}>{log}</div>
        ))}
      </div>
    </div>
  );
}

export default LogsContainer;