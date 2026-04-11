import "./App.css";
import { useEffect, useState, useRef } from "react";
import { LogsProvider } from "./contexts/LogsContext";
import ConnectionSettings from "./components/ConnectionSettings";
function App() {
  return (
    <div className="App">
      <LogsProvider>
          <ConnectionSettings />
      </LogsProvider>
    </div>
  );
}

export default App;
