import "./App.css";
import { useEffect, useState, useRef } from "react";
import ConnectionSettings from "./components/ConnectionSettings";
function App() {
  return (
    <div className="App">
      <ConnectionSettings />
    </div>
  );
}

export default App;
