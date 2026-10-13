"use client";

import React, { useState } from "react";
import { 
  Bot, 
  Compass, 
  AlertTriangle, 
  Send, 
  CheckCircle2, 
  ExternalLink,
  ShieldCheck,
  RotateCcw,
  Sliders
} from "lucide-react";

interface UINavResult {
  screen_name: string;
  route_path: string;
  breadcrumbs: string[];
  description: string;
  action_available?: string;
}

interface TraceExplanation {
  correlation_id: string;
  task_id?: string;
  agent_id?: string;
  daemon_id?: string;
  total_events: number;
  has_errors: boolean;
  root_cause_summary: string;
  suggested_remedy: string;
  timeline: Array<{
    timestamp: string;
    event_type: string;
    level: string;
    message: string;
  }>;
}

export function OwnerCopilotDrawer({ isOpen, onClose }: { isOpen: boolean; onClose: () => void }) {
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [navResults, setNavResults] = useState<UINavResult[]>([]);
  const [traceResult, setTraceResult] = useState<TraceExplanation | null>(null);
  const [actionStatus, setActionStatus] = useState<string | null>(null);

  const [budgetAgentId, setBudgetAgentId] = useState("");
  const [newBudget, setNewBudget] = useState(100);

  if (!isOpen) return null;

  const handleAskCopilot = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;
    setLoading(true);
    setActionStatus(null);

    if (query.toLowerCase().includes("trace") || query.startsWith("corr-")) {
      const match = query.match(/corr-[a-zA-Z0-9_-]+/);
      const corrId = match ? match[0] : query.trim();
      try {
        const res = await fetch("http://127.0.0.1:8000/api/v1/owner/copilot/explain-trace", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ correlation_id: corrId }),
        });
        const data = await res.json();
        setTraceResult(data);
        setNavResults([]);
      } catch (err) {
        console.error(err);
      }
    } else {
      try {
        const res = await fetch("http://127.0.0.1:8000/api/v1/owner/copilot/navigate", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ query }),
        });
        const data = await res.json();
        setNavResults(data);
        setTraceResult(null);
      } catch (err) {
        console.error(err);
      }
    }
    setLoading(false);
  };

  const handleExecuteBudgetUpdate = async () => {
    if (!budgetAgentId) return;
    setLoading(true);
    try {
      const res = await fetch("http://127.0.0.1:8000/api/v1/owner/copilot/action/budget", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          agent_id: budgetAgentId,
          monthly_budget_usd: Number(newBudget),
        }),
      });
      const data = await res.json();
      if (data.success) {
        setActionStatus(`Budget updated successfully to $${newBudget}/mo!`);
      } else {
        setActionStatus(`Failed: ${data.message}`);
      }
    } catch (err: any) {
      setActionStatus(`Error: ${err.message}`);
    }
    setLoading(false);
  };

  return (
    <div className="fixed inset-y-0 right-0 w-96 bg-zinc-900 border-l border-zinc-800 text-zinc-100 shadow-2xl z-50 flex flex-col">
      <div className="p-4 border-b border-zinc-800 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Bot className="w-5 h-5 text-indigo-400" />
          <h2 className="font-semibold text-sm tracking-wide">Owner Copilot (BI & Navigator)</h2>
        </div>
        <button onClick={onClose} className="text-zinc-400 hover:text-white text-xs">
          ✕ Close
        </button>
      </div>

      <div className="bg-indigo-950/40 border-b border-indigo-800/30 px-4 py-2 flex items-center gap-2 text-xs text-indigo-300">
        <ShieldCheck className="w-4 h-4 shrink-0 text-indigo-400" />
        <span>Strict Pydantic API boundary & Zero direct SQL access</span>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {navResults.length > 0 && (
          <div className="space-y-3">
            <p className="text-xs text-zinc-400 font-medium">UI NAVIGATION RECOMMENDATIONS</p>
            {navResults.map((item, idx) => (
              <div key={idx} className="bg-zinc-800/80 border border-zinc-700/60 rounded-lg p-3 space-y-2">
                <div className="flex items-center gap-1.5 text-xs text-indigo-400">
                  <Compass className="w-3.5 h-3.5" />
                  <span>{item.breadcrumbs.join(" > ")}</span>
                </div>
                <h4 className="font-medium text-sm text-white">{item.screen_name}</h4>
                <p className="text-xs text-zinc-300">{item.description}</p>
                <div className="pt-1 flex items-center justify-between">
                  <span className="text-[10px] font-mono text-zinc-400">{item.route_path}</span>
                  <a
                    href={item.route_path}
                    className="inline-flex items-center gap-1 text-xs text-indigo-400 hover:underline"
                  >
                    Go to screen <ExternalLink className="w-3 h-3" />
                  </a>
                </div>
              </div>
            ))}
          </div>
        )}

        {traceResult && (
          <div className="bg-zinc-800/90 border border-zinc-700 rounded-lg p-3 space-y-3">
            <div className="flex items-center gap-2 text-amber-400 text-xs font-semibold">
              <AlertTriangle className="w-4 h-4" />
              <span>DIAGNOSTIC TRACE REPORT</span>
            </div>
            <div className="text-xs space-y-1">
              <p><span className="text-zinc-400">Correlation ID:</span> <span className="font-mono text-zinc-200">{traceResult.correlation_id}</span></p>
              <p><span className="text-zinc-400">Events Recorded:</span> {traceResult.total_events}</p>
            </div>
            <div className="bg-red-950/40 border border-red-800/40 rounded p-2 text-xs text-red-200">
              <span className="font-semibold">Root Cause:</span> {traceResult.root_cause_summary}
            </div>
            <div className="bg-emerald-950/40 border border-emerald-800/40 rounded p-2 text-xs text-emerald-200">
              <span className="font-semibold">Remedy:</span> {traceResult.suggested_remedy}
            </div>
          </div>
        )}

        <div className="bg-zinc-800/50 border border-zinc-700/50 rounded-lg p-3 space-y-2">
          <div className="flex items-center gap-2 text-xs font-semibold text-zinc-300">
            <Sliders className="w-3.5 h-3.5 text-indigo-400" />
            <span>Typed Action: Update Agent Budget</span>
          </div>
          <input
            type="text"
            placeholder="Agent UUID..."
            value={budgetAgentId}
            onChange={(e) => setBudgetAgentId(e.target.value)}
            className="w-full bg-zinc-900 border border-zinc-700 rounded px-2 py-1 text-xs"
          />
          <div className="flex items-center gap-2">
            <input
              type="number"
              value={newBudget}
              onChange={(e) => setNewBudget(Number(e.target.value))}
              className="w-24 bg-zinc-900 border border-zinc-700 rounded px-2 py-1 text-xs"
            />
            <button
              onClick={handleExecuteBudgetUpdate}
              disabled={loading || !budgetAgentId}
              className="flex-1 bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white rounded px-2 py-1 text-xs font-medium"
            >
              Apply Budget
            </button>
          </div>
          {actionStatus && (
            <p className="text-[11px] text-emerald-400 mt-1 flex items-center gap-1">
              <CheckCircle2 className="w-3 h-3" /> {actionStatus}
            </p>
          )}
        </div>
      </div>

      <form onSubmit={handleAskCopilot} className="p-3 border-t border-zinc-800 bg-zinc-900 flex gap-2">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Ask where a setting is or paste a corr-id..."
          className="flex-1 bg-zinc-800 border border-zinc-700 rounded px-3 py-1.5 text-xs text-white placeholder-zinc-500 focus:outline-none focus:border-indigo-500"
        />
        <button
          type="submit"
          disabled={loading}
          className="bg-indigo-600 hover:bg-indigo-500 text-white rounded px-3 py-1.5 text-xs font-medium flex items-center gap-1"
        >
          <Send className="w-3 h-3" />
        </button>
      </form>
    </div>
  );
}
