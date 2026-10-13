"use client";

import React, { useEffect, useState } from "react";
import { 
  Clock, 
  Tag, 
  ShieldAlert, 
  GitPullRequest, 
  RotateCcw, 
  Users, 
  Terminal as TerminalIcon,
  Bot
} from "lucide-react";
import { OwnerCopilotDrawer } from "../../components/copilot-drawer";
import { TelemetryTerminal } from "../../components/telemetry-terminal";
import { ReviewGateModal } from "../../components/review-gate-modal";

interface TaskItem {
  id: string;
  title: string;
  project_tag: string;
  status: string;
  priority: string;
  assigned_agent_id?: string;
  lock_owner_id?: string;
  lock_expires_at?: string;
  lock_suspended: boolean;
  lock_suspended_remaining_seconds?: number;
  correlation_id?: string;
  dlq_reason?: string;
}

const COLUMNS = [
  { id: "BACKLOG", title: "Backlog", color: "border-zinc-700" },
  { id: "QUEUED", title: "Queued", color: "border-blue-700" },
  { id: "IN_PROGRESS", title: "In Progress (Locked)", color: "border-emerald-600" },
  { id: "PAUSED_FOR_CONSULTATION", title: "Paused (War Room)", color: "border-purple-600" },
  { id: "AWAITING_REVIEW", title: "Review Gate", color: "border-amber-600" },
  { id: "DEAD_LETTER_QUEUE", title: "Dead-Letter Queue (DLQ)", color: "border-red-600" },
  { id: "DONE", title: "Done", color: "border-zinc-600" },
];

export default function KanbanPage() {
  const [tasks, setTasks] = useState<TaskItem[]>([]);
  const [selectedTag, setSelectedTag] = useState<string>("ALL");
  const [isCopilotOpen, setIsCopilotOpen] = useState(false);
  const [selectedGate, setSelectedGate] = useState<{ id: string; taskId: string; diff: string } | null>(null);

  const fetchTasks = async () => {
    try {
      const res = await fetch("http://127.0.0.1:8000/api/v1/tasks");
      const data = await res.json();
      setTasks(data);
    } catch (err) {
      console.error("Failed to load tasks:", err);
    }
  };

  useEffect(() => {
    fetchTasks();
    const interval = setInterval(fetchTasks, 3000);
    return () => clearInterval(interval);
  }, []);

  const filteredTasks = selectedTag === "ALL" 
    ? tasks 
    : tasks.filter(t => t.project_tag === selectedTag);

  const allTags = Array.from(new Set(tasks.map(t => t.project_tag)));

  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-100 flex flex-col">
      <header className="border-b border-zinc-800 bg-zinc-900/60 backdrop-blur px-6 py-4 flex items-center justify-between">
        <div>
          <h1 className="text-lg font-bold tracking-tight text-white flex items-center gap-2">
            <span>Folks Orchestrator</span>
            <span className="text-xs bg-indigo-500/20 text-indigo-400 border border-indigo-500/30 px-2 py-0.5 rounded-full font-mono font-normal">
              v1.0 Kanban
            </span>
          </h1>
          <p className="text-xs text-zinc-400">Strict Lock State Machine & Local Host Daemon Telemetry</p>
        </div>

        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 text-xs bg-zinc-800/80 border border-zinc-700 px-3 py-1.5 rounded-lg">
            <Tag className="w-3.5 h-3.5 text-zinc-400" />
            <select
              value={selectedTag}
              onChange={(e) => setSelectedTag(e.target.value)}
              className="bg-transparent text-zinc-200 focus:outline-none"
            >
              <option value="ALL">All Project Tags</option>
              {allTags.map((tag) => (
                <option key={tag} value={tag} className="bg-zinc-900">{tag}</option>
              ))}
            </select>
          </div>

          <button
            onClick={() => setIsCopilotOpen(true)}
            className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-500 text-white px-3 py-1.5 rounded-lg text-xs font-semibold shadow-lg shadow-indigo-600/20"
          >
            <Bot className="w-4 h-4" />
            <span>Owner Copilot</span>
          </button>
        </div>
      </header>

      <main className="flex-1 p-6 overflow-x-auto flex gap-4 items-start">
        {COLUMNS.map((col) => {
          const colTasks = filteredTasks.filter((t) => t.status === col.id);
          return (
            <div
              key={col.id}
              className={`w-72 shrink-0 bg-zinc-900/40 border-t-2 ${col.color} border-x border-b border-zinc-800 rounded-xl p-3 flex flex-col max-h-[calc(100vh-280px)]`}
            >
              <div className="flex items-center justify-between mb-3 pb-2 border-b border-zinc-800">
                <span className="font-semibold text-xs text-zinc-300">{col.title}</span>
                <span className="text-[11px] font-mono bg-zinc-800 text-zinc-400 px-2 py-0.5 rounded-full">
                  {colTasks.length}
                </span>
              </div>

              <div className="flex-1 overflow-y-auto space-y-2.5">
                {colTasks.map((task) => (
                  <div
                    key={task.id}
                    className="bg-zinc-900 border border-zinc-800/80 rounded-lg p-3 space-y-2 shadow-sm hover:border-zinc-700 transition"
                  >
                    <div className="flex items-start justify-between gap-2">
                      <h4 className="text-xs font-medium text-white line-clamp-2">{task.title}</h4>
                      <span className={`text-[10px] uppercase font-bold px-1.5 py-0.5 rounded ${
                        task.priority === "HIGH" ? "bg-red-950 text-red-400 border border-red-800/40" : "bg-zinc-800 text-zinc-400"
                      }`}>
                        {task.priority}
                      </span>
                    </div>

                    <div className="flex flex-wrap items-center gap-1.5 text-[11px]">
                      <span className="inline-flex items-center gap-1 text-zinc-400 bg-zinc-800 px-1.5 py-0.5 rounded">
                        <Tag className="w-3 h-3 text-indigo-400" />
                        {task.project_tag}
                      </span>

                      {task.lock_owner_id && (
                        <span className="inline-flex items-center gap-1 text-emerald-400 bg-emerald-950/40 px-1.5 py-0.5 rounded border border-emerald-800/30">
                          <Clock className="w-3 h-3" />
                          60s TTL
                        </span>
                      )}

                      {task.lock_suspended && (
                        <span className="inline-flex items-center gap-1 text-purple-300 bg-purple-950/50 px-1.5 py-0.5 rounded border border-purple-700/40">
                          TTL Frozen ({task.lock_suspended_remaining_seconds}s)
                        </span>
                      )}
                    </div>

                    {task.status === "DEAD_LETTER_QUEUE" && (
                      <div className="bg-red-950/40 border border-red-800/50 rounded p-2 text-[11px] text-red-300 space-y-1">
                        <div className="flex items-center gap-1 font-semibold text-red-400">
                          <ShieldAlert className="w-3.5 h-3.5" />
                          <span>Daemon Timeout / Reaped</span>
                        </div>
                        <p className="line-clamp-2 text-zinc-400">{task.dlq_reason}</p>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          );
        })}
      </main>

      <footer className="p-4 bg-zinc-950 border-t border-zinc-800">
        <TelemetryTerminal />
      </footer>

      <OwnerCopilotDrawer isOpen={isCopilotOpen} onClose={() => setIsCopilotOpen(false)} />
    </div>
  );
}
