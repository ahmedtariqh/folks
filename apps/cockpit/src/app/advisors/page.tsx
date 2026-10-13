"use client";

import React, { useEffect, useState } from "react";
import { 
  GraduationCap, 
  BrainCircuit, 
  BookOpen, 
  ShieldAlert, 
  CheckCircle, 
  HelpCircle, 
  MessageSquare,
  Sparkles,
  ChevronRight,
  FileText
} from "lucide-react";

interface KnowledgeBaseItem {
  id: string;
  name: string;
  description: string;
  domain_tag: string;
  documents: Array<{ title: string; content: string }>;
}

interface AdvisorItem {
  id: string;
  name: string;
  domain: string;
  reasoning_model: string;
  system_prompt: string;
  status: string;
  linked_knowledge_base_ids: string[];
}

interface AdvisorySessionItem {
  id: string;
  task_id?: string;
  requesting_agent_id: string;
  advisor_id: string;
  request_type: string;
  query_text: string;
  knowledge_references: Array<{ kb_name: string; title: string; excerpt: string }>;
  reasoning_trace?: string;
  verdict: string;
  advice_summary?: string;
  correlation_id: string;
  status: string;
  created_at: string;
}

export default function AdvisorsPage() {
  const [advisors, setAdvisors] = useState<AdvisorItem[]>([]);
  const [knowledgeBases, setKnowledgeBases] = useState<KnowledgeBaseItem[]>([]);
  const [sessions, setSessions] = useState<AdvisorySessionItem[]>([]);
  const [selectedSession, setSelectedSession] = useState<AdvisorySessionItem | null>(null);

  // Consultation Form State
  const [selectedAdvisorId, setSelectedAdvisorId] = useState("");
  const [consultQuery, setConsultQuery] = useState("");
  const [requestType, setRequestType] = useState("ARCHITECTURE_ADVICE");
  const [loading, setLoading] = useState(false);

  const fetchData = async () => {
    try {
      const [resAdv, resKb, resSess] = await Promise.all([
        fetch("http://127.0.0.1:8000/api/v1/advisors"),
        fetch("http://127.0.0.1:8000/api/v1/advisors/knowledge-bases"),
        fetch("http://127.0.0.1:8000/api/v1/advisors/sessions"),
      ]);
      setAdvisors(await resAdv.json());
      setKnowledgeBases(await resKb.json());
      setSessions(await resSess.json());
    } catch (err) {
      console.error("Failed to load advisory data:", err);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleConsult = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedAdvisorId || !consultQuery.trim()) return;
    setLoading(true);
    try {
      const res = await fetch("http://127.0.0.1:8000/api/v1/advisors/consult", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          requesting_agent_id: "agent-lead-default",
          advisor_id: selectedAdvisorId,
          query_text: consultQuery,
          request_type: requestType,
          correlation_id: `corr-adv-${Date.now()}`
        }),
      });
      if (res.ok) {
        const newSession = await res.json();
        setSessions([newSession, ...sessions]);
        setSelectedSession(newSession);
        setConsultQuery("");
      }
    } catch (err) {
      console.error(err);
    }
    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-100 flex flex-col font-sans">
      {/* Top Navbar */}
      <header className="border-b border-zinc-800 bg-zinc-900/60 backdrop-blur px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-indigo-500/10 border border-indigo-500/30 rounded-xl text-indigo-400">
            <GraduationCap className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-lg font-bold tracking-tight text-white flex items-center gap-2">
              <span>Board of Advisors</span>
              <span className="text-xs bg-purple-500/20 text-purple-400 border border-purple-500/30 px-2 py-0.5 rounded-full font-mono font-normal">
                Intense Reasoning & Heavy-Weight KBs
              </span>
            </h1>
            <p className="text-xs text-zinc-400">Elite domain advisors providing architectural sign-offs, security audits, and strategic reviews</p>
          </div>
        </div>

        <a href="/kanban" className="text-xs text-zinc-400 hover:text-white flex items-center gap-1">
          Back to Kanban <ChevronRight className="w-3.5 h-3.5" />
        </a>
      </header>

      {/* Main Grid */}
      <main className="flex-1 p-6 grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: Board Roster & KBs */}
        <div className="space-y-6">
          {/* Advisors List */}
          <div className="bg-zinc-900/40 border border-zinc-800 rounded-xl p-4 space-y-3">
            <h2 className="text-sm font-semibold text-zinc-200 flex items-center gap-2">
              <BrainCircuit className="w-4 h-4 text-purple-400" />
              <span>Appointed Board Advisors ({advisors.length})</span>
            </h2>
            <div className="space-y-2.5">
              {advisors.map((adv) => (
                <div key={adv.id} className="bg-zinc-900 border border-zinc-800 rounded-lg p-3 space-y-1.5">
                  <div className="flex items-center justify-between">
                    <h3 className="font-semibold text-xs text-white">{adv.name}</h3>
                    <span className="text-[10px] font-mono bg-purple-950 text-purple-300 border border-purple-800/40 px-1.5 py-0.5 rounded">
                      {adv.reasoning_model}
                    </span>
                  </div>
                  <p className="text-[11px] text-zinc-400">{adv.domain}</p>
                  <p className="text-xs text-zinc-300 italic line-clamp-2">"{adv.system_prompt}"</p>
                </div>
              ))}
            </div>
          </div>

          {/* Heavy-weight Knowledge Bases */}
          <div className="bg-zinc-900/40 border border-zinc-800 rounded-xl p-4 space-y-3">
            <h2 className="text-sm font-semibold text-zinc-200 flex items-center gap-2">
              <BookOpen className="w-4 h-4 text-indigo-400" />
              <span>Heavy-Weight Knowledge Bases ({knowledgeBases.length})</span>
            </h2>
            <div className="space-y-2">
              {knowledgeBases.map((kb) => (
                <div key={kb.id} className="bg-zinc-900 border border-zinc-800 rounded-lg p-3 space-y-1">
                  <h4 className="text-xs font-semibold text-white">{kb.name}</h4>
                  <p className="text-[11px] text-zinc-400">{kb.description}</p>
                  <div className="pt-1 flex items-center gap-2 text-[10px] text-zinc-500 font-mono">
                    <span>tag: {kb.domain_tag}</span>
                    <span>•</span>
                    <span>{kb.documents.length} verified documents</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Center Column: Consultation Request Console */}
        <div className="space-y-4">
          <div className="bg-zinc-900/60 border border-zinc-800 rounded-xl p-4 space-y-4">
            <div className="flex items-center gap-2 text-sm font-semibold text-zinc-200">
              <Sparkles className="w-4 h-4 text-amber-400" />
              <span>Request Advisory Consultation / Review</span>
            </div>

            <form onSubmit={handleConsult} className="space-y-3 text-xs">
              <div>
                <label className="block text-zinc-400 mb-1 font-medium">Select Advisor</label>
                <select
                  value={selectedAdvisorId}
                  onChange={(e) => setSelectedAdvisorId(e.target.value)}
                  className="w-full bg-zinc-800 border border-zinc-700 rounded-lg p-2 text-zinc-100 focus:outline-none focus:border-indigo-500"
                >
                  <option value="">-- Choose Advisor --</option>
                  {advisors.map((a) => (
                    <option key={a.id} value={a.id}>{a.name} ({a.domain})</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-zinc-400 mb-1 font-medium">Consultation Type</label>
                <select
                  value={requestType}
                  onChange={(e) => setRequestType(e.target.value)}
                  className="w-full bg-zinc-800 border border-zinc-700 rounded-lg p-2 text-zinc-100 focus:outline-none focus:border-indigo-500"
                >
                  <option value="ARCHITECTURE_ADVICE">Architecture & System Design Advice</option>
                  <option value="SECURITY_REVIEW">Security Compliance & Vulnerability Audit</option>
                  <option value="STRATEGIC_DIRECTION">Strategic Direction & Performance Trade-offs</option>
                  <option value="PRE_GATE_AUDIT">Pre-Review Gate Diff Audit</option>
                </select>
              </div>

              <div>
                <label className="block text-zinc-400 mb-1 font-medium">Proposal, Code Diff, or Query</label>
                <textarea
                  value={consultQuery}
                  onChange={(e) => setConsultQuery(e.target.value)}
                  placeholder="Describe architectural dilemma, proposed concurrency model, or security boundaries..."
                  rows={5}
                  className="w-full bg-zinc-800 border border-zinc-700 rounded-lg p-2.5 text-zinc-100 placeholder-zinc-500 focus:outline-none focus:border-indigo-500 leading-relaxed font-mono"
                />
              </div>

              <button
                type="submit"
                disabled={loading || !selectedAdvisorId || !consultQuery.trim()}
                className="w-full bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white font-semibold py-2 rounded-lg transition shadow-lg shadow-indigo-600/20"
              >
                {loading ? "Advisor Reasoning in Progress (Lock Suspended)..." : "Submit for Intense Reasoning"}
              </button>
            </form>
          </div>

          {/* Past Consultation History Feed */}
          <div className="bg-zinc-900/40 border border-zinc-800 rounded-xl p-4 space-y-3">
            <h3 className="text-xs font-semibold text-zinc-300 flex items-center gap-1.5">
              <MessageSquare className="w-3.5 h-3.5 text-zinc-400" />
              <span>Advisory Reviews ({sessions.length})</span>
            </h3>

            <div className="space-y-2 max-h-80 overflow-y-auto">
              {sessions.map((sess) => (
                <div
                  key={sess.id}
                  onClick={() => setSelectedSession(sess)}
                  className={`p-2.5 rounded-lg border cursor-pointer transition text-xs space-y-1 ${
                    selectedSession?.id === sess.id 
                      ? "bg-zinc-800 border-indigo-500" 
                      : "bg-zinc-900 border-zinc-800 hover:border-zinc-700"
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span className="font-semibold text-white truncate max-w-[180px]">{sess.request_type}</span>
                    <span className={`text-[10px] uppercase font-bold px-1.5 py-0.5 rounded ${
                      sess.verdict === "APPROVED" 
                        ? "bg-emerald-950 text-emerald-400 border border-emerald-800/40"
                        : sess.verdict === "RISK_FLAGGED"
                        ? "bg-red-950 text-red-400 border border-red-800/40"
                        : "bg-indigo-950 text-indigo-300 border border-indigo-800/40"
                    }`}>
                      {sess.verdict}
                    </span>
                  </div>
                  <p className="text-zinc-400 line-clamp-1">{sess.query_text}</p>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right Column: Reasoning Trace & Knowledge Citations */}
        <div className="space-y-4">
          {selectedSession ? (
            <div className="bg-zinc-900/60 border border-zinc-800 rounded-xl p-4 space-y-4 text-xs">
              <div className="flex items-center justify-between pb-2 border-b border-zinc-800">
                <span className="font-semibold text-sm text-white">Advisory Verdict & Trace</span>
                <span className="font-mono text-zinc-500">[{selectedSession.correlation_id.slice(-8)}]</span>
              </div>

              {/* Verdict Banner */}
              <div className={`p-3 rounded-lg border ${
                selectedSession.verdict === "APPROVED"
                  ? "bg-emerald-950/40 border-emerald-800/50 text-emerald-200"
                  : selectedSession.verdict === "RISK_FLAGGED"
                  ? "bg-red-950/40 border-red-800/50 text-red-200"
                  : "bg-indigo-950/40 border-indigo-800/50 text-indigo-200"
              }`}>
                <div className="font-bold text-xs uppercase mb-1">Verdict: {selectedSession.verdict}</div>
                <p className="leading-relaxed">{selectedSession.advice_summary}</p>
              </div>

              {/* Knowledge Base Citations */}
              <div className="space-y-2">
                <h4 className="font-semibold text-zinc-300 flex items-center gap-1.5">
                  <FileText className="w-3.5 h-3.5 text-indigo-400" />
                  <span>Knowledge Base Evidence Citations ({selectedSession.knowledge_references.length})</span>
                </h4>
                <div className="space-y-2">
                  {selectedSession.knowledge_references.map((ref, idx) => (
                    <div key={idx} className="bg-zinc-950 p-2.5 rounded-lg border border-zinc-800 font-mono space-y-1">
                      <div className="text-indigo-400 font-semibold">{ref.title}</div>
                      <div className="text-[11px] text-zinc-400 leading-relaxed">{ref.excerpt}</div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Deep Reasoning Steps Trace */}
              <div className="space-y-2">
                <h4 className="font-semibold text-zinc-300 flex items-center gap-1.5">
                  <BrainCircuit className="w-3.5 h-3.5 text-purple-400" />
                  <span>Extended Reasoning Trace (Thinking Steps)</span>
                </h4>
                <pre className="bg-black/80 p-3 rounded-lg font-mono text-[11px] text-zinc-300 whitespace-pre-wrap leading-relaxed border border-zinc-800">
                  {selectedSession.reasoning_trace || "No raw trace available."}
                </pre>
              </div>
            </div>
          ) : (
            <div className="h-full bg-zinc-900/30 border border-zinc-800/50 rounded-xl p-8 flex flex-col items-center justify-center text-center text-zinc-500 space-y-2">
              <BrainCircuit className="w-8 h-8 text-zinc-600" />
              <p className="text-xs">Select an advisory session to inspect the deep reasoning trace and knowledge citations.</p>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
