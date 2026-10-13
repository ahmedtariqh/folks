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
  Bot,
  Settings,
  Sparkles,
  Building
} from "lucide-react";
import { OwnerCopilotDrawer } from "../../components/copilot-drawer";
import { TelemetryTerminal } from "../../components/telemetry-terminal";
import { ReviewGateModal } from "../../components/review-gate-modal";
import { OnboardingWizard } from "../../components/onboarding-wizard";

interface TaskItem {
  id: string;
  title: string;
  description?: string;
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

interface OnboardingStatus {
  onboarding_completed: boolean;
  company_name?: string;
  company_mission?: string;
  project_tag?: string;
  lead_agent_name?: string;
  llm_provider?: {
    provider_name?: string;
    default_model?: string;
  };
}

const COLUMNS = [
  { id: "BACKLOG", title: "Backlog", color: "border-slate-300 bg-slate-100/60" },
  { id: "QUEUED", title: "Queued", color: "border-slate-400 bg-slate-100/60" },
  { id: "IN_PROGRESS", title: "In Progress (Locked)", color: "border-blue-500 bg-blue-50/30" },
  { id: "PAUSED_FOR_CONSULTATION", title: "Paused (War Room)", color: "border-amber-500 bg-amber-50/30" },
  { id: "AWAITING_REVIEW", title: "Review Gate", color: "border-purple-500 bg-purple-50/30" },
  { id: "DEAD_LETTER_QUEUE", title: "Dead-Letter Queue (DLQ)", color: "border-red-500 bg-red-50/30" },
  { id: "DONE", title: "Done", color: "border-emerald-500 bg-emerald-50/30" },
];

export default function KanbanPage() {
  const [tasks, setTasks] = useState<TaskItem[]>([]);
  const [selectedTag, setSelectedTag] = useState<string>("ALL");
  const [isCopilotOpen, setIsCopilotOpen] = useState(false);
  const [selectedGate, setSelectedGate] = useState<{ id: string; taskId: string; diff: string } | null>(null);

  const [onboardingStatus, setOnboardingStatus] = useState<OnboardingStatus | null>(null);
  const [showWizard, setShowWizard] = useState(false);

  const checkStatus = async () => {
    try {
      const res = await fetch("http://127.0.0.1:8000/api/v1/onboarding/status");
      if (res.ok) {
        const data = await res.json();
        setOnboardingStatus(data);
        if (!data.onboarding_completed) {
          setShowWizard(true);
        }
      }
    } catch (err) {
      console.error("Failed to fetch onboarding status:", err);
    }
  };

  const fetchTasks = async () => {
    try {
      const res = await fetch("http://127.0.0.1:8000/api/v1/tasks");
      if (res.ok) {
        const data = await res.json();
        setTasks(data);
      }
    } catch (err) {
      console.error("Failed to load tasks:", err);
    }
  };

  useEffect(() => {
    checkStatus();
    fetchTasks();
    const interval = setInterval(fetchTasks, 3000);
    return () => clearInterval(interval);
  }, []);

  const filteredTasks = selectedTag === "ALL" 
    ? tasks 
    : tasks.filter(t => t.project_tag === selectedTag);

  const allTags = Array.from(new Set(tasks.map(t => t.project_tag)));

  if (showWizard) {
    return (
      <div className="min-h-screen bg-[#f8fafc] text-slate-800 p-6 flex flex-col justify-center">
        <OnboardingWizard
          onCompleted={() => {
            setShowWizard(false);
            checkStatus();
            fetchTasks();
          }}
        />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#f8fafc] text-slate-800 flex flex-col font-sans">
      
      {/* Top Header */}
      <header className="border-b border-slate-200 bg-white/95 backdrop-blur px-6 py-3.5 flex items-center justify-between shadow-xs">
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 rounded-lg bg-emerald-600 flex items-center justify-center font-bold text-white shadow-xs">
            F
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-base font-bold text-slate-900">
                {onboardingStatus?.company_name || "Folks Orchestrator"}
              </h1>
              <span className="text-[10px] bg-emerald-50 text-emerald-700 border border-emerald-200 px-2 py-0.5 rounded-full font-mono font-medium">
                {onboardingStatus?.project_tag || "v1.0"}
              </span>
              {onboardingStatus?.llm_provider && (
                <span className="text-[10px] bg-indigo-50 text-indigo-700 border border-indigo-200 px-2 py-0.5 rounded font-mono">
                  ⚡ {onboardingStatus.llm_provider.default_model}
                </span>
              )}
            </div>
            <p className="text-[11px] text-slate-500 max-w-xl truncate">
              {onboardingStatus?.company_mission || "Paperclip-style Resilient Agent Architecture & Host Daemon"}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2.5">
          <div className="flex items-center gap-2 text-xs bg-slate-50 border border-slate-200 px-3 py-1.5 rounded-lg text-slate-600">
            <Tag className="w-3.5 h-3.5 text-slate-400" />
            <select
              value={selectedTag}
              onChange={(e) => setSelectedTag(e.target.value)}
              className="bg-transparent text-slate-800 focus:outline-none text-xs"
            >
              <option value="ALL">All Project Tags</option>
              {allTags.map((tag) => (
                <option key={tag} value={tag} className="bg-white">{tag}</option>
              ))}
            </select>
          </div>

          <button
            onClick={() => setShowWizard(true)}
            className="flex items-center gap-1.5 bg-white hover:bg-slate-50 text-slate-700 border border-slate-200 px-3 py-1.5 rounded-lg text-xs font-semibold shadow-xs transition"
          >
            <Settings className="w-3.5 h-3.5" />
            <span>Setup Wizard</span>
          </button>

          <button
            onClick={() => setIsCopilotOpen(true)}
            className="flex items-center gap-1.5 bg-emerald-600 hover:bg-emerald-700 text-white px-3.5 py-1.5 rounded-lg text-xs font-semibold shadow-xs transition"
          >
            <Bot className="w-4 h-4" />
            <span>Owner Copilot</span>
          </button>
        </div>
      </header>

      {/* Main Kanban Content */}
      <main className="flex-1 p-6 overflow-x-auto flex gap-4 items-start">
        {COLUMNS.map((col) => {
          const colTasks = filteredTasks.filter((t) => t.status === col.id);
          return (
            <div
              key={col.id}
              className={`w-72 shrink-0 ${col.color} border border-slate-200 rounded-xl p-3 flex flex-col max-h-[calc(100vh-260px)] shadow-xs`}
            >
              <div className="flex items-center justify-between mb-3 pb-2 border-b border-slate-200">
                <span className="font-bold text-xs text-slate-800">{col.title}</span>
                <span className="text-[11px] font-mono font-bold bg-white text-slate-700 border border-slate-200 px-2 py-0.5 rounded-full shadow-2xs">
                  {colTasks.length}
                </span>
              </div>

              <div className="flex-1 overflow-y-auto space-y-2.5">
                {colTasks.length === 0 ? (
                  <div className="p-4 text-center text-slate-400 text-[11px] italic">No tasks</div>
                ) : (
                  colTasks.map((task) => (
                    <div
                      key={task.id}
                      className="bg-white border border-slate-200 rounded-lg p-3 space-y-2 shadow-xs hover:border-slate-300 transition"
                    >
                      <div className="flex items-start justify-between gap-2">
                        <h4 className="text-xs font-bold text-slate-900 leading-snug">{task.title}</h4>
                        <span className={`text-[10px] uppercase font-bold px-1.5 py-0.5 rounded ${
                          task.priority === "HIGH" || task.priority === "URGENT" || task.priority === "CRITICAL"
                            ? "bg-red-50 text-red-700 border border-red-200"
                            : "bg-slate-100 text-slate-700"
                        }`}>
                          {task.priority}
                        </span>
                      </div>

                      {task.description && (
                        <p className="text-[11px] text-slate-500 line-clamp-2 leading-relaxed">
                          {task.description}
                        </p>
                      )}

                      <div className="flex flex-wrap items-center gap-1.5 text-[10px] pt-1 border-t border-slate-100">
                        <span className="inline-flex items-center gap-1 text-slate-500 bg-slate-50 px-1.5 py-0.5 rounded border border-slate-200">
                          <Tag className="w-3 h-3 text-indigo-500" />
                          {task.project_tag}
                        </span>

                        {task.lock_owner_id && (
                          <span className="inline-flex items-center gap-1 text-blue-700 bg-blue-50 px-1.5 py-0.5 rounded border border-blue-200 font-medium">
                            <Clock className="w-3 h-3" />
                            60s TTL
                          </span>
                        )}

                        {task.lock_suspended && (
                          <span className="inline-flex items-center gap-1 text-amber-700 bg-amber-50 px-1.5 py-0.5 rounded border border-amber-200 font-medium">
                            TTL Frozen ({task.lock_suspended_remaining_seconds || 45}s)
                          </span>
                        )}
                      </div>

                      {task.status === "DEAD_LETTER_QUEUE" && (
                        <div className="bg-red-50 border border-red-200 rounded p-2 text-[10px] text-red-800 space-y-1">
                          <div className="flex items-center gap-1 font-bold text-red-700">
                            <ShieldAlert className="w-3.5 h-3.5" />
                            <span>Swept to DLQ</span>
                          </div>
                          <p className="line-clamp-2 text-red-600">{task.dlq_reason}</p>
                        </div>
                      )}
                    </div>
                  ))
                )}
              </div>
            </div>
          );
        })}
      </main>

      <footer className="p-4 bg-white border-t border-slate-200">
        <TelemetryTerminal />
      </footer>

      <OwnerCopilotDrawer isOpen={isCopilotOpen} onClose={() => setIsCopilotOpen(false)} />
    </div>
  );
}
