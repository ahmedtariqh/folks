"use client";

import React, { useState } from "react";
import { Sparkles, Bot, Shield, CheckCircle2, ArrowRight, ArrowLeft, Key, Cpu, Zap, Activity } from "lucide-react";

interface OnboardingWizardProps {
  onCompleted: (companyData: any) => void;
}

export function OnboardingWizard({ onCompleted }: OnboardingWizardProps) {
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [testingLlm, setTestingLlm] = useState(false);
  const [llmTestMsg, setLlmTestMsg] = useState<{ success: boolean; text: string } | null>(null);

  // Form State
  const [orgName, setOrgName] = useState("Apex Autonomous Labs");
  const [orgMission, setOrgMission] = useState(
    "Build high-reliability autonomous software engineering squads with resilient lock handoffs and zero-trust execution boundaries."
  );
  const [orgTag, setOrgTag] = useState("apex_core");

  // Custom LLM State
  const [providerType, setProviderType] = useState("custom");
  const [providerName, setProviderName] = useState("Custom LLM Gateway");
  const [baseUrl, setBaseUrl] = useState("http://localhost:11434/v1");
  const [apiKey, setApiKey] = useState("");
  const [defaultModel, setDefaultModel] = useState("llama3.3:70b");
  const [advisorModel, setAdvisorModel] = useState("deepseek-r1");

  // Agent State
  const [agentName, setAgentName] = useState("Nova - Lead Orchestrator");
  const [agentRole, setAgentRole] = useState("Chief Executive Agent");
  const [agentBackstory, setAgentBackstory] = useState(
    "Architect and executive lead. Coordinates ticket checkouts and enforces deterministic state transitions."
  );
  const [agentAdapter, setAgentAdapter] = useState("host_cli");
  const [agentBudget, setAgentBudget] = useState(100);

  // Advisor State
  const [advisorName, setAdvisorName] = useState("Dr. Aris Thorne");
  const [advisorDomain, setAdvisorDomain] = useState("DISTRIBUTED_SYSTEMS");
  const [advisorDocTitle, setAdvisorDocTitle] = useState("Lock Invariants and Sweeper Policies");
  const [advisorDocContent, setAdvisorDocContent] = useState(
    "Kanban holds primary lock. Daemons must emit 15s heartbeats. Expired locks after 60s MUST reap to DLQ."
  );

  // Initial Task
  const [taskTitle, setTaskTitle] = useState("Establish Host Daemon WebSocket Handshake & Telemetry");
  const [taskDesc, setTaskDesc] = useState(
    "Connect execution daemon to /ws/daemon/{daemon_id}, stream stdout telemetry chunks, and verify 15s heartbeats."
  );
  const [taskPriority, setTaskPriority] = useState("HIGH");

  const selectPreset = (type: string) => {
    setProviderType(type);
    if (type === "ollama") {
      setProviderName("Local Ollama");
      setBaseUrl("http://localhost:11434/v1");
      setDefaultModel("llama3.3:70b");
      setAdvisorModel("deepseek-r1");
    } else if (type === "anthropic") {
      setProviderName("Anthropic Claude");
      setBaseUrl("https://api.anthropic.com");
      setDefaultModel("claude-3-7-sonnet");
      setAdvisorModel("claude-3-7-sonnet-thought");
    } else if (type === "openai") {
      setProviderName("OpenAI Gateway");
      setBaseUrl("https://api.openai.com/v1");
      setDefaultModel("gpt-4o");
      setAdvisorModel("o3-mini");
    } else if (type === "openrouter") {
      setProviderName("OpenRouter");
      setBaseUrl("https://openrouter.ai/api/v1");
      setDefaultModel("anthropic/claude-3.7-sonnet");
      setAdvisorModel("deepseek/deepseek-r1");
    } else {
      setProviderName("Custom Gateway");
      setBaseUrl("http://localhost:8000/v1");
      setDefaultModel("custom-model");
      setAdvisorModel("custom-reasoner");
    }
  };

  const handleTestLlm = async () => {
    setTestingLlm(true);
    setLlmTestMsg(null);
    try {
      const res = await fetch("http://127.0.0.1:8000/api/v1/onboarding/test-llm", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          provider_type: providerType,
          provider_name: providerName,
          base_url: baseUrl || null,
          api_key: apiKey || null,
          default_model: defaultModel,
          advisor_reasoning_model: advisorModel,
        }),
      });
      const data = await res.json();
      setLlmTestMsg({
        success: data.success,
        text: data.message,
      });
    } catch {
      setLlmTestMsg({
        success: false,
        text: "Could not reach local server to test endpoint.",
      });
    } finally {
      setTestingLlm(false);
    }
  };

  const handleSubmit = async () => {
    setLoading(true);
    try {
      const payload = {
        organization: {
          name: orgName,
          mission: orgMission,
          project_tag: orgTag,
        },
        llm_provider: {
          provider_type: providerType,
          provider_name: providerName,
          base_url: baseUrl || null,
          api_key: apiKey || null,
          default_model: defaultModel,
          advisor_reasoning_model: advisorModel,
          temperature: 0.7,
          max_tokens: 4096,
        },
        lead_agent: {
          name: agentName,
          role: agentRole,
          backstory: agentBackstory,
          adapter_type: agentAdapter,
          monthly_budget_usd: agentBudget,
        },
        advisor: {
          name: advisorName,
          domain: advisorDomain,
          knowledge_title: advisorDocTitle,
          knowledge_content: advisorDocContent,
        },
        initial_task: {
          title: taskTitle,
          description: taskDesc,
          priority: taskPriority,
        },
      };

      const res = await fetch("http://127.0.0.1:8000/api/v1/onboarding/complete", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (res.ok) {
        onCompleted(payload);
      } else {
        alert("Failed to complete onboarding.");
      }
    } catch (err) {
      console.error(err);
      alert("Error submitting onboarding.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto my-8 bg-white border border-slate-200 rounded-2xl shadow-xl overflow-hidden text-slate-800">
      {/* Banner */}
      <div className="bg-gradient-to-r from-emerald-600 via-teal-600 to-indigo-600 p-8 text-white">
        <div className="flex items-center justify-between">
          <div>
            <span className="text-[10px] font-mono font-bold tracking-widest uppercase bg-white/20 px-2.5 py-1 rounded-full text-emerald-100">
              Paperclip Onboarding
            </span>
            <h1 className="text-2xl font-black mt-2 tracking-tight">Welcome to Folks</h1>
            <p className="text-emerald-100 text-xs mt-1 max-w-xl">
              Initialize your autonomous engineering organization with custom LLM settings, lead agent, and strategic advisor.
            </p>
          </div>
          <span className="text-4xl">📎</span>
        </div>

        {/* Stepper Dots */}
        <div className="mt-8 flex items-center justify-between relative max-w-2xl">
          <div className="absolute left-0 top-1/2 -translate-y-1/2 h-0.5 bg-white/30 w-full z-0" />
          {[1, 2, 3, 4, 5, 6].map((num) => (
            <div
              key={num}
              className={`z-10 w-8 h-8 rounded-full font-bold flex items-center justify-center text-xs transition ${
                num === step
                  ? "bg-white text-emerald-700 shadow-md ring-2 ring-emerald-300"
                  : num < step
                  ? "bg-emerald-300 text-emerald-900"
                  : "bg-white/40 text-white"
              }`}
            >
              {num}
            </div>
          ))}
        </div>
      </div>

      <div className="p-8">
        {/* STEP 1: Company & Mission */}
        {step === 1 && (
          <div className="space-y-6">
            <div>
              <h2 className="text-lg font-bold text-slate-900">Step 1: Define Your Company & Mission</h2>
              <p className="text-xs text-slate-500 mt-0.5">High-level context that all autonomous agents use to align their execution.</p>
            </div>
            <div className="space-y-4 text-xs">
              <div>
                <label className="block font-semibold text-slate-700 mb-1">Company / Organization Name</label>
                <input
                  type="text"
                  value={orgName}
                  onChange={(e) => setOrgName(e.target.value)}
                  className="w-full bg-slate-50 border border-slate-300 rounded-lg px-3.5 py-2.5 text-slate-900 text-sm focus:outline-none focus:border-emerald-500 focus:bg-white"
                />
              </div>
              <div>
                <label className="block font-semibold text-slate-700 mb-1">Core Mission Statement</label>
                <textarea
                  rows={3}
                  value={orgMission}
                  onChange={(e) => setOrgMission(e.target.value)}
                  className="w-full bg-slate-50 border border-slate-300 rounded-lg px-3.5 py-2.5 text-slate-900 text-sm focus:outline-none focus:border-emerald-500 focus:bg-white"
                />
              </div>
              <div>
                <label className="block font-semibold text-slate-700 mb-1">Project Scope Tag</label>
                <input
                  type="text"
                  value={orgTag}
                  onChange={(e) => setOrgTag(e.target.value)}
                  className="w-full bg-slate-50 border border-slate-300 rounded-lg px-3.5 py-2 text-slate-900 font-mono text-xs focus:outline-none focus:border-emerald-500 focus:bg-white"
                />
              </div>
            </div>
            <div className="flex justify-end pt-4 border-t border-slate-200">
              <button
                onClick={() => setStep(2)}
                className="bg-emerald-600 hover:bg-emerald-700 text-white px-5 py-2 rounded-lg text-xs font-semibold shadow-xs flex items-center space-x-1.5"
              >
                <span>Next: Custom LLM Settings</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
        )}

        {/* STEP 2: Custom LLM Provider */}
        {step === 2 && (
          <div className="space-y-6">
            <div>
              <span className="text-[10px] font-bold font-mono px-2 py-0.5 rounded bg-indigo-50 text-indigo-700 border border-indigo-200">
                CUSTOM GATEWAY
              </span>
              <h2 className="text-lg font-bold text-slate-900 mt-1">Step 2: Configure Custom LLM Provider</h2>
              <p className="text-xs text-slate-500 mt-0.5">Plug in your custom OpenAI-compatible endpoint, local Ollama, or cloud model.</p>
            </div>

            {/* Presets */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-2.5">
              {[
                { id: "custom", label: "Custom Endpoint", icon: "⚡" },
                { id: "ollama", label: "Local Ollama", icon: "🦙" },
                { id: "anthropic", label: "Anthropic Claude", icon: "🧠" },
                { id: "openai", label: "OpenAI", icon: "🤖" },
              ].map((p) => (
                <div
                  key={p.id}
                  onClick={() => selectPreset(p.id)}
                  className={`p-3 rounded-xl border text-xs cursor-pointer transition ${
                    providerType === p.id
                      ? "border-emerald-600 bg-emerald-50/40 font-bold text-slate-900"
                      : "border-slate-200 bg-white hover:border-slate-300 text-slate-700"
                  }`}
                >
                  <span className="text-base mr-1.5">{p.icon}</span>
                  <span>{p.label}</span>
                </div>
              ))}
            </div>

            <div className="space-y-3.5 text-xs bg-slate-50/70 p-4 rounded-xl border border-slate-200">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                <div>
                  <label className="block font-semibold text-slate-700 mb-1">Provider Label</label>
                  <input
                    type="text"
                    value={providerName}
                    onChange={(e) => setProviderName(e.target.value)}
                    className="w-full bg-white border border-slate-300 rounded-lg px-3 py-2 text-slate-900 focus:outline-none focus:border-emerald-500"
                  />
                </div>
                <div>
                  <label className="block font-semibold text-slate-700 mb-1">Base URL</label>
                  <input
                    type="text"
                    value={baseUrl}
                    onChange={(e) => setBaseUrl(e.target.value)}
                    className="w-full bg-white border border-slate-300 rounded-lg px-3 py-2 text-slate-900 font-mono focus:outline-none focus:border-emerald-500"
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                <div>
                  <label className="block font-semibold text-slate-700 mb-1">API Key / Token</label>
                  <input
                    type="password"
                    value={apiKey}
                    onChange={(e) => setApiKey(e.target.value)}
                    placeholder="sk-... (Optional for Ollama)"
                    className="w-full bg-white border border-slate-300 rounded-lg px-3 py-2 text-slate-900 font-mono text-xs focus:outline-none focus:border-emerald-500"
                  />
                </div>
                <div>
                  <label className="block font-semibold text-slate-700 mb-1">Default Agent Model</label>
                  <input
                    type="text"
                    value={defaultModel}
                    onChange={(e) => setDefaultModel(e.target.value)}
                    className="w-full bg-white border border-slate-300 rounded-lg px-3 py-2 text-slate-900 font-mono focus:outline-none focus:border-emerald-500"
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                <div>
                  <label className="block font-semibold text-slate-700 mb-1">Advisor Reasoning Model</label>
                  <input
                    type="text"
                    value={advisorModel}
                    onChange={(e) => setAdvisorModel(e.target.value)}
                    className="w-full bg-white border border-slate-300 rounded-lg px-3 py-2 text-slate-900 font-mono focus:outline-none focus:border-emerald-500"
                  />
                </div>
                <div className="flex items-end">
                  <button
                    type="button"
                    onClick={handleTestLlm}
                    disabled={testingLlm}
                    className="w-full bg-indigo-50 hover:bg-indigo-100 text-indigo-700 border border-indigo-200 font-semibold px-4 py-2 rounded-lg transition text-xs flex items-center justify-center gap-1.5"
                  >
                    <Zap className="w-3.5 h-3.5" />
                    <span>{testingLlm ? "Testing Connection..." : "Test Endpoint Connection"}</span>
                  </button>
                </div>
              </div>

              {llmTestMsg && (
                <div
                  className={`p-2.5 rounded-lg border text-xs font-mono ${
                    llmTestMsg.success
                      ? "bg-emerald-50 border-emerald-200 text-emerald-800"
                      : "bg-amber-50 border-amber-200 text-amber-800"
                  }`}
                >
                  {llmTestMsg.text}
                </div>
              )}
            </div>

            <div className="flex justify-between pt-4 border-t border-slate-200">
              <button onClick={() => setStep(1)} className="text-slate-600 hover:text-slate-900 px-4 py-2 text-xs font-medium">
                &larr; Back
              </button>
              <button
                onClick={() => setStep(3)}
                className="bg-emerald-600 hover:bg-emerald-700 text-white px-5 py-2 rounded-lg text-xs font-semibold shadow-xs flex items-center space-x-1.5"
              >
                <span>Next: Hire CEO / Lead Agent</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
        )}

        {/* STEP 3: Lead Agent */}
        {step === 3 && (
          <div className="space-y-6">
            <div>
              <h2 className="text-lg font-bold text-slate-900">Step 3: Hire Lead Agent (CEO)</h2>
              <p className="text-xs text-slate-500 mt-0.5">Primary orchestrator coordinating tasks and virtual squads.</p>
            </div>
            <div className="space-y-4 text-xs">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                <div>
                  <label className="block font-semibold text-slate-700 mb-1">Agent Name</label>
                  <input
                    type="text"
                    value={agentName}
                    onChange={(e) => setAgentName(e.target.value)}
                    className="w-full bg-slate-50 border border-slate-300 rounded-lg px-3 py-2 text-slate-900 focus:outline-none focus:border-emerald-500 focus:bg-white"
                  />
                </div>
                <div>
                  <label className="block font-semibold text-slate-700 mb-1">Role Title</label>
                  <input
                    type="text"
                    value={agentRole}
                    onChange={(e) => setAgentRole(e.target.value)}
                    className="w-full bg-slate-50 border border-slate-300 rounded-lg px-3 py-2 text-slate-900 focus:outline-none focus:border-emerald-500 focus:bg-white"
                  />
                </div>
              </div>
              <div>
                <label className="block font-semibold text-slate-700 mb-1">Persona & Backstory</label>
                <textarea
                  rows={3}
                  value={agentBackstory}
                  onChange={(e) => setAgentBackstory(e.target.value)}
                  className="w-full bg-slate-50 border border-slate-300 rounded-lg px-3 py-2 text-slate-900 focus:outline-none focus:border-emerald-500 focus:bg-white"
                />
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                <div>
                  <label className="block font-semibold text-slate-700 mb-1">Harness / Daemon Adapter</label>
                  <select
                    value={agentAdapter}
                    onChange={(e) => setAgentAdapter(e.target.value)}
                    className="w-full bg-slate-50 border border-slate-300 rounded-lg px-3 py-2 text-slate-900 focus:outline-none focus:border-emerald-500"
                  >
                    <option value="host_cli">Local Host CLI Daemon</option>
                    <option value="claude_local">Claude Local Harness</option>
                  </select>
                </div>
                <div>
                  <label className="block font-semibold text-slate-700 mb-1">Monthly Budget Cap (USD)</label>
                  <input
                    type="number"
                    value={agentBudget}
                    onChange={(e) => setAgentBudget(parseFloat(e.target.value))}
                    className="w-full bg-slate-50 border border-slate-300 rounded-lg px-3 py-2 text-slate-900 focus:outline-none focus:border-emerald-500"
                  />
                </div>
              </div>
            </div>
            <div className="flex justify-between pt-4 border-t border-slate-200">
              <button onClick={() => setStep(2)} className="text-slate-600 hover:text-slate-900 px-4 py-2 text-xs font-medium">
                &larr; Back
              </button>
              <button
                onClick={() => setStep(4)}
                className="bg-emerald-600 hover:bg-emerald-700 text-white px-5 py-2 rounded-lg text-xs font-semibold shadow-xs flex items-center space-x-1.5"
              >
                <span>Next: Appoint Advisor</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
        )}

        {/* STEP 4: Strategic Advisor */}
        {step === 4 && (
          <div className="space-y-6">
            <div>
              <h2 className="text-lg font-bold text-slate-900">Step 4: Appoint Strategic Advisor</h2>
              <p className="text-xs text-slate-500 mt-0.5">Domain authority equipped with deep reasoning to review critical decisions.</p>
            </div>
            <div className="space-y-4 text-xs">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                <div>
                  <label className="block font-semibold text-slate-700 mb-1">Advisor Name</label>
                  <input
                    type="text"
                    value={advisorName}
                    onChange={(e) => setAdvisorName(e.target.value)}
                    className="w-full bg-slate-50 border border-slate-300 rounded-lg px-3 py-2 text-slate-900 focus:outline-none focus:border-emerald-500 focus:bg-white"
                  />
                </div>
                <div>
                  <label className="block font-semibold text-slate-700 mb-1">Domain</label>
                  <select
                    value={advisorDomain}
                    onChange={(e) => setAdvisorDomain(e.target.value)}
                    className="w-full bg-slate-50 border border-slate-300 rounded-lg px-3 py-2 text-slate-900 focus:outline-none focus:border-emerald-500"
                  >
                    <option value="DISTRIBUTED_SYSTEMS">Distributed Systems</option>
                    <option value="SECURITY_COMPLIANCE">Security & Zero-Trust</option>
                    <option value="ENTERPRISE_ARCHITECTURE">Enterprise Architecture</option>
                  </select>
                </div>
              </div>
              <div>
                <label className="block font-semibold text-slate-700 mb-1">Foundational Knowledge Document Title</label>
                <input
                  type="text"
                  value={advisorDocTitle}
                  onChange={(e) => setAdvisorDocTitle(e.target.value)}
                  className="w-full bg-slate-50 border border-slate-300 rounded-lg px-3 py-2 text-slate-900 focus:outline-none focus:border-emerald-500 focus:bg-white"
                />
              </div>
              <div>
                <label className="block font-semibold text-slate-700 mb-1">Knowledge Content</label>
                <textarea
                  rows={3}
                  value={advisorDocContent}
                  onChange={(e) => setAdvisorDocContent(e.target.value)}
                  className="w-full bg-slate-50 border border-slate-300 rounded-lg px-3 py-2 text-slate-900 focus:outline-none focus:border-emerald-500 focus:bg-white"
                />
              </div>
            </div>
            <div className="flex justify-between pt-4 border-t border-slate-200">
              <button onClick={() => setStep(3)} className="text-slate-600 hover:text-slate-900 px-4 py-2 text-xs font-medium">
                &larr; Back
              </button>
              <button
                onClick={() => setStep(5)}
                className="bg-emerald-600 hover:bg-emerald-700 text-white px-5 py-2 rounded-lg text-xs font-semibold shadow-xs flex items-center space-x-1.5"
              >
                <span>Next: First Mission</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
        )}

        {/* STEP 5: First Kanban Mission */}
        {step === 5 && (
          <div className="space-y-6">
            <div>
              <h2 className="text-lg font-bold text-slate-900">Step 5: Define First Mission / Task</h2>
              <p className="text-xs text-slate-500 mt-0.5">Kickstart your Kanban backlog with an initial task.</p>
            </div>
            <div className="space-y-4 text-xs">
              <div>
                <label className="block font-semibold text-slate-700 mb-1">Task Title</label>
                <input
                  type="text"
                  value={taskTitle}
                  onChange={(e) => setTaskTitle(e.target.value)}
                  className="w-full bg-slate-50 border border-slate-300 rounded-lg px-3.5 py-2.5 text-slate-900 text-sm focus:outline-none focus:border-emerald-500 focus:bg-white"
                />
              </div>
              <div>
                <label className="block font-semibold text-slate-700 mb-1">Description</label>
                <textarea
                  rows={3}
                  value={taskDesc}
                  onChange={(e) => setTaskDesc(e.target.value)}
                  className="w-full bg-slate-50 border border-slate-300 rounded-lg px-3.5 py-2 text-slate-900 focus:outline-none focus:border-emerald-500 focus:bg-white"
                />
              </div>
              <div>
                <label className="block font-semibold text-slate-700 mb-1">Priority</label>
                <select
                  value={taskPriority}
                  onChange={(e) => setTaskPriority(e.target.value)}
                  className="w-full bg-slate-50 border border-slate-300 rounded-lg px-3 py-2 text-slate-900 focus:outline-none focus:border-emerald-500"
                >
                  <option value="LOW">LOW</option>
                  <option value="MEDIUM">MEDIUM</option>
                  <option value="HIGH">HIGH</option>
                  <option value="URGENT">URGENT</option>
                </select>
              </div>
            </div>
            <div className="flex justify-between pt-4 border-t border-slate-200">
              <button onClick={() => setStep(4)} className="text-slate-600 hover:text-slate-900 px-4 py-2 text-xs font-medium">
                &larr; Back
              </button>
              <button
                onClick={() => setStep(6)}
                className="bg-emerald-600 hover:bg-emerald-700 text-white px-5 py-2 rounded-lg text-xs font-semibold shadow-xs flex items-center space-x-1.5"
              >
                <span>Review & Launch</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
        )}

        {/* STEP 6: Summary */}
        {step === 6 && (
          <div className="space-y-6">
            <div>
              <h2 className="text-lg font-bold text-slate-900">Step 6: Ready to Launch</h2>
              <p className="text-xs text-slate-500 mt-0.5">Review your configuration before saving directly to the database.</p>
            </div>

            <div className="bg-slate-50 rounded-xl p-5 border border-slate-200 space-y-3 text-xs">
              <div className="flex justify-between border-b border-slate-200 pb-2">
                <span className="text-slate-500">Company:</span>
                <span className="font-bold text-slate-900">{orgName} ({orgTag})</span>
              </div>
              <div className="flex justify-between border-b border-slate-200 pb-2">
                <span className="text-slate-500">Custom LLM:</span>
                <span className="font-mono font-semibold text-indigo-700">{providerName} ({defaultModel})</span>
              </div>
              <div className="flex justify-between border-b border-slate-200 pb-2">
                <span className="text-slate-500">Lead Orchestrator (CEO):</span>
                <span className="font-bold text-slate-900">{agentName}</span>
              </div>
              <div className="flex justify-between border-b border-slate-200 pb-2">
                <span className="text-slate-500">Board Advisor:</span>
                <span className="font-bold text-purple-700">{advisorName}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">Initial Task:</span>
                <span className="font-medium text-slate-800">{taskTitle}</span>
              </div>
            </div>

            <div className="flex justify-between pt-4 border-t border-slate-200">
              <button onClick={() => setStep(5)} className="text-slate-600 hover:text-slate-900 px-4 py-2 text-xs font-medium">
                &larr; Back
              </button>
              <button
                onClick={handleSubmit}
                disabled={loading}
                className="bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-700 hover:to-teal-700 text-white px-7 py-2.5 rounded-lg text-xs font-bold shadow-md transition"
              >
                {loading ? "Saving to Database..." : "🚀 Launch Organization & Save to Database"}
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
