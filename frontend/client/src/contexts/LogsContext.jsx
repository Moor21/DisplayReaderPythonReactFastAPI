import { createContext,useContext,useState } from "react";

const LogsContext = createContext();
export const useLogsContext =()=> {
    const context = useContext(LogsContext);
    if(!context){
        throw new Error("useLogsContext should be used in LogsProvider");
    }
    return context;
}
export const LogsProvider = ({children})=>{
    const [logs, setLogs] = useState([]);
    const addLog = (message)=>{
    const time = new Date().toLocaleTimeString("ru-RU", {
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit",
    });
    setLogs((prev)=>[...prev, `${time}: ${message}`]);
    }

    const value = {logs, addLog};
    return(
        <LogsContext.Provider value={value}>
            {children}
        </LogsContext.Provider>
    )
}