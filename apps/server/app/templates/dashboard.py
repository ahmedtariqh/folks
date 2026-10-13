def get_dashboard_html() -> str:
    return """<!DOCTYPE html>
<html lang="en" class="light">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>FOLKS // Multi-Agent Orchestrator</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <script>
    tailwind.config = {
      darkMode: 'class',
      theme: {
        extend: {
          colors: {
            brand: {
              50: '#ecfdf5',
              100: '#d1fae5',
              500: '#10b981',
              600: '#059669',
              700: '#047857',
            }
          }
        }
      }
    }
  </script>
  <style>
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    }
    .custom-scroll::-webkit-scrollbar {
      width: 6px;
      height: 6px;
    }
    .custom-scroll::-webkit-scrollbar-track {
      background: #f1f5f9;
    }
    .custom-scroll::-webkit-scrollbar-thumb {
      background: #cbd5e1;
      border-radius: 3px;
    }
    .pulse-dot {
      animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
    }
    @keyframes pulse {
      0%, 100% { opacity: 1; }
      50% { opacity: .3; }
    }
  </style>
</head>
<body class="min-h-screen flex flex-col bg-[#f8fafc] text-slate-800 antialiased selection:bg-emerald-500 selection:text-white">

  <!-- Top Navigation Header -->
  <header class="border-b border-slate-200 bg-white/95 backdrop-blur sticky top-0 z-40 px-6 py-3 flex items-center justify-between shadow-xs">
    <div class="flex items-center space-x-4">
      <div class="flex items-center space-x-2.5">
        <div class="w-8 h-8 rounded-lg bg-emerald-600 flex items-center justify-center font-black text-white text-base shadow-sm">
          F
        </div>
        <div>
          <div class="flex items-center space-x-2">
            <span class="font-extrabold tracking-tight text-slate-900 text-lg">FOLKS</span>
            <span class="text-[11px] px-2 py-0.5 rounded-full bg-slate-100 text-slate-700 border border-slate-200 font-mono font-medium">Orchestrator</span>
            <span id="headerCompanyBadge" class="hidden text-[11px] px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200 font-semibold font-sans"></span>
          </div>
          <p class="text-[11px] text-slate-500">Paperclip-style Resilient Agent Architecture & Host Daemon</p>
        </div>
      </div>
      
      <div class="hidden lg:flex items-center space-x-2 pl-4 border-l border-slate-200 text-xs">
        <div class="flex items-center space-x-1.5 bg-slate-50 px-2.5 py-1 rounded-md border border-slate-200 text-slate-600">
          <span class="w-2 h-2 rounded-full bg-emerald-500 pulse-dot"></span>
          <span class="font-mono font-medium">API :8000</span>
        </div>
        <div id="llmActiveBadge" class="hidden items-center space-x-1.5 bg-indigo-50 px-2.5 py-1 rounded-md border border-indigo-200 text-indigo-700 text-xs">
          <span>⚡</span>
          <span id="llmActiveText" class="font-mono font-medium">Custom LLM</span>
        </div>
        <div id="wsStatusBadge" class="flex items-center space-x-1.5 bg-slate-50 px-2.5 py-1 rounded-md border border-slate-200 text-slate-600">
          <span id="wsStatusDot" class="w-2 h-2 rounded-full bg-amber-400 pulse-dot"></span>
          <span id="wsStatusText" class="font-mono">WS Connecting...</span>
        </div>
      </div>
    </div>

    <div class="flex items-center space-x-2.5">
      <button onclick="launchOnboardingWizard(true)" class="text-xs bg-white hover:bg-slate-50 text-slate-700 font-medium px-3 py-1.5 rounded-lg border border-slate-200 flex items-center space-x-1.5 shadow-xs transition">
        <span>⚙️</span>
        <span>Setup Wizard</span>
      </button>

      <button onclick="openNewTaskModal()" class="text-xs bg-emerald-600 hover:bg-emerald-700 text-white font-medium px-3.5 py-1.5 rounded-lg border border-emerald-600 flex items-center space-x-1 shadow-xs transition">
        <span>➕</span>
        <span>New Task</span>
      </button>

      <a href="/docs" target="_blank" class="text-xs bg-white hover:bg-slate-50 text-slate-600 px-3 py-1.5 rounded-lg border border-slate-200 flex items-center space-x-1 shadow-xs transition">
        <span>📖</span>
        <span>API Docs</span>
      </a>

      <button onclick="resetOnboardingFresh()" title="Reset onboarding to test first-time setup flow" class="text-xs bg-slate-100 hover:bg-slate-200 text-slate-600 px-2.5 py-1.5 rounded-lg border border-slate-200 transition">
        <span>🔄 Reset Flow</span>
      </button>
    </div>
  </header>

  <!-- ONBOARDING WIZARD CONTAINER (Displayed for First-Time Setup) -->
  <section id="onboardingSection" class="hidden flex-1 max-w-4xl w-full mx-auto p-6 md:p-10 my-auto">
    <div class="bg-white border border-slate-200 rounded-2xl shadow-xl overflow-hidden">
      
      <!-- Wizard Header Banner -->
      <div class="bg-gradient-to-r from-emerald-600 via-teal-600 to-indigo-600 p-8 text-white">
        <div class="flex items-center justify-between">
          <div>
            <span class="text-xs font-mono font-bold tracking-widest uppercase bg-white/20 px-2.5 py-1 rounded-full text-emerald-100">Paperclip Initialization</span>
            <h1 class="text-2xl font-black mt-2 tracking-tight">Welcome to Folks</h1>
            <p class="text-emerald-100 text-xs mt-1 max-w-xl">Set up your autonomous organization, configure your custom LLM gateway, hire your CEO agent, and assign your first mission.</p>
          </div>
          <div class="hidden sm:block text-5xl opacity-80 font-mono">📎</div>
        </div>

        <!-- Stepper Indicator -->
        <div class="mt-8 flex items-center justify-between relative max-w-2xl">
          <div class="absolute left-0 top-1/2 -translate-y-1/2 h-0.5 bg-white/30 w-full z-0"></div>
          <div id="stepDot1" class="step-dot z-10 w-8 h-8 rounded-full bg-white text-emerald-700 font-bold flex items-center justify-center text-xs shadow-md">1</div>
          <div id="stepDot2" class="step-dot z-10 w-8 h-8 rounded-full bg-white/40 text-white font-bold flex items-center justify-center text-xs">2</div>
          <div id="stepDot3" class="step-dot z-10 w-8 h-8 rounded-full bg-white/40 text-white font-bold flex items-center justify-center text-xs">3</div>
          <div id="stepDot4" class="step-dot z-10 w-8 h-8 rounded-full bg-white/40 text-white font-bold flex items-center justify-center text-xs">4</div>
          <div id="stepDot5" class="step-dot z-10 w-8 h-8 rounded-full bg-white/40 text-white font-bold flex items-center justify-center text-xs">5</div>
          <div id="stepDot6" class="step-dot z-10 w-8 h-8 rounded-full bg-white/40 text-white font-bold flex items-center justify-center text-xs">6</div>
        </div>
      </div>

      <!-- Wizard Step Content -->
      <div class="p-8">
        
        <!-- STEP 1: Organization & Mission -->
        <div id="wizardStep1" class="space-y-6">
          <div>
            <h2 class="text-lg font-bold text-slate-900">Step 1: Define Your Company & Core Mission</h2>
            <p class="text-xs text-slate-500 mt-0.5">The high-level context document that all autonomous agents read to align their execution.</p>
          </div>

          <div class="space-y-4 text-xs">
            <div>
              <label class="block font-semibold text-slate-700 mb-1">Company / Organization Name</label>
              <input id="obOrgName" type="text" value="Apex Autonomous Labs" class="w-full bg-slate-50 border border-slate-300 rounded-lg px-3.5 py-2.5 text-slate-900 focus:outline-none focus:border-emerald-500 focus:bg-white text-sm" placeholder="e.g. Acme Corp">
            </div>

            <div>
              <label class="block font-semibold text-slate-700 mb-1">Core Mission Statement</label>
              <textarea id="obOrgMission" rows="3" class="w-full bg-slate-50 border border-slate-300 rounded-lg px-3.5 py-2.5 text-slate-900 focus:outline-none focus:border-emerald-500 focus:bg-white text-sm" placeholder="Detail high-level objectives, operating directives, and architectural invariants...">Build high-reliability autonomous software engineering squads with resilient lock handoffs, zero-trust execution boundaries, and continuous automated verification.</textarea>
            </div>

            <div>
              <label class="block font-semibold text-slate-700 mb-1">Project Scope Tag</label>
              <input id="obOrgTag" type="text" value="apex_core" class="w-full bg-slate-50 border border-slate-300 rounded-lg px-3.5 py-2.5 text-slate-900 focus:outline-none focus:border-emerald-500 focus:bg-white font-mono text-xs" placeholder="e.g. project_main">
              <span class="text-[11px] text-slate-400 mt-1 block">Strict namespace tag bounding agent permissions and Kanban task checkouts.</span>
            </div>
          </div>

          <div class="flex justify-end pt-4 border-t border-slate-200">
            <button onclick="goToWizardStep(2)" class="bg-emerald-600 hover:bg-emerald-700 text-white px-5 py-2 rounded-lg text-xs font-semibold shadow-sm transition flex items-center space-x-1.5">
              <span>Next: Custom LLM Settings</span>
              <span>&rarr;</span>
            </button>
          </div>
        </div>

        <!-- STEP 2: Custom LLM Provider Setting (Requested Directive) -->
        <div id="wizardStep2" class="hidden space-y-6">
          <div>
            <div class="flex items-center space-x-2">
              <span class="px-2 py-0.5 bg-indigo-50 text-indigo-700 rounded border border-indigo-200 font-mono text-[10px] font-bold">CUSTOM GATEWAY</span>
              <h2 class="text-lg font-bold text-slate-900">Step 2: Configure Custom LLM Provider</h2>
            </div>
            <p class="text-xs text-slate-500 mt-0.5">Plug in your custom OpenAI-compatible endpoint, local Ollama instance, or enterprise cloud model.</p>
          </div>

          <!-- Provider Select Cards -->
          <div class="grid grid-cols-2 md:grid-cols-3 gap-3">
            <div onclick="selectProviderPreset('custom')" id="presetCard_custom" class="provider-preset-card border-2 border-emerald-600 bg-emerald-50/40 rounded-xl p-3 cursor-pointer transition text-xs">
              <div class="flex items-center justify-between">
                <span class="font-bold text-slate-900">Custom Gateway</span>
                <span>⚡</span>
              </div>
              <p class="text-[11px] text-slate-500 mt-1">OpenAI-compatible proxy, vLLM, LMStudio</p>
            </div>

            <div onclick="selectProviderPreset('ollama')" id="presetCard_ollama" class="provider-preset-card border border-slate-200 bg-white hover:border-slate-300 rounded-xl p-3 cursor-pointer transition text-xs">
              <div class="flex items-center justify-between">
                <span class="font-bold text-slate-900">Local Ollama</span>
                <span>🦙</span>
              </div>
              <p class="text-[11px] text-slate-500 mt-1">Localhost :11434 with zero cloud dependencies</p>
            </div>

            <div onclick="selectProviderPreset('anthropic')" id="presetCard_anthropic" class="provider-preset-card border border-slate-200 bg-white hover:border-slate-300 rounded-xl p-3 cursor-pointer transition text-xs">
              <div class="flex items-center justify-between">
                <span class="font-bold text-slate-900">Anthropic</span>
                <span>🧠</span>
              </div>
              <p class="text-[11px] text-slate-500 mt-1">Claude 3.7 Sonnet & Thought</p>
            </div>

            <div onclick="selectProviderPreset('openai')" id="presetCard_openai" class="provider-preset-card border border-slate-200 bg-white hover:border-slate-300 rounded-xl p-3 cursor-pointer transition text-xs">
              <div class="flex items-center justify-between">
                <span class="font-bold text-slate-900">OpenAI</span>
                <span>🤖</span>
              </div>
              <p class="text-[11px] text-slate-500 mt-1">GPT-4o & o3-mini models</p>
            </div>

            <div onclick="selectProviderPreset('openrouter')" id="presetCard_openrouter" class="provider-preset-card border border-slate-200 bg-white hover:border-slate-300 rounded-xl p-3 cursor-pointer transition text-xs">
              <div class="flex items-center justify-between">
                <span class="font-bold text-slate-900">OpenRouter</span>
                <span>🌐</span>
              </div>
              <p class="text-[11px] text-slate-500 mt-1">Multi-model router gateway</p>
            </div>

            <div onclick="selectProviderPreset('gemini')" id="presetCard_gemini" class="provider-preset-card border border-slate-200 bg-white hover:border-slate-300 rounded-xl p-3 cursor-pointer transition text-xs">
              <div class="flex items-center justify-between">
                <span class="font-bold text-slate-900">Google Gemini</span>
                <span>✨</span>
              </div>
              <p class="text-[11px] text-slate-500 mt-1">Gemini 2.0 Flash / Pro models</p>
            </div>
          </div>

          <!-- Configuration Fields -->
          <div class="space-y-3.5 text-xs bg-slate-50/70 p-4 rounded-xl border border-slate-200">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
              <div>
                <label class="block font-semibold text-slate-700 mb-1">Provider Label</label>
                <input id="obLlmName" type="text" value="Custom LLM Gateway" class="w-full bg-white border border-slate-300 rounded-lg px-3 py-2 text-slate-900 focus:outline-none focus:border-emerald-500">
              </div>
              <div>
                <label class="block font-semibold text-slate-700 mb-1">Base URL (API Endpoint)</label>
                <input id="obLlmBaseUrl" type="text" value="http://localhost:11434/v1" class="w-full bg-white border border-slate-300 rounded-lg px-3 py-2 text-slate-900 font-mono focus:outline-none focus:border-emerald-500" placeholder="https://api.openai.com/v1 or http://localhost:11434/v1">
              </div>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
              <div>
                <label class="block font-semibold text-slate-700 mb-1">API Key / Bearer Token</label>
                <div class="relative">
                  <input id="obLlmApiKey" type="password" placeholder="sk-... (Leave empty for local Ollama)" class="w-full bg-white border border-slate-300 rounded-lg px-3 py-2 pr-10 text-slate-900 focus:outline-none focus:border-emerald-500 font-mono text-xs">
                  <button type="button" onclick="toggleApiKeyVisibility()" class="absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 text-xs">👁️</button>
                </div>
              </div>
              <div>
                <label class="block font-semibold text-slate-700 mb-1">Default Agent Model</label>
                <input id="obLlmDefaultModel" type="text" value="llama3.3:70b" class="w-full bg-white border border-slate-300 rounded-lg px-3 py-2 text-slate-900 font-mono focus:outline-none focus:border-emerald-500" placeholder="e.g. claude-3-7-sonnet, llama3.3:70b">
              </div>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
              <div>
                <label class="block font-semibold text-slate-700 mb-1">Advisor Deep-Reasoning Model</label>
                <input id="obLlmAdvisorModel" type="text" value="deepseek-r1" class="w-full bg-white border border-slate-300 rounded-lg px-3 py-2 text-slate-900 font-mono focus:outline-none focus:border-emerald-500" placeholder="e.g. claude-3-7-sonnet-thought, o3-mini, deepseek-r1">
                <span class="text-[10px] text-slate-400">Model used exclusively by the Board of Advisors for complex reviews.</span>
              </div>
              <div class="flex items-end">
                <button type="button" onclick="testLlmConnection()" id="btnTestLlm" class="w-full bg-indigo-50 hover:bg-indigo-100 text-indigo-700 border border-indigo-200 font-semibold px-4 py-2 rounded-lg transition flex items-center justify-center space-x-1.5">
                  <span>⚡</span>
                  <span>Test Endpoint Connection</span>
                </button>
              </div>
            </div>

            <!-- Test Connection Result Notification -->
            <div id="llmTestResult" class="hidden p-2.5 rounded-lg border text-xs font-mono"></div>
          </div>

          <div class="flex justify-between pt-4 border-t border-slate-200">
            <button onclick="goToWizardStep(1)" class="text-slate-600 hover:text-slate-900 px-4 py-2 text-xs font-medium">&larr; Back</button>
            <button onclick="goToWizardStep(3)" class="bg-emerald-600 hover:bg-emerald-700 text-white px-5 py-2 rounded-lg text-xs font-semibold shadow-sm transition flex items-center space-x-1.5">
              <span>Next: Hire CEO / Lead Agent</span>
              <span>&rarr;</span>
            </button>
          </div>
        </div>

        <!-- STEP 3: Hire First Lead Agent / CEO -->
        <div id="wizardStep3" class="hidden space-y-6">
          <div>
            <h2 class="text-lg font-bold text-slate-900">Step 3: Hire Your Primary Lead Agent (CEO)</h2>
            <p class="text-xs text-slate-500 mt-0.5">The primary orchestrator in charge of coordinating virtual teams and executing Kanban tasks.</p>
          </div>

          <div class="space-y-4 text-xs">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
              <div>
                <label class="block font-semibold text-slate-700 mb-1">Agent Name</label>
                <input id="obAgentName" type="text" value="Nova - Lead Orchestrator" class="w-full bg-slate-50 border border-slate-300 rounded-lg px-3.5 py-2 text-slate-900 focus:outline-none focus:border-emerald-500 focus:bg-white">
              </div>
              <div>
                <label class="block font-semibold text-slate-700 mb-1">Role Title</label>
                <input id="obAgentRole" type="text" value="Chief Executive Agent" class="w-full bg-slate-50 border border-slate-300 rounded-lg px-3.5 py-2 text-slate-900 focus:outline-none focus:border-emerald-500 focus:bg-white">
              </div>
            </div>

            <div>
              <label class="block font-semibold text-slate-700 mb-1">Agent Backstory & Operating Persona</label>
              <textarea id="obAgentBackstory" rows="3" class="w-full bg-slate-50 border border-slate-300 rounded-lg px-3.5 py-2 text-slate-900 focus:outline-none focus:border-emerald-500 focus:bg-white">Architect and executive lead. Coordinates asynchronous ticket checkouts, delegates specialized sub-routines, and enforces deterministic state transitions.</textarea>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
              <div>
                <label class="block font-semibold text-slate-700 mb-1">Execution Harness / Daemon Adapter</label>
                <select id="obAgentAdapter" class="w-full bg-slate-50 border border-slate-300 rounded-lg px-3 py-2 text-slate-900 focus:outline-none focus:border-emerald-500">
                  <option value="host_cli" selected>Local Host CLI Daemon (Streaming WebSockets)</option>
                  <option value="claude_local">Claude Local Harness</option>
                  <option value="docker_sandbox">Isolated Docker Sandbox</option>
                </select>
              </div>
              <div>
                <label class="block font-semibold text-slate-700 mb-1">Monthly Budget Cap (USD)</label>
                <input id="obAgentBudget" type="number" value="100.00" step="10" class="w-full bg-slate-50 border border-slate-300 rounded-lg px-3 py-2 text-slate-900 focus:outline-none focus:border-emerald-500">
              </div>
            </div>
          </div>

          <div class="flex justify-between pt-4 border-t border-slate-200">
            <button onclick="goToWizardStep(2)" class="text-slate-600 hover:text-slate-900 px-4 py-2 text-xs font-medium">&larr; Back</button>
            <button onclick="goToWizardStep(4)" class="bg-emerald-600 hover:bg-emerald-700 text-white px-5 py-2 rounded-lg text-xs font-semibold shadow-sm transition flex items-center space-x-1.5">
              <span>Next: Appoint Strategic Advisor</span>
              <span>&rarr;</span>
            </button>
          </div>
        </div>

        <!-- STEP 4: Appoint Strategic Advisor (Board of Advisors) -->
        <div id="wizardStep4" class="hidden space-y-6">
          <div>
            <h2 class="text-lg font-bold text-slate-900">Step 4: Appoint Your First Strategic Advisor</h2>
            <p class="text-xs text-slate-500 mt-0.5">Heavy-weight domain authority with deep reasoning capabilities to review architectures and critical PRs.</p>
          </div>

          <div class="space-y-4 text-xs">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
              <div>
                <label class="block font-semibold text-slate-700 mb-1">Advisor Name</label>
                <input id="obAdvName" type="text" value="Dr. Aris Thorne" class="w-full bg-slate-50 border border-slate-300 rounded-lg px-3.5 py-2 text-slate-900 focus:outline-none focus:border-emerald-500 focus:bg-white">
              </div>
              <div>
                <label class="block font-semibold text-slate-700 mb-1">Domain Authority</label>
                <select id="obAdvDomain" class="w-full bg-slate-50 border border-slate-300 rounded-lg px-3 py-2 text-slate-900 focus:outline-none focus:border-emerald-500">
                  <option value="DISTRIBUTED_SYSTEMS" selected>Distributed Systems & Resilience</option>
                  <option value="SECURITY_COMPLIANCE">Security & Zero-Trust Compliance</option>
                  <option value="ENTERPRISE_ARCHITECTURE">Enterprise Software Architecture</option>
                </select>
              </div>
            </div>

            <div>
              <label class="block font-semibold text-slate-700 mb-1">Foundational Knowledge Document Title</label>
              <input id="obAdvDocTitle" type="text" value="Lock Invariants and Sweeper Policies" class="w-full bg-slate-50 border border-slate-300 rounded-lg px-3.5 py-2 text-slate-900 focus:outline-none focus:border-emerald-500 focus:bg-white">
            </div>

            <div>
              <label class="block font-semibold text-slate-700 mb-1">Knowledge Content & Standards</label>
              <textarea id="obAdvDocContent" rows="3" class="w-full bg-slate-50 border border-slate-300 rounded-lg px-3.5 py-2 text-slate-900 focus:outline-none focus:border-emerald-500 focus:bg-white">Kanban holds primary lock. Daemons must emit 15s heartbeats. Expired locks after 60s MUST reap to DLQ. War rooms are ephemeral subroutines.</textarea>
            </div>
          </div>

          <div class="flex justify-between pt-4 border-t border-slate-200">
            <button onclick="goToWizardStep(3)" class="text-slate-600 hover:text-slate-900 px-4 py-2 text-xs font-medium">&larr; Back</button>
            <button onclick="goToWizardStep(5)" class="bg-emerald-600 hover:bg-emerald-700 text-white px-5 py-2 rounded-lg text-xs font-semibold shadow-sm transition flex items-center space-x-1.5">
              <span>Next: First Kanban Task</span>
              <span>&rarr;</span>
            </button>
          </div>
        </div>

        <!-- STEP 5: First Kanban Mission -->
        <div id="wizardStep5" class="hidden space-y-6">
          <div>
            <h2 class="text-lg font-bold text-slate-900">Step 5: Define First Mission / Kanban Task</h2>
            <p class="text-xs text-slate-500 mt-0.5">Kickstart your organization with an initial task added to your Kanban board.</p>
          </div>

          <div class="space-y-4 text-xs">
            <div>
              <label class="block font-semibold text-slate-700 mb-1">Task Title</label>
              <input id="obTaskTitle" type="text" value="Establish Host Daemon WebSocket Handshake & Telemetry" class="w-full bg-slate-50 border border-slate-300 rounded-lg px-3.5 py-2.5 text-slate-900 text-sm focus:outline-none focus:border-emerald-500 focus:bg-white">
            </div>

            <div>
              <label class="block font-semibold text-slate-700 mb-1">Description & Acceptance Criteria</label>
              <textarea id="obTaskDesc" rows="3" class="w-full bg-slate-50 border border-slate-300 rounded-lg px-3.5 py-2 text-slate-900 focus:outline-none focus:border-emerald-500 focus:bg-white">Start the CLI companion daemon, establish connection to /ws/daemon/{daemon_id}, stream stdout telemetry chunks, and verify 15s heartbeats.</textarea>
            </div>

            <div>
              <label class="block font-semibold text-slate-700 mb-1">Priority</label>
              <select id="obTaskPriority" class="w-full bg-slate-50 border border-slate-300 rounded-lg px-3 py-2 text-slate-900 focus:outline-none focus:border-emerald-500">
                <option value="LOW">LOW</option>
                <option value="MEDIUM">MEDIUM</option>
                <option value="HIGH" selected>HIGH</option>
                <option value="URGENT">URGENT</option>
              </select>
            </div>
          </div>

          <div class="flex justify-between pt-4 border-t border-slate-200">
            <button onclick="goToWizardStep(4)" class="text-slate-600 hover:text-slate-900 px-4 py-2 text-xs font-medium">&larr; Back</button>
            <button onclick="goToWizardStep(6)" class="bg-emerald-600 hover:bg-emerald-700 text-white px-5 py-2 rounded-lg text-xs font-semibold shadow-sm transition flex items-center space-x-1.5">
              <span>Review & Launch</span>
              <span>&rarr;</span>
            </button>
          </div>
        </div>

        <!-- STEP 6: Summary & Launch -->
        <div id="wizardStep6" class="hidden space-y-6">
          <div>
            <h2 class="text-lg font-bold text-slate-900">Step 6: Ready to Launch Your Autonomous Company</h2>
            <p class="text-xs text-slate-500 mt-0.5">Review your configuration before saving directly to the database.</p>
          </div>

          <div class="bg-slate-50 rounded-xl p-5 border border-slate-200 space-y-3.5 text-xs">
            <div class="flex justify-between border-b border-slate-200 pb-2">
              <span class="text-slate-500">Company:</span>
              <span id="sumOrg" class="font-bold text-slate-900">-</span>
            </div>
            <div class="flex justify-between border-b border-slate-200 pb-2">
              <span class="text-slate-500">Custom LLM Provider:</span>
              <span id="sumLlm" class="font-mono font-semibold text-indigo-700">-</span>
            </div>
            <div class="flex justify-between border-b border-slate-200 pb-2">
              <span class="text-slate-500">Lead Orchestrator (CEO):</span>
              <span id="sumAgent" class="font-bold text-slate-900">-</span>
            </div>
            <div class="flex justify-between border-b border-slate-200 pb-2">
              <span class="text-slate-500">Board Advisor:</span>
              <span id="sumAdvisor" class="font-bold text-purple-700">-</span>
            </div>
            <div class="flex justify-between">
              <span class="text-slate-500">Initial Task:</span>
              <span id="sumTask" class="font-medium text-slate-800">-</span>
            </div>
          </div>

          <div class="flex justify-between pt-4 border-t border-slate-200">
            <button onclick="goToWizardStep(5)" class="text-slate-600 hover:text-slate-900 px-4 py-2 text-xs font-medium">&larr; Back</button>
            <button onclick="submitOnboardingComplete()" id="btnLaunchOrg" class="bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-700 hover:to-teal-700 text-white px-7 py-2.5 rounded-lg text-xs font-bold shadow-md transition flex items-center space-x-2">
              <span>🚀</span>
              <span>Launch Organization & Save to Database</span>
            </button>
          </div>
        </div>

      </div>
    </div>
  </section>

  <!-- MAIN DASHBOARD CONTENT (Displays Only Actual Real Data from Database) -->
  <main id="dashboardSection" class="flex-1 p-6 max-w-7xl w-full mx-auto space-y-6">

    <!-- Company Header Banner (Actual Data from Database) -->
    <div class="bg-white border border-slate-200 rounded-xl p-5 shadow-xs flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
      <div class="flex items-start space-x-3.5">
        <div class="p-2.5 bg-emerald-50 rounded-lg border border-emerald-200 text-emerald-700 mt-0.5">
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"/></svg>
        </div>
        <div>
          <div class="flex items-center space-x-2.5">
            <h1 id="dashCompanyName" class="text-lg font-black text-slate-900 tracking-tight">Organization</h1>
            <span id="dashProjectTag" class="text-[10px] font-mono font-semibold bg-slate-100 text-slate-700 px-2 py-0.5 rounded border border-slate-200"></span>
          </div>
          <p id="dashCompanyMission" class="text-xs text-slate-600 mt-1 max-w-3xl leading-relaxed italic"></p>
        </div>
      </div>

      <div class="flex items-center space-x-2 text-xs font-mono text-slate-600 bg-slate-50 px-3.5 py-2 rounded-lg border border-slate-200 shrink-0">
        <span class="text-slate-400">Daemon:</span>
        <code class="text-emerald-700 font-semibold">python -m packages.daemon.folks_daemon.main</code>
      </div>
    </div>

    <!-- Metrics Cards Grid (Real Counts from Database) -->
    <div class="grid grid-cols-2 md:grid-cols-6 gap-3.5">
      <div class="bg-white border border-slate-200 rounded-xl p-4 shadow-xs flex flex-col justify-between">
        <span class="text-[11px] font-bold text-slate-500 uppercase tracking-wider">Agents</span>
        <div class="mt-2 flex items-baseline justify-between">
          <span id="metricAgents" class="text-2xl font-black text-slate-900 font-mono">-</span>
          <span class="text-[10px] text-emerald-700 bg-emerald-50 border border-emerald-200 px-1.5 py-0.5 rounded font-medium">In DB</span>
        </div>
      </div>

      <div class="bg-white border border-slate-200 rounded-xl p-4 shadow-xs flex flex-col justify-between">
        <span class="text-[11px] font-bold text-slate-500 uppercase tracking-wider">Backlog / Todo</span>
        <div class="mt-2 flex items-baseline justify-between">
          <span id="metricBacklog" class="text-2xl font-black text-slate-900 font-mono">-</span>
          <span class="text-[10px] text-slate-600 bg-slate-100 px-1.5 py-0.5 rounded font-medium">Queue</span>
        </div>
      </div>

      <div class="bg-white border border-blue-200 rounded-xl p-4 shadow-xs flex flex-col justify-between">
        <span class="text-[11px] font-bold text-blue-700 uppercase tracking-wider">In Progress</span>
        <div class="mt-2 flex items-baseline justify-between">
          <span id="metricInProgress" class="text-2xl font-black text-blue-800 font-mono">-</span>
          <span class="text-[10px] text-blue-700 bg-blue-50 border border-blue-200 px-1.5 py-0.5 rounded font-medium">Locked</span>
        </div>
      </div>

      <div class="bg-white border border-amber-200 rounded-xl p-4 shadow-xs flex flex-col justify-between">
        <span class="text-[11px] font-bold text-amber-700 uppercase tracking-wider">Consultation</span>
        <div class="mt-2 flex items-baseline justify-between">
          <span id="metricConsultation" class="text-2xl font-black text-amber-800 font-mono">-</span>
          <span class="text-[10px] text-amber-700 bg-amber-50 border border-amber-200 px-1.5 py-0.5 rounded font-medium">Frozen</span>
        </div>
      </div>

      <div class="bg-white border border-red-200 rounded-xl p-4 shadow-xs flex flex-col justify-between">
        <span class="text-[11px] font-bold text-red-700 uppercase tracking-wider">DLQ</span>
        <div class="mt-2 flex items-baseline justify-between">
          <span id="metricDLQ" class="text-2xl font-black text-red-700 font-mono">-</span>
          <span class="text-[10px] text-red-700 bg-red-50 border border-red-200 px-1.5 py-0.5 rounded font-medium">Reaped</span>
        </div>
      </div>

      <div class="bg-white border border-purple-200 rounded-xl p-4 shadow-xs flex flex-col justify-between">
        <span class="text-[11px] font-bold text-purple-700 uppercase tracking-wider">Advisors</span>
        <div class="mt-2 flex items-baseline justify-between">
          <span id="metricAdvisors" class="text-2xl font-black text-purple-800 font-mono">-</span>
          <span class="text-[10px] text-purple-700 bg-purple-50 border border-purple-200 px-1.5 py-0.5 rounded font-medium">Reasoning</span>
        </div>
      </div>
    </div>

    <!-- Navigation Tabs -->
    <div class="flex items-center space-x-1 border-b border-slate-200 pb-px">
      <button onclick="switchTab('kanban')" id="tabKanban" class="tab-btn px-4 py-2.5 text-xs font-bold text-emerald-700 border-b-2 border-emerald-600 transition flex items-center space-x-2">
        <span>📋</span>
        <span>Kanban Board</span>
      </button>
      <button onclick="switchTab('advisors')" id="tabAdvisors" class="tab-btn px-4 py-2.5 text-xs font-semibold text-slate-500 hover:text-slate-900 border-b-2 border-transparent transition flex items-center space-x-2">
        <span>🧠</span>
        <span>Board of Advisors</span>
      </button>
      <button onclick="switchTab('copilot')" id="tabCopilot" class="tab-btn px-4 py-2.5 text-xs font-semibold text-slate-500 hover:text-slate-900 border-b-2 border-transparent transition flex items-center space-x-2">
        <span>💬</span>
        <span>Owner Copilot (Typed API)</span>
      </button>
      <button onclick="switchTab('telemetry')" id="tabTelemetry" class="tab-btn px-4 py-2.5 text-xs font-semibold text-slate-500 hover:text-slate-900 border-b-2 border-transparent transition flex items-center space-x-2">
        <span>📟</span>
        <span>Live Telemetry Terminal</span>
      </button>
    </div>

    <!-- TAB 1: KANBAN BOARD (Pure Database Records) -->
    <div id="viewKanban" class="space-y-4">
      <div class="grid grid-cols-1 md:grid-cols-5 gap-4">
        
        <!-- Backlog / Todo -->
        <div class="bg-slate-100/60 border border-slate-200 rounded-xl flex flex-col min-h-[460px]">
          <div class="p-3 border-b border-slate-200 bg-white/70 rounded-t-xl flex items-center justify-between">
            <span class="text-xs font-bold text-slate-700 flex items-center space-x-1.5">
              <span class="w-2 h-2 rounded-full bg-slate-400"></span>
              <span>BACKLOG / TODO</span>
            </span>
            <span id="colCountBacklog" class="text-xs font-mono font-bold text-slate-600 bg-slate-200 px-2 py-0.5 rounded">0</span>
          </div>
          <div id="cardsBacklog" class="p-2.5 space-y-2.5 flex-1 overflow-y-auto max-h-[600px] custom-scroll"></div>
        </div>

        <!-- In Progress (Locked) -->
        <div class="bg-blue-50/30 border border-blue-200/80 rounded-xl flex flex-col min-h-[460px]">
          <div class="p-3 border-b border-blue-200/80 bg-blue-50/60 rounded-t-xl flex items-center justify-between">
            <span class="text-xs font-bold text-blue-800 flex items-center space-x-1.5">
              <span class="w-2 h-2 rounded-full bg-blue-500 pulse-dot"></span>
              <span>IN PROGRESS (LOCKED)</span>
            </span>
            <span id="colCountInProgress" class="text-xs font-mono font-bold text-blue-800 bg-blue-100 px-2 py-0.5 rounded">0</span>
          </div>
          <div id="cardsInProgress" class="p-2.5 space-y-2.5 flex-1 overflow-y-auto max-h-[600px] custom-scroll"></div>
        </div>

        <!-- Paused Consultation -->
        <div class="bg-amber-50/30 border border-amber-200/80 rounded-xl flex flex-col min-h-[460px]">
          <div class="p-3 border-b border-amber-200/80 bg-amber-50/60 rounded-t-xl flex items-center justify-between">
            <span class="text-xs font-bold text-amber-800 flex items-center space-x-1.5">
              <span class="w-2 h-2 rounded-full bg-amber-500"></span>
              <span>PAUSED CONSULTATION</span>
            </span>
            <span id="colCountPaused" class="text-xs font-mono font-bold text-amber-800 bg-amber-100 px-2 py-0.5 rounded">0</span>
          </div>
          <div id="cardsPaused" class="p-2.5 space-y-2.5 flex-1 overflow-y-auto max-h-[600px] custom-scroll"></div>
        </div>

        <!-- Completed -->
        <div class="bg-emerald-50/30 border border-emerald-200/80 rounded-xl flex flex-col min-h-[460px]">
          <div class="p-3 border-b border-emerald-200/80 bg-emerald-50/60 rounded-t-xl flex items-center justify-between">
            <span class="text-xs font-bold text-emerald-800 flex items-center space-x-1.5">
              <span class="w-2 h-2 rounded-full bg-emerald-600"></span>
              <span>COMPLETED</span>
            </span>
            <span id="colCountCompleted" class="text-xs font-mono font-bold text-emerald-800 bg-emerald-100 px-2 py-0.5 rounded">0</span>
          </div>
          <div id="cardsCompleted" class="p-2.5 space-y-2.5 flex-1 overflow-y-auto max-h-[600px] custom-scroll"></div>
        </div>

        <!-- Dead Letter Queue (DLQ) -->
        <div class="bg-red-50/30 border border-red-200/80 rounded-xl flex flex-col min-h-[460px]">
          <div class="p-3 border-b border-red-200/80 bg-red-50/60 rounded-t-xl flex items-center justify-between">
            <span class="text-xs font-bold text-red-700 flex items-center space-x-1.5">
              <span class="w-2 h-2 rounded-full bg-red-500 pulse-dot"></span>
              <span>DEAD-LETTER QUEUE</span>
            </span>
            <span id="colCountDLQ" class="text-xs font-mono font-bold text-red-700 bg-red-100 px-2 py-0.5 rounded">0</span>
          </div>
          <div id="cardsDLQ" class="p-2.5 space-y-2.5 flex-1 overflow-y-auto max-h-[600px] custom-scroll"></div>
        </div>
      </div>
    </div>

    <!-- TAB 2: BOARD OF ADVISORS (Pure Database Records) -->
    <div id="viewAdvisors" class="hidden space-y-6">
      <div class="flex items-center justify-between">
        <div>
          <h2 class="text-base font-bold text-slate-900">Board of Strategic Advisors</h2>
          <p class="text-xs text-slate-500">Domain authorities loaded with dense knowledge bases and intense reasoning models.</p>
        </div>
        <button onclick="openAdvisoryModal()" class="text-xs bg-purple-600 hover:bg-purple-700 text-white px-3.5 py-2 rounded-lg font-semibold shadow-xs transition flex items-center space-x-1.5">
          <span>🧠</span>
          <span>Consult Advisor</span>
        </button>
      </div>

      <div id="advisorsList" class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <!-- Dynamically rendered from DB -->
      </div>
    </div>

    <!-- TAB 3: OWNER COPILOT (Typed API) -->
    <div id="viewCopilot" class="hidden space-y-4">
      <div class="bg-white border border-slate-200 rounded-xl p-5 shadow-xs space-y-4">
        <div class="flex items-center justify-between">
          <div class="flex items-center space-x-3">
            <div class="w-9 h-9 rounded-lg bg-emerald-50 border border-emerald-200 flex items-center justify-center text-emerald-700 font-bold">
              ⚡
            </div>
            <div>
              <h2 class="text-sm font-bold text-slate-900">Owner Copilot Interface</h2>
              <p class="text-xs text-slate-500">Intelligent UI navigator and diagnostic log interpreter. Strict zero direct SQL boundary.</p>
            </div>
          </div>
          <span class="text-xs font-mono text-emerald-700 bg-emerald-50 border border-emerald-200 px-2.5 py-1 rounded-md font-semibold">Boundary: Enforced</span>
        </div>

        <div class="space-y-2">
          <div class="flex items-center space-x-2">
            <input id="copilotQueryInput" type="text" placeholder="e.g. 'Where do I configure agent token limits?' or 'Explain recent DLQ failures'" class="flex-1 bg-slate-50 border border-slate-300 rounded-lg px-3.5 py-2 text-xs text-slate-900 placeholder-slate-400 focus:outline-none focus:border-emerald-500 focus:bg-white" onkeydown="if(event.key === 'Enter') submitCopilotQuery()">
            <button onclick="submitCopilotQuery()" id="copilotSendBtn" class="bg-emerald-600 hover:bg-emerald-700 text-white px-4 py-2 rounded-lg text-xs font-semibold shadow-xs transition">Send</button>
          </div>
          <div class="flex flex-wrap gap-2 text-[11px] text-slate-500">
            <span class="text-slate-400">Suggested queries:</span>
            <button onclick="setCopilotQuery('Where do I configure agent token limits?')" class="bg-slate-100 hover:bg-slate-200 px-2 py-0.5 rounded text-slate-700">"Where do I configure token limits?"</button>
            <button onclick="setCopilotQuery('Explain why recent tasks failed or got swept to DLQ')" class="bg-slate-100 hover:bg-slate-200 px-2 py-0.5 rounded text-slate-700">"Explain why task swept to DLQ"</button>
            <button onclick="setCopilotQuery('List active agents and their capabilities')" class="bg-slate-100 hover:bg-slate-200 px-2 py-0.5 rounded text-slate-700">"List active agents"</button>
          </div>
        </div>

        <div id="copilotResponseBox" class="hidden bg-slate-50 border border-slate-200 rounded-lg p-4 space-y-3 font-mono text-xs">
          <div class="flex items-center justify-between text-slate-500 border-b border-slate-200 pb-2">
            <span class="text-emerald-700 font-bold flex items-center space-x-1.5">
              <span>🤖</span>
              <span>Copilot Response (Typed & Validated)</span>
            </span>
            <span id="copilotIntentBadge" class="text-[10px] bg-slate-200 px-2 py-0.5 rounded text-slate-700 font-mono font-semibold">INTENT</span>
          </div>
          <p id="copilotMessageText" class="text-slate-800 font-sans leading-relaxed"></p>
          <div id="copilotUiNavSection" class="hidden bg-white border border-slate-200 rounded p-3 text-[11px] space-y-1">
            <span class="text-slate-700 font-bold block">UI Navigation Route:</span>
            <div id="copilotUiNavContent" class="text-indigo-600"></div>
          </div>
          <div id="copilotDiagnosticsSection" class="hidden bg-white border border-slate-200 rounded p-3 text-[11px] space-y-1">
            <span class="text-amber-700 font-bold block">Diagnostic Log Summary:</span>
            <div id="copilotDiagnosticsContent" class="text-slate-700"></div>
          </div>
        </div>
      </div>
    </div>

    <!-- TAB 4: LIVE TELEMETRY TERMINAL -->
    <div id="viewTelemetry" class="space-y-3">
      <div class="bg-white border border-slate-200 rounded-xl p-4 shadow-xs flex flex-col h-[500px]">
        <div class="flex items-center justify-between pb-3 border-b border-slate-200">
          <div class="flex items-center space-x-2">
            <span class="w-3 h-3 rounded-full bg-emerald-500"></span>
            <span class="w-3 h-3 rounded-full bg-amber-500"></span>
            <span class="w-3 h-3 rounded-full bg-red-500"></span>
            <span class="text-xs font-mono font-bold text-slate-700 ml-2">LIVE DAEMON TELEMETRY // /ws/cockpit</span>
          </div>
          <div class="flex items-center space-x-2">
            <button onclick="clearTerminal()" class="text-[11px] bg-slate-100 hover:bg-slate-200 text-slate-700 px-2.5 py-1 rounded font-mono transition">Clear</button>
            <button onclick="toggleTerminalAutoscroll()" id="btnAutoscroll" class="text-[11px] bg-emerald-50 text-emerald-700 border border-emerald-200 px-2.5 py-1 rounded font-mono transition">Autoscroll: ON</button>
          </div>
        </div>

        <div id="terminalBody" class="flex-1 bg-slate-900 p-3.5 font-mono text-xs overflow-y-auto space-y-1 custom-scroll rounded-lg mt-3 text-slate-300">
          <div class="text-slate-500">[SYSTEM] Terminal initialized. Waiting for daemon heartbeats and events...</div>
        </div>
      </div>
    </div>

  </main>

  <!-- MODAL: Create New Task -->
  <div id="newTaskModal" class="hidden fixed inset-0 z-50 bg-slate-900/40 backdrop-blur-xs flex items-center justify-center p-4">
    <div class="bg-white border border-slate-200 rounded-2xl max-w-lg w-full p-6 space-y-4 shadow-2xl">
      <div class="flex items-center justify-between border-b border-slate-200 pb-3">
        <h3 class="text-sm font-bold text-slate-900 flex items-center space-x-2">
          <span>➕</span>
          <span>Create New Kanban Task</span>
        </h3>
        <button onclick="closeNewTaskModal()" class="text-slate-400 hover:text-slate-700 text-lg leading-none">&times;</button>
      </div>
      <div class="space-y-3 text-xs">
        <div>
          <label class="block font-semibold text-slate-700 mb-1">Task Title</label>
          <input id="modalTaskTitle" type="text" placeholder="e.g. Implement TLS socket verification" class="w-full bg-slate-50 border border-slate-300 rounded-lg px-3 py-2 text-slate-900 focus:outline-none focus:border-emerald-500 focus:bg-white">
        </div>
        <div>
          <label class="block font-semibold text-slate-700 mb-1">Description</label>
          <textarea id="modalTaskDesc" rows="3" placeholder="Execution requirements and invariants..." class="w-full bg-slate-50 border border-slate-300 rounded-lg px-3 py-2 text-slate-900 focus:outline-none focus:border-emerald-500 focus:bg-white"></textarea>
        </div>
        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="block font-semibold text-slate-700 mb-1">Priority</label>
            <select id="modalTaskPriority" class="w-full bg-slate-50 border border-slate-300 rounded-lg px-3 py-2 text-slate-900 focus:outline-none focus:border-emerald-500">
              <option value="LOW">LOW</option>
              <option value="MEDIUM" selected>MEDIUM</option>
              <option value="HIGH">HIGH</option>
              <option value="URGENT">URGENT</option>
            </select>
          </div>
          <div>
            <label class="block font-semibold text-slate-700 mb-1">Project Tag</label>
            <input id="modalTaskTag" type="text" value="folks_core" class="w-full bg-slate-50 border border-slate-300 rounded-lg px-3 py-2 text-slate-900 font-mono focus:outline-none focus:border-emerald-500">
          </div>
        </div>
      </div>
      <div class="flex items-center justify-end space-x-2 pt-3 border-t border-slate-200">
        <button onclick="closeNewTaskModal()" class="px-3.5 py-1.5 text-xs text-slate-600 hover:text-slate-900">Cancel</button>
        <button onclick="submitNewTask()" class="bg-emerald-600 hover:bg-emerald-700 text-white px-4 py-1.5 rounded-lg text-xs font-semibold shadow-xs transition">Create Task</button>
      </div>
    </div>
  </div>

  <!-- MODAL: Advisory Session -->
  <div id="advisoryModal" class="hidden fixed inset-0 z-50 bg-slate-900/40 backdrop-blur-xs flex items-center justify-center p-4">
    <div class="bg-white border border-purple-200 rounded-2xl max-w-xl w-full p-6 space-y-4 shadow-2xl">
      <div class="flex items-center justify-between border-b border-slate-200 pb-3">
        <div class="flex items-center space-x-2">
          <span class="text-xl">🧠</span>
          <h3 class="text-sm font-bold text-slate-900">Board of Advisors Consultation</h3>
        </div>
        <button onclick="closeAdvisoryModal()" class="text-slate-400 hover:text-slate-700 text-lg leading-none">&times;</button>
      </div>
      <div class="space-y-3 text-xs">
        <div>
          <label class="block font-semibold text-slate-700 mb-1">Select Advisor</label>
          <select id="modalAdvisorSelect" class="w-full bg-slate-50 border border-slate-300 rounded-lg px-3 py-2 text-slate-900 focus:outline-none focus:border-purple-500"></select>
        </div>
        <div>
          <label class="block font-semibold text-slate-700 mb-1">Technical Impasse / Review Topic</label>
          <input id="modalAdvisoryTopic" type="text" placeholder="e.g. Distributed Lock TTL Under Jitter" class="w-full bg-slate-50 border border-slate-300 rounded-lg px-3 py-2 text-slate-900 focus:outline-none focus:border-purple-500 focus:bg-white">
        </div>
        <div>
          <label class="block font-semibold text-slate-700 mb-1">Inquiry Details</label>
          <textarea id="modalAdvisoryInquiry" rows="4" placeholder="Detail the impasse, tradeoffs, and evidence..." class="w-full bg-slate-50 border border-slate-300 rounded-lg px-3 py-2 text-slate-900 focus:outline-none focus:border-purple-500 focus:bg-white"></textarea>
        </div>
      </div>
      <div class="flex items-center justify-end space-x-2 pt-3 border-t border-slate-200">
        <button onclick="closeAdvisoryModal()" class="px-3.5 py-1.5 text-xs text-slate-600 hover:text-slate-900">Cancel</button>
        <button onclick="submitAdvisorySession()" id="modalAdvisorSubmitBtn" class="bg-purple-600 hover:bg-purple-700 text-white px-4 py-1.5 rounded-lg text-xs font-semibold shadow-xs transition">Run Deep Reasoning</button>
      </div>
    </div>
  </div>

  <script>
    let autoscroll = true;
    let ws = null;
    let cachedAdvisors = [];
    let currentStep = 1;
    let selectedProviderPreset = 'custom';

    // 1. Initial State Check
    window.addEventListener('DOMContentLoaded', async () => {
      initWebSocket();
      await checkOnboardingState();
    });

    async function checkOnboardingState() {
      try {
        const res = await fetch('/api/v1/onboarding/status');
        if (res.ok) {
          const status = await res.json();
          if (!status.onboarding_completed) {
            launchOnboardingWizard(false);
          } else {
            showDashboard(status);
          }
        } else {
          launchOnboardingWizard(false);
        }
      } catch (err) {
        console.error('Failed to load status:', err);
        launchOnboardingWizard(false);
      }
    }

    // 2. Wizard Stepper Navigation
    function launchOnboardingWizard(isManualReconfigure) {
      document.getElementById('dashboardSection').classList.add('hidden');
      document.getElementById('onboardingSection').classList.remove('hidden');
      goToWizardStep(1);
    }

    function showDashboard(statusData) {
      document.getElementById('onboardingSection').classList.add('hidden');
      document.getElementById('dashboardSection').classList.remove('hidden');

      if (statusData && statusData.company_name) {
        document.getElementById('dashCompanyName').innerText = statusData.company_name;
        document.getElementById('dashProjectTag').innerText = statusData.project_tag || 'folks_core';
        document.getElementById('dashCompanyMission').innerText = `"${statusData.company_mission || 'Autonomous Multi-Agent Engineering Organization'}"`;
        document.getElementById('headerCompanyBadge').innerText = statusData.company_name;
        document.getElementById('headerCompanyBadge').classList.remove('hidden');

        if (statusData.llm_provider) {
          const p = statusData.llm_provider;
          document.getElementById('llmActiveBadge').classList.remove('hidden');
          document.getElementById('llmActiveBadge').classList.add('flex');
          document.getElementById('llmActiveText').innerText = `${p.provider_name || 'Custom LLM'} (${p.default_model})`;
        }
      }

      refreshActualData();
      fetchAdvisors();
    }

    function goToWizardStep(step) {
      currentStep = step;
      for (let i = 1; i <= 6; i++) {
        const el = document.getElementById('wizardStep' + i);
        const dot = document.getElementById('stepDot' + i);
        if (i === step) {
          el.classList.remove('hidden');
          dot.className = 'step-dot z-10 w-8 h-8 rounded-full bg-white text-emerald-700 font-bold flex items-center justify-center text-xs shadow-md ring-2 ring-emerald-300';
        } else if (i < step) {
          el.classList.add('hidden');
          dot.className = 'step-dot z-10 w-8 h-8 rounded-full bg-emerald-300 text-emerald-900 font-bold flex items-center justify-center text-xs';
        } else {
          el.classList.add('hidden');
          dot.className = 'step-dot z-10 w-8 h-8 rounded-full bg-white/40 text-white font-bold flex items-center justify-center text-xs';
        }
      }

      if (step === 6) {
        populateSummary();
      }
    }

    // Provider Presets
    function selectProviderPreset(type) {
      selectedProviderPreset = type;
      document.querySelectorAll('.provider-preset-card').forEach(c => {
        c.className = 'provider-preset-card border border-slate-200 bg-white hover:border-slate-300 rounded-xl p-3 cursor-pointer transition text-xs';
      });
      const activeCard = document.getElementById('presetCard_' + type);
      if (activeCard) {
        activeCard.className = 'provider-preset-card border-2 border-emerald-600 bg-emerald-50/40 rounded-xl p-3 cursor-pointer transition text-xs';
      }

      const nameInput = document.getElementById('obLlmName');
      const baseInput = document.getElementById('obLlmBaseUrl');
      const defModelInput = document.getElementById('obLlmDefaultModel');
      const advModelInput = document.getElementById('obLlmAdvisorModel');

      if (type === 'ollama') {
        nameInput.value = 'Local Ollama Instance';
        baseInput.value = 'http://localhost:11434/v1';
        defModelInput.value = 'llama3.3:70b';
        advModelInput.value = 'deepseek-r1';
      } else if (type === 'anthropic') {
        nameInput.value = 'Anthropic Claude';
        baseInput.value = 'https://api.anthropic.com';
        defModelInput.value = 'claude-3-7-sonnet';
        advModelInput.value = 'claude-3-7-sonnet-thought';
      } else if (type === 'openai') {
        nameInput.value = 'OpenAI Gateway';
        baseInput.value = 'https://api.openai.com/v1';
        defModelInput.value = 'gpt-4o';
        advModelInput.value = 'o3-mini';
      } else if (type === 'openrouter') {
        nameInput.value = 'OpenRouter Gateway';
        baseInput.value = 'https://openrouter.ai/api/v1';
        defModelInput.value = 'anthropic/claude-3.7-sonnet';
        advModelInput.value = 'deepseek/deepseek-r1';
      } else if (type === 'gemini') {
        nameInput.value = 'Google Gemini Direct';
        baseInput.value = 'https://generativelanguage.googleapis.com/v1beta';
        defModelInput.value = 'gemini-2.0-flash';
        advModelInput.value = 'gemini-2.0-pro-exp';
      } else {
        nameInput.value = 'Custom OpenAI-compatible Gateway';
        baseInput.value = 'http://localhost:8000/v1';
        defModelInput.value = 'custom-agent-model';
        advModelInput.value = 'custom-reasoner-model';
      }
    }

    function toggleApiKeyVisibility() {
      const inp = document.getElementById('obLlmApiKey');
      inp.type = inp.type === 'password' ? 'text' : 'password';
    }

    // Live LLM Connection Test
    async function testLlmConnection() {
      const btn = document.getElementById('btnTestLlm');
      const box = document.getElementById('llmTestResult');
      btn.innerText = 'Testing Connection...';
      btn.disabled = true;

      const payload = {
        provider_type: selectedProviderPreset,
        provider_name: document.getElementById('obLlmName').value,
        base_url: document.getElementById('obLlmBaseUrl').value || null,
        api_key: document.getElementById('obLlmApiKey').value || null,
        default_model: document.getElementById('obLlmDefaultModel').value,
        advisor_reasoning_model: document.getElementById('obLlmAdvisorModel').value
      };

      try {
        const res = await fetch('/api/v1/onboarding/test-llm', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
        const data = await res.json();
        box.classList.remove('hidden');

        if (data.success) {
          box.className = 'p-3 rounded-lg border border-emerald-200 bg-emerald-50 text-emerald-800 text-xs font-mono';
          box.innerHTML = `<strong>Connected (${data.latency_ms}ms):</strong> ${escapeHtml(data.message)}`;
        } else {
          box.className = 'p-3 rounded-lg border border-amber-200 bg-amber-50 text-amber-800 text-xs font-mono';
          box.innerHTML = `<strong>Warning:</strong> ${escapeHtml(data.message)}`;
        }
      } catch (err) {
        box.classList.remove('hidden');
        box.className = 'p-3 rounded-lg border border-red-200 bg-red-50 text-red-800 text-xs font-mono';
        box.innerHTML = `<strong>Error:</strong> Failed to reach test endpoint.`;
      } finally {
        btn.innerText = '⚡ Test Endpoint Connection';
        btn.disabled = false;
      }
    }

    function populateSummary() {
      document.getElementById('sumOrg').innerText = `${document.getElementById('obOrgName').value} (${document.getElementById('obOrgTag').value})`;
      document.getElementById('sumLlm').innerText = `${document.getElementById('obLlmName').value} | Model: ${document.getElementById('obLlmDefaultModel').value}`;
      document.getElementById('sumAgent').innerText = `${document.getElementById('obAgentName').value} (${document.getElementById('obAgentRole').value})`;
      document.getElementById('sumAdvisor').innerText = `${document.getElementById('obAdvName').value} (${document.getElementById('obAdvDomain').value})`;
      document.getElementById('sumTask').innerText = document.getElementById('obTaskTitle').value;
    }

    // Submit Onboarding to Database
    async function submitOnboardingComplete() {
      const btn = document.getElementById('btnLaunchOrg');
      btn.innerText = 'Saving to Database...';
      btn.disabled = true;

      const payload = {
        organization: {
          name: document.getElementById('obOrgName').value.trim(),
          mission: document.getElementById('obOrgMission').value.trim(),
          project_tag: document.getElementById('obOrgTag').value.trim()
        },
        llm_provider: {
          provider_type: selectedProviderPreset,
          provider_name: document.getElementById('obLlmName').value.trim(),
          base_url: document.getElementById('obLlmBaseUrl').value.trim() || null,
          api_key: document.getElementById('obLlmApiKey').value.trim() || null,
          default_model: document.getElementById('obLlmDefaultModel').value.trim(),
          advisor_reasoning_model: document.getElementById('obLlmAdvisorModel').value.trim(),
          temperature: 0.7,
          max_tokens: 4096
        },
        lead_agent: {
          name: document.getElementById('obAgentName').value.trim(),
          role: document.getElementById('obAgentRole').value.trim(),
          backstory: document.getElementById('obAgentBackstory').value.trim(),
          adapter_type: document.getElementById('obAgentAdapter').value,
          monthly_budget_usd: parseFloat(document.getElementById('obAgentBudget').value) || 100.0
        },
        advisor: {
          name: document.getElementById('obAdvName').value.trim(),
          domain: document.getElementById('obAdvDomain').value,
          knowledge_title: document.getElementById('obAdvDocTitle').value.trim(),
          knowledge_content: document.getElementById('obAdvDocContent').value.trim()
        },
        initial_task: {
          title: document.getElementById('obTaskTitle').value.trim(),
          description: document.getElementById('obTaskDesc').value.trim(),
          priority: document.getElementById('obTaskPriority').value
        }
      };

      try {
        const res = await fetch('/api/v1/onboarding/complete', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });

        if (res.ok) {
          const statusRes = await fetch('/api/v1/onboarding/status');
          const statusData = await statusRes.json();
          showDashboard(statusData);
          logToTerminal(`[ONBOARDING] Company '${payload.organization.name}' successfully initialized in database.`, 'emerald');
        } else {
          const err = await res.json();
          alert('Onboarding failed: ' + (err.detail || 'Server error'));
        }
      } catch (err) {
        alert('Network error completing onboarding');
      } finally {
        btn.innerText = '🚀 Launch Organization & Save to Database';
        btn.disabled = false;
      }
    }

    async function resetOnboardingFresh() {
      if (!confirm('Reset onboarding status to test the initial setup wizard again? (Your database records remain intact)')) return;
      try {
        await fetch('/api/v1/onboarding/reset', { method: 'POST' });
        launchOnboardingWizard(false);
      } catch (e) {
        console.error(e);
      }
    }

    // 3. Tab Navigation
    function switchTab(tabId) {
      ['kanban', 'advisors', 'copilot', 'telemetry'].forEach(t => {
        const view = document.getElementById('view' + t.charAt(0).toUpperCase() + t.slice(1));
        const btn = document.getElementById('tab' + t.charAt(0).toUpperCase() + t.slice(1));
        if (t === tabId) {
          view.classList.remove('hidden');
          btn.className = 'tab-btn px-4 py-2.5 text-xs font-bold text-emerald-700 border-b-2 border-emerald-600 transition flex items-center space-x-2';
        } else {
          view.classList.add('hidden');
          btn.className = 'tab-btn px-4 py-2.5 text-xs font-semibold text-slate-500 hover:text-slate-900 border-b-2 border-transparent transition flex items-center space-x-2';
        }
      });
      if (tabId === 'advisors') fetchAdvisors();
    }

    // 4. Modals
    function openNewTaskModal() { document.getElementById('newTaskModal').classList.remove('hidden'); }
    function closeNewTaskModal() { document.getElementById('newTaskModal').classList.add('hidden'); }
    function openAdvisoryModal() { 
      document.getElementById('advisoryModal').classList.remove('hidden'); 
      const sel = document.getElementById('modalAdvisorSelect');
      sel.innerHTML = cachedAdvisors.map(a => `<option value="${a.id}">${a.name} (${a.domain} - ${a.reasoning_model})</option>`).join('');
    }
    function closeAdvisoryModal() { document.getElementById('advisoryModal').classList.add('hidden'); }

    // 5. Real Database Data Rendering (Zero Dummy Data)
    async function refreshActualData() {
      try {
        const [overviewRes, tasksRes, agentsRes] = await Promise.all([
          fetch('/api/v1/system/overview'),
          fetch('/api/v1/tasks'),
          fetch('/api/v1/agents')
        ]);

        if (overviewRes.ok) {
          const overview = await overviewRes.json();
          renderOverview(overview);
        }

        if (tasksRes.ok) {
          const tasks = await tasksRes.json();
          renderKanban(tasks);
        }

        if (agentsRes.ok) {
          const agents = await agentsRes.json();
          document.getElementById('metricAgents').innerText = agents.length;
        }
      } catch (err) {
        console.error('Data refresh error:', err);
      }
    }

    function renderOverview(data) {
      const m = data.metrics;
      document.getElementById('metricAgents').innerText = m.agents_total;
      document.getElementById('metricBacklog').innerText = m.tasks.backlog;
      document.getElementById('metricInProgress').innerText = m.tasks.in_progress;
      document.getElementById('metricConsultation').innerText = m.tasks.paused_for_consultation;
      document.getElementById('metricDLQ').innerText = m.tasks.dlq;
      document.getElementById('metricAdvisors').innerText = m.advisors_total;
    }

    function renderKanban(tasks) {
      const cols = {
        backlog: document.getElementById('cardsBacklog'),
        inProgress: document.getElementById('cardsInProgress'),
        paused: document.getElementById('cardsPaused'),
        completed: document.getElementById('cardsCompleted'),
        dlq: document.getElementById('cardsDLQ')
      };

      Object.values(cols).forEach(c => c.innerHTML = '');

      const counts = { backlog: 0, inProgress: 0, paused: 0, completed: 0, dlq: 0 };

      tasks.forEach(t => {
        const card = createKanbanCard(t);
        if (t.status === 'IN_PROGRESS') {
          cols.inProgress.appendChild(card);
          counts.inProgress++;
        } else if (t.status === 'PAUSED_FOR_CONSULTATION') {
          cols.paused.appendChild(card);
          counts.paused++;
        } else if (t.status === 'DEAD_LETTER_QUEUE') {
          cols.dlq.appendChild(card);
          counts.dlq++;
        } else if (t.status === 'DONE' || t.status === 'COMPLETED') {
          cols.completed.appendChild(card);
          counts.completed++;
        } else {
          cols.backlog.appendChild(card);
          counts.backlog++;
        }
      });

      // Show empty state placeholder if column has no tasks
      Object.entries(cols).forEach(([key, colEl]) => {
        if (counts[key] === 0) {
          colEl.innerHTML = `<div class="p-4 text-center text-slate-400 text-[11px] italic">No tasks in this column</div>`;
        }
      });

      document.getElementById('colCountBacklog').innerText = counts.backlog;
      document.getElementById('colCountInProgress').innerText = counts.inProgress;
      document.getElementById('colCountPaused').innerText = counts.paused;
      document.getElementById('colCountCompleted').innerText = counts.completed;
      document.getElementById('colCountDLQ').innerText = counts.dlq;
    }

    function createKanbanCard(t) {
      const div = document.createElement('div');
      div.className = 'bg-white border border-slate-200 hover:border-slate-300 rounded-lg p-3 space-y-2 text-xs transition shadow-xs';

      let priorityBadge = 'bg-slate-100 text-slate-700';
      if (t.priority === 'HIGH') priorityBadge = 'bg-amber-50 text-amber-800 border border-amber-200';
      if (t.priority === 'URGENT' || t.priority === 'CRITICAL') priorityBadge = 'bg-red-50 text-red-800 border border-red-200';

      let actionHtml = '';
      if (t.status === 'IN_PROGRESS') {
        actionHtml = `
          <div class="pt-2 border-t border-slate-100 flex items-center justify-between">
            <span class="text-[10px] text-blue-700 font-mono font-medium">🔒 Lock: Active (60s TTL)</span>
            <button onclick="suspendTask('${t.id}')" class="text-[10px] bg-amber-50 hover:bg-amber-100 text-amber-800 font-semibold px-2 py-0.5 rounded border border-amber-200">Suspend</button>
          </div>
        `;
      } else if (t.status === 'PAUSED_FOR_CONSULTATION') {
        actionHtml = `
          <div class="pt-2 border-t border-slate-100 flex items-center justify-between">
            <span class="text-[10px] text-amber-700 font-mono font-medium">⏸️ TTL Frozen (${t.lock_suspended_remaining_seconds || 45}s)</span>
            <button onclick="resumeTask('${t.id}')" class="text-[10px] bg-emerald-50 hover:bg-emerald-100 text-emerald-800 font-semibold px-2 py-0.5 rounded border border-emerald-200">Resume</button>
          </div>
        `;
      } else if (t.status === 'DEAD_LETTER_QUEUE') {
        actionHtml = `
          <div class="pt-2 border-t border-red-100 space-y-1">
            <div class="text-[10px] text-red-700 leading-tight"><strong>Reaped:</strong> ${escapeHtml(t.dlq_reason || 'Lock expired; swept by reaper')}</div>
            <div class="flex items-center justify-between pt-1">
              <span class="text-[10px] text-slate-400 font-mono">Retries: ${t.retry_count}</span>
              <button onclick="requeueDLQ('${t.id}')" class="text-[10px] bg-red-100 hover:bg-red-200 text-red-800 font-semibold px-2 py-0.5 rounded border border-red-300">Requeue</button>
            </div>
          </div>
        `;
      }

      div.innerHTML = `
        <div class="flex items-center justify-between">
          <span class="text-[10px] font-mono text-slate-400 font-medium">${t.project_tag}</span>
          <span class="text-[10px] font-bold px-1.5 py-0.5 rounded ${priorityBadge}">${t.priority}</span>
        </div>
        <div class="font-bold text-slate-900 leading-snug">${escapeHtml(t.title)}</div>
        <p class="text-slate-500 text-[11px] line-clamp-2 leading-relaxed">${escapeHtml(t.description || 'No description provided.')}</p>
        ${actionHtml}
      `;
      return div;
    }

    async function suspendTask(taskId) {
      try {
        const res = await fetch(`/api/v1/tasks/${taskId}/suspend`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ correlation_id: 'ui-manual-suspend' })
        });
        if (res.ok) {
          logToTerminal(`[LOCK_SUSPEND] Task ${taskId} suspended for consultation. Lock TTL frozen.`, 'amber');
          refreshActualData();
        }
      } catch (err) {
        console.error(err);
      }
    }

    async function resumeTask(taskId) {
      try {
        const res = await fetch(`/api/v1/tasks/${taskId}/resume`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ correlation_id: 'ui-manual-resume' })
        });
        if (res.ok) {
          logToTerminal(`[LOCK_RESUME] Task ${taskId} resumed. Lock unfreezes and countdown continues.`, 'emerald');
          refreshActualData();
        }
      } catch (err) {
        console.error(err);
      }
    }

    async function fetchAdvisors() {
      try {
        const res = await fetch('/api/v1/advisors');
        if (res.ok) {
          cachedAdvisors = await res.json();
          renderAdvisorsList(cachedAdvisors);
        }
      } catch (err) {
        console.error(err);
      }
    }

    function renderAdvisorsList(advisors) {
      const container = document.getElementById('advisorsList');
      if (advisors.length === 0) {
        container.innerHTML = '<div class="col-span-2 text-center text-slate-400 py-10 text-xs italic">No advisors registered in database. Use Setup Wizard to appoint one.</div>';
        return;
      }
      container.innerHTML = advisors.map(a => `
        <div class="bg-white border border-purple-200 rounded-xl p-5 space-y-3 shadow-xs">
          <div class="flex items-center justify-between">
            <div class="flex items-center space-x-2.5">
              <div class="w-8 h-8 rounded-lg bg-purple-50 border border-purple-200 flex items-center justify-center text-purple-700 font-bold">
                🧠
              </div>
              <div>
                <h3 class="text-sm font-bold text-slate-900">${escapeHtml(a.name)}</h3>
                <span class="text-[10px] font-mono text-purple-700 bg-purple-50 border border-purple-200 px-2 py-0.5 rounded font-semibold">${a.domain}</span>
              </div>
            </div>
            <span class="text-[11px] font-mono font-semibold text-indigo-700 bg-indigo-50 border border-indigo-200 px-2 py-0.5 rounded">${a.reasoning_model}</span>
          </div>
          <p class="text-xs text-slate-600 leading-relaxed">${escapeHtml(a.system_prompt)}</p>
          <div class="pt-3 border-t border-slate-100 flex items-center justify-between">
            <span class="text-[11px] text-slate-500">Status: <span class="text-emerald-700 font-semibold">${a.status}</span></span>
            <button onclick="promptConsultAdvisor('${a.id}', '${escapeHtml(a.name)}')" class="text-xs bg-purple-600 hover:bg-purple-700 text-white px-3 py-1 rounded-lg font-semibold shadow-xs transition">Consult</button>
          </div>
        </div>
      `).join('');
    }

    function promptConsultAdvisor(id, name) {
      openAdvisoryModal();
      document.getElementById('modalAdvisorSelect').value = id;
    }

    async function submitAdvisorySession() {
      const advisorId = document.getElementById('modalAdvisorSelect').value;
      const topic = document.getElementById('modalAdvisoryTopic').value;
      const inquiry = document.getElementById('modalAdvisoryInquiry').value;
      if (!topic || !inquiry) {
        alert('Please fill out topic and inquiry');
        return;
      }

      const btn = document.getElementById('modalAdvisorSubmitBtn');
      btn.innerText = 'Synthesizing with Deep Reasoning...';
      btn.disabled = true;

      try {
        const res = await fetch('/api/v1/advisors/sessions', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            advisor_id: advisorId,
            requesting_agent_id: 'lead-architect',
            topic: topic,
            inquiry_details: inquiry
          })
        });

        if (res.ok) {
          const session = await res.json();
          closeAdvisoryModal();
          switchTab('telemetry');
          logToTerminal(`[ADVISORY_SYNTHESIS] Advisor completed deep reasoning on '${topic}':`, 'purple');
          logToTerminal(`[RECOMMENDATION] ${session.synthesis}`, 'emerald');
        } else {
          alert('Advisory session failed');
        }
      } catch (err) {
        console.error(err);
      } finally {
        btn.innerText = 'Run Deep Reasoning';
        btn.disabled = false;
      }
    }

    // 6. Owner Copilot Interaction
    function setCopilotQuery(q) {
      document.getElementById('copilotQueryInput').value = q;
      submitCopilotQuery();
    }

    async function submitCopilotQuery() {
      const q = document.getElementById('copilotQueryInput').value.trim();
      if (!q) return;

      const btn = document.getElementById('copilotSendBtn');
      btn.innerText = 'Processing...';
      btn.disabled = true;

      try {
        const res = await fetch('/api/v1/owner/copilot/chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ message: q })
        });

        if (res.ok) {
          const data = await res.json();
          document.getElementById('copilotResponseBox').classList.remove('hidden');
          document.getElementById('copilotIntentBadge').innerText = data.intent;
          document.getElementById('copilotMessageText').innerText = data.response_message;

          const navSec = document.getElementById('copilotUiNavSection');
          if (data.ui_navigation) {
            navSec.classList.remove('hidden');
            document.getElementById('copilotUiNavContent').innerHTML = `
              <strong>Target Route:</strong> ${escapeHtml(data.ui_navigation.route)}<br>
              <strong>Component:</strong> ${escapeHtml(data.ui_navigation.component_name || 'N/A')}<br>
              <strong>Parameters:</strong> ${JSON.stringify(data.ui_navigation.parameters || {})}
            `;
          } else {
            navSec.classList.add('hidden');
          }

          const diagSec = document.getElementById('copilotDiagnosticsSection');
          if (data.diagnostic_summary) {
            diagSec.classList.remove('hidden');
            document.getElementById('copilotDiagnosticsContent').innerHTML = `
              <strong>Root Cause:</strong> ${escapeHtml(data.diagnostic_summary.root_cause || 'N/A')}<br>
              <strong>Recommendation:</strong> ${escapeHtml(data.diagnostic_summary.recommended_action || 'N/A')}
            `;
          } else {
            diagSec.classList.add('hidden');
          }
        }
      } catch (err) {
        console.error(err);
      } finally {
        btn.innerText = 'Send';
        btn.disabled = false;
      }
    }

    // 7. Create New Task
    async function submitNewTask() {
      const title = document.getElementById('modalTaskTitle').value.trim();
      const desc = document.getElementById('modalTaskDesc').value.trim();
      const priority = document.getElementById('modalTaskPriority').value;
      const tag = document.getElementById('modalTaskTag').value.trim();

      if (!title) {
        alert('Please specify task title');
        return;
      }

      try {
        const res = await fetch('/api/v1/tasks', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            title: title,
            description: desc,
            priority: priority,
            project_tag: tag
          })
        });

        if (res.ok) {
          closeNewTaskModal();
          logToTerminal(`[TASK_CREATED] New task '${title}' created successfully`, 'emerald');
          refreshActualData();
        }
      } catch (err) {
        console.error(err);
      }
    }

    // 8. WebSocket Telemetry
    function initWebSocket() {
      const loc = window.location;
      const wsProtocol = loc.protocol === 'https:' ? 'wss:' : 'ws:';
      const wsUrl = `${wsProtocol}//${loc.host}/ws/cockpit`;

      ws = new WebSocket(wsUrl);

      ws.onopen = () => {
        document.getElementById('wsStatusDot').className = 'w-2 h-2 rounded-full bg-emerald-500 pulse-dot';
        document.getElementById('wsStatusText').innerText = 'Telemetry Connected';
        logToTerminal('[WS_CONN] Connected to real-time orchestrator channel /ws/cockpit', 'emerald');
      };

      ws.onmessage = (event) => {
        try {
          const msg = JSON.parse(event.data);
          handleWebSocketMessage(msg);
        } catch (e) {
          logToTerminal(`[WS_RAW] ${event.data}`, 'gray');
        }
      };

      ws.onclose = () => {
        document.getElementById('wsStatusDot').className = 'w-2 h-2 rounded-full bg-red-500';
        document.getElementById('wsStatusText').innerText = 'Telemetry Reconnecting...';
        logToTerminal('[WS_DISCONN] Connection dropped. Retrying in 3s...', 'red');
        setTimeout(initWebSocket, 3000);
      };
    }

    function handleWebSocketMessage(msg) {
      if (msg.type === 'terminal_chunk') {
        const color = msg.stream === 'stderr' ? 'red' : 'cyan';
        logToTerminal(`[DAEMON ${msg.daemon_id}] (${msg.stream}) ${msg.text.trim()}`, color);
      } else if (msg.type === 'task_status_changed') {
        logToTerminal(`[STATE_CHANGE] Task status updated: ${JSON.stringify(msg.payload)}`, 'purple');
        refreshActualData();
      } else {
        logToTerminal(`[EVENT] ${JSON.stringify(msg)}`, 'blue');
      }
    }

    function logToTerminal(text, color = 'gray') {
      const term = document.getElementById('terminalBody');
      const row = document.createElement('div');
      const time = new Date().toLocaleTimeString();

      let colorClass = 'text-slate-300';
      if (color === 'emerald') colorClass = 'text-emerald-400 font-semibold';
      if (color === 'cyan') colorClass = 'text-cyan-300';
      if (color === 'red') colorClass = 'text-red-400 font-semibold';
      if (color === 'purple') colorClass = 'text-purple-300';
      if (color === 'blue') colorClass = 'text-blue-300';
      if (color === 'amber') colorClass = 'text-amber-300';

      row.className = `leading-relaxed ${colorClass}`;
      row.innerHTML = `<span class="text-slate-500 mr-2">[${time}]</span>${escapeHtml(text)}`;
      term.appendChild(row);

      if (autoscroll) {
        term.scrollTop = term.scrollHeight;
      }
    }

    function clearTerminal() {
      document.getElementById('terminalBody').innerHTML = '<div class="text-slate-500">[SYSTEM] Terminal buffer cleared.</div>';
    }

    function toggleTerminalAutoscroll() {
      autoscroll = !autoscroll;
      const btn = document.getElementById('btnAutoscroll');
      btn.innerText = `Autoscroll: ${autoscroll ? 'ON' : 'OFF'}`;
      btn.className = autoscroll 
        ? 'text-[11px] bg-emerald-50 text-emerald-700 border border-emerald-200 px-2.5 py-1 rounded font-mono transition'
        : 'text-[11px] bg-slate-100 text-slate-500 border border-slate-200 px-2.5 py-1 rounded font-mono transition';
    }

    function escapeHtml(string) {
      const entityMap = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' };
      return String(string).replace(/[&<>"']/g, s => entityMap[s]);
    }
  </script>
</body>
</html>
"""
