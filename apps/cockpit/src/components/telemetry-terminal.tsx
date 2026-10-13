"use client";

import React, { useEffect, useState, useRef } from "react";
import { Terminal, Shield, Pause, Play, Trash2 } from "lucide-react";

interface LogLine {
  id: string;
  timestamp: string;
  stream: "stdout" | "stderr";
  task_id?: string;
  correlation_id?: string;
  text: string;
}

export function TelemetryTerminal({ activeTaskId }: { activeTaskId?: string }) {
  const [logs, setLogs] = useState<LogLine[]>([]);
  const [isPaused, setIsPaused] = useState(false);
  const [connected, setConnected] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const ws = new WebSocket("ws://127.0.0.1:8000/ws/cockpit");

    ws.onopen = () => {
      setConnected(true);
    };

    ws.onclose = () => {
      setConnected(false);
    };

    ws.onmessage = (event) => {
      if (isPaused) return;
      try {
        const msg = JSON.parse(event.data);
        if (msg.type === "terminal_chunk") {
          if (activeTaskId && msg.task_id !== activeTaskId) return;

          setLogs((prev) => [
            ...prev.slice(-400),
            {
              id: Math.random().toString(),
              timestamp: new Date().toLocaleTimeString(),
              stream: msg.stream,
              task_id: msg.task_id,
              correlation_id: msg.correlation_id,
              text: msg.text,
            },
          ]);
        }
      } catch (err) {
        console.error("WS Parse Error:", err);
      }
    };

    return () => {
      ws.close();
    };
  }, [activeTaskId, isPaused]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [logs]);

  return (
    <div className="bg-zinc-950 border border-zinc-800 rounded-lg overflow-hidden flex flex-col font-mono text-xs">
      <div className="bg-zinc-900 border-b border-zinc-800 px-3 py-2 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Terminal className="w-4 h-4 text-emerald-400" />
          <span className="font-semibold text-zinc-300">Live Daemon Execution Telemetry</span>
          <span
            className={`w-2 h-2 rounded-full ${
              connected ? "bg-emerald-500 animate-pulse" : "bg-red-500"
            }`}
          />
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => setIsPaused(!isPaused)}
            className="text-zinc-400 hover:text-white p-1"
            title={isPaused ? "Resume Stream" : "Pause Stream"}
          >
            {isPaused ? <Play className="w-3.5 h-3.5" /> : <Pause className="w-3.5 h-3.5" />}
          </button>
          <button
            onClick={() => setLogs([])}
            className="text-zinc-400 hover:text-white p-1"
            title="Clear Terminal"
          >
            <Trash2 className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      <div className="h-64 overflow-y-auto p-3 space-y-1 bg-black/90">
        {logs.length === 0 ? (
          <div className="text-zinc-600 italic">Waiting for daemon execution output...</div>
        ) : (
          logs.map((log) => (
            <div key={log.id} className="flex items-start gap-2 leading-relaxed">
              <span className="text-zinc-600 select-none">{log.timestamp}</span>
              {log.correlation_id && (
                <span className="text-[10px] text-zinc-500 bg-zinc-900 px-1 rounded select-none">
                  [{log.correlation_id.slice(-6)}]
                </span>
              )}
              <span
                className={
                  log.stream === "stderr"
                    ? "text-red-400 font-semibold"
                    : "text-zinc-300"
                }
              >
                {log.text}
              </span>
            </div>
          ))
        )}
        <div ref={bottomRef} />
      </div>
    </div>
  );
}
