def get_dashboard_html() -> str:
    return """<!DOCTYPE html>
<html lang="en" class="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>FOLKS // Multi-Agent Orchestrator Dashboard</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <script>
    tailwind.config = {
      darkMode: 'class',
      theme: {
        extend: {
          colors: {
            brand: {
              50: '#f0fdf4',
              500: '#10b981',
              600: '#059669',
              900: '#064e3b',
            },
            dark: {
              bg: '#090d16',
              card: '#111827',
              border: '#1f2937',
              muted: '#374151'
            }
          }
        }
      }
    }
  </script>
  <style>
    body {
      background-color: #090d16;
      color: #e2e8f0;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    }
    .terminal-scroll::-webkit-scrollbar {
      width: 6px;
      height: 6px;
    }
    .terminal-scroll::-webkit-scrollbar-track {
      background: #0f172a;
    }
    .terminal-scroll::-webkit-scrollbar-thumb {
      background: #334155;
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
<body class="min-h-screen flex flex-col antialiased selection:bg-emerald-500 selection:text-black">

  <!-- Top Navigation Bar -->
  <header class="border-b border-dark-border bg-dark-card/90 backdrop-blur sticky top-0 z-50 px-6 py-3.5 flex items-center justify-between">
    <div class="flex items-center space-x-4">
      <div class="flex items-center space-x-2">
        <div class="w-8 h-8 rounded-lg bg-emerald-500/20 border border-emerald-500/40 flex items-center justify-center font-bold text-emerald-400 text-lg shadow-[0_0_15px_rgba(16,185,129,0.3)]">
          F
        </div>
        <div>
          <div class="flex items-center space-x-2">
            <span class="font-black tracking-wider text-white text-lg">FOLKS</span>
            <span class="text-xs px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 font-mono font-semibold">ORCHESTRATOR v1.0</span>
          </div>
          <p class="text-[11px] text-gray-400">Resilient Multi-Agent Kanban & Host Daemon Engine</p>
        </div>
      </div>
      
      <div class="hidden md:flex items-center space-x-2 pl-4 border-l border-dark-border text-xs text-gray-400">
        <div class="flex items-center space-x-1.5 bg-dark-bg px-2.5 py-1 rounded-md border border-dark-border">
          <span class="w-2 h-2 rounded-full bg-emerald-500 pulse-dot"></span>
          <span class="font-mono text-emerald-400 font-medium">Core API :8000</span>
        </div>
        <div class="flex items-center space-x-1.5 bg-dark-bg px-2.5 py-1 rounded-md border border-dark-border">
          <span class="w-2 h-2 rounded-full bg-cyan-400 pulse-dot"></span>
          <span class="font-mono text-cyan-300">Lock Sweeper (15s / 60s TTL)</span>
        </div>
        <div id="wsStatusBadge" class="flex items-center space-x-1.5 bg-dark-bg px-2.5 py-1 rounded-md border border-dark-border">
          <span id="wsStatusDot" class="w-2 h-2 rounded-full bg-amber-400 pulse-dot"></span>
          <span id="wsStatusText" class="font-mono text-gray-300">WS Telemetry Connecting...</span>
        </div>
      </div>
    </div>

    <div class="flex items-center space-x-3">
      <button onclick="seedDemoData()" id="seedBtn" class="text-xs bg-emerald-600 hover:bg-emerald-500 text-white font-medium px-3.5 py-1.5 rounded-lg border border-emerald-400/30 flex items-center space-x-1.5 shadow-sm transition">
        <span>⚡</span>
        <span>Seed Demo Data</span>
      </button>

      <button onclick="openNewTaskModal()" class="text-xs bg-slate-800 hover:bg-slate-700 text-gray-200 font-medium px-3 py-1.5 rounded-lg border border-slate-700 flex items-center space-x-1 transition">
        <span>➕</span>
        <span>New Task</span>
      </button>

      <a href="/docs" target="_blank" class="text-xs bg-slate-800 hover:bg-slate-700 text-gray-300 px-3 py-1.5 rounded-lg border border-slate-700 flex items-center space-x-1 transition">
        <span>📖</span>
        <span>Swagger Docs</span>
      </a>

      <a href="http://localhost:3000" target="_blank" class="text-xs bg-purple-950/60 hover:bg-purple-900/80 text-purple-300 border border-purple-800/50 px-3 py-1.5 rounded-lg flex items-center space-x-1 transition" title="Start Cockpit with: cd apps/cockpit && npm run dev">
        <span>🖥️</span>
        <span>Cockpit UI (:3000)</span>
      </a>
    </div>
  </header>

  <!-- Main Content Area -->
  <main class="flex-1 p-6 max-w-7xl w-full mx-auto space-y-6">

    <!-- Resilience Alert Banner -->
    <div class="bg-gradient-to-r from-emerald-950/30 via-slate-900 to-cyan-950/30 border border-emerald-800/30 rounded-xl p-4 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
      <div class="flex items-center space-x-3.5">
        <div class="p-2.5 bg-emerald-500/10 rounded-lg border border-emerald-500/30 text-emerald-400">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"/></svg>
        </div>
        <div>
          <h2 class="text-sm font-semibold text-white">Hierarchical State Machine & Sweeper Active</h2>
          <p class="text-xs text-gray-400 mt-0.5">Kanban holds primary lock. Daemons ping 15s heartbeats. Expired locks automatically swept to DLQ. War rooms act as non-blocking sub-routines.</p>
        </div>
      </div>
      <div class="flex items-center space-x-2 text-xs font-mono text-gray-400 bg-black/40 px-3 py-1.5 rounded-lg border border-slate-800">
        <span class="text-gray-500">Daemon Driver:</span>
        <code class="text-emerald-400">python -m packages.daemon.folks_daemon.main</code>
      </div>
    </div>

    <!-- Metrics Cards Grid -->
    <div class="grid grid-cols-2 md:grid-cols-6 gap-3.5">
      <div class="bg-dark-card border border-dark-border rounded-xl p-4 flex flex-col justify-between">
        <span class="text-[11px] font-medium text-gray-400 uppercase tracking-wider">Agents</span>
        <div class="mt-2 flex items-baseline justify-between">
          <span id="metricAgents" class="text-2xl font-black text-white font-mono">-</span>
          <span class="text-[10px] text-emerald-400 bg-emerald-500/10 px-1.5 py-0.5 rounded">Active</span>
        </div>
      </div>

      <div class="bg-dark-card border border-dark-border rounded-xl p-4 flex flex-col justify-between">
        <span class="text-[11px] font-medium text-gray-400 uppercase tracking-wider">Backlog / Todo</span>
        <div class="mt-2 flex items-baseline justify-between">
          <span id="metricBacklog" class="text-2xl font-black text-white font-mono">-</span>
          <span class="text-[10px] text-gray-400 bg-gray-500/10 px-1.5 py-0.5 rounded">Queue</span>
        </div>
      </div>

      <div class="bg-dark-card border border-blue-500/30 rounded-xl p-4 flex flex-col justify-between shadow-[0_0_12px_rgba(59,130,246,0.1)]">
        <span class="text-[11px] font-medium text-blue-400 uppercase tracking-wider">In Progress (Locked)</span>
        <div class="mt-2 flex items-baseline justify-between">
          <span id="metricInProgress" class="text-2xl font-black text-blue-300 font-mono">-</span>
          <span class="text-[10px] text-blue-400 bg-blue-500/10 px-1.5 py-0.5 rounded">Live TTL</span>
        </div>
      </div>

      <div class="bg-dark-card border border-amber-500/30 rounded-xl p-4 flex flex-col justify-between shadow-[0_0_12px_rgba(245,158,11,0.1)]">
        <span class="text-[11px] font-medium text-amber-400 uppercase tracking-wider">Consultation</span>
        <div class="mt-2 flex items-baseline justify-between">
          <span id="metricConsultation" class="text-2xl font-black text-amber-300 font-mono">-</span>
          <span class="text-[10px] text-amber-400 bg-amber-500/10 px-1.5 py-0.5 rounded">TTL Frozen</span>
        </div>
      </div>

      <div class="bg-dark-card border border-red-500/40 rounded-xl p-4 flex flex-col justify-between shadow-[0_0_15px_rgba(239,68,68,0.15)]">
        <span class="text-[11px] font-medium text-red-400 uppercase tracking-wider">DLQ (Swept)</span>
        <div class="mt-2 flex items-baseline justify-between">
          <span id="metricDLQ" class="text-2xl font-black text-red-400 font-mono">-</span>
          <span class="text-[10px] text-red-400 bg-red-500/10 px-1.5 py-0.5 rounded">Reaped</span>
        </div>
      </div>

      <div class="bg-dark-card border border-purple-500/30 rounded-xl p-4 flex flex-col justify-between shadow-[0_0_12px_rgba(168,85,247,0.1)]">
        <span class="text-[11px] font-medium text-purple-400 uppercase tracking-wider">Advisory Board</span>
        <div class="mt-2 flex items-baseline justify-between">
          <span id="metricAdvisors" class="text-2xl font-black text-purple-300 font-mono">-</span>
          <span class="text-[10px] text-purple-400 bg-purple-500/10 px-1.5 py-0.5 rounded">Heavy KB</span>
        </div>
      </div>
    </div>

    <!-- Interactive Navigation Tabs -->
    <div class="flex items-center space-x-1 border-b border-dark-border pb-px">
      <button onclick="switchTab('kanban')" id="tabKanban" class="tab-btn px-4 py-2 text-xs font-semibold text-emerald-400 border-b-2 border-emerald-500 transition flex items-center space-x-2">
        <span>📋</span>
        <span>Kanban Board</span>
      </button>
      <button onclick="switchTab('advisors')" id="tabAdvisors" class="tab-btn px-4 py-2 text-xs font-semibold text-gray-400 hover:text-gray-200 border-b-2 border-transparent transition flex items-center space-x-2">
        <span>🧠</span>
        <span>Board of Advisors</span>
      </button>
      <button onclick="switchTab('copilot')" id="tabCopilot" class="tab-btn px-4 py-2 text-xs font-semibold text-gray-400 hover:text-gray-200 border-b-2 border-transparent transition flex items-center space-x-2">
        <span>💬</span>
        <span>Owner Copilot (Typed API)</span>
      </button>
      <button onclick="switchTab('telemetry')" id="tabTelemetry" class="tab-btn px-4 py-2 text-xs font-semibold text-gray-400 hover:text-gray-200 border-b-2 border-transparent transition flex items-center space-x-2">
        <span>📟</span>
        <span>Live Telemetry Terminal</span>
      </button>
    </div>

    <!-- Tab 1: Kanban Board -->
    <div id="viewKanban" class="space-y-4">
      <div class="grid grid-cols-1 md:grid-cols-5 gap-4">
        <!-- Col: Backlog / Todo -->
        <div class="bg-dark-card border border-dark-border rounded-xl flex flex-col min-h-[480px]">
          <div class="p-3 border-b border-dark-border flex items-center justify-between">
            <span class="text-xs font-bold text-gray-300 flex items-center space-x-1.5">
              <span class="w-2 h-2 rounded-full bg-gray-400"></span>
              <span>BACKLOG / TODO</span>
            </span>
            <span id="colCountBacklog" class="text-xs font-mono text-gray-400 bg-gray-800 px-2 py-0.5 rounded">0</span>
          </div>
          <div id="cardsBacklog" class="p-2.5 space-y-2.5 flex-1 overflow-y-auto max-h-[600px]"></div>
        </div>

        <!-- Col: In Progress (Active Lock) -->
        <div class="bg-dark-card border border-blue-900/40 rounded-xl flex flex-col min-h-[480px]">
          <div class="p-3 border-b border-blue-900/40 bg-blue-950/20 flex items-center justify-between">
            <span class="text-xs font-bold text-blue-400 flex items-center space-x-1.5">
              <span class="w-2 h-2 rounded-full bg-blue-400 pulse-dot"></span>
              <span>IN PROGRESS (LOCKED)</span>
            </span>
            <span id="colCountInProgress" class="text-xs font-mono text-blue-300 bg-blue-950 px-2 py-0.5 rounded border border-blue-800/40">0</span>
          </div>
          <div id="cardsInProgress" class="p-2.5 space-y-2.5 flex-1 overflow-y-auto max-h-[600px]"></div>
        </div>

        <!-- Col: Paused For Consultation -->
        <div class="bg-dark-card border border-amber-900/40 rounded-xl flex flex-col min-h-[480px]">
          <div class="p-3 border-b border-amber-900/40 bg-amber-950/20 flex items-center justify-between">
            <span class="text-xs font-bold text-amber-400 flex items-center space-x-1.5">
              <span class="w-2 h-2 rounded-full bg-amber-400"></span>
              <span>PAUSED CONSULTATION</span>
            </span>
            <span id="colCountPaused" class="text-xs font-mono text-amber-300 bg-amber-950 px-2 py-0.5 rounded border border-amber-800/40">0</span>
          </div>
          <div id="cardsPaused" class="p-2.5 space-y-2.5 flex-1 overflow-y-auto max-h-[600px]"></div>
        </div>

        <!-- Col: Completed -->
        <div class="bg-dark-card border border-emerald-900/40 rounded-xl flex flex-col min-h-[480px]">
          <div class="p-3 border-b border-emerald-900/40 bg-emerald-950/20 flex items-center justify-between">
            <span class="text-xs font-bold text-emerald-400 flex items-center space-x-1.5">
              <span class="w-2 h-2 rounded-full bg-emerald-400"></span>
              <span>COMPLETED</span>
            </span>
            <span id="colCountCompleted" class="text-xs font-mono text-emerald-300 bg-emerald-950 px-2 py-0.5 rounded border border-emerald-800/40">0</span>
          </div>
          <div id="cardsCompleted" class="p-2.5 space-y-2.5 flex-1 overflow-y-auto max-h-[600px]"></div>
        </div>

        <!-- Col: Dead Letter Queue (DLQ) -->
        <div class="bg-dark-card border border-red-900/50 rounded-xl flex flex-col min-h-[480px] shadow-[0_0_20px_rgba(239,68,68,0.05)]">
          <div class="p-3 border-b border-red-900/50 bg-red-950/30 flex items-center justify-between">
            <span class="text-xs font-bold text-red-400 flex items-center space-x-1.5">
              <span class="w-2 h-2 rounded-full bg-red-500 pulse-dot"></span>
              <span>DEAD-LETTER QUEUE (DLQ)</span>
            </span>
            <span id="colCountDLQ" class="text-xs font-mono text-red-300 bg-red-950 px-2 py-0.5 rounded border border-red-800/40">0</span>
          </div>
          <div id="cardsDLQ" class="p-2.5 space-y-2.5 flex-1 overflow-y-auto max-h-[600px]"></div>
        </div>
      </div>
    </div>

    <!-- Tab 2: Board of Advisors -->
    <div id="viewAdvisors" class="hidden space-y-6">
      <div class="flex items-center justify-between">
        <div>
          <h2 class="text-base font-bold text-white">Board of Advisors</h2>
          <p class="text-xs text-gray-400">Domain authorities loaded with dense knowledge bases and deep reasoning chains (e.g. Claude 3.7 Thought, o3-mini).</p>
        </div>
        <button onclick="openAdvisoryModal()" class="text-xs bg-purple-600 hover:bg-purple-500 text-white px-3.5 py-2 rounded-lg font-medium shadow-sm transition flex items-center space-x-1.5">
          <span>🧠</span>
          <span>Initiate Advisory Session</span>
        </button>
      </div>

      <div id="advisorsList" class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <!-- Dynamically rendered -->
      </div>
    </div>

    <!-- Tab 3: Owner Copilot -->
    <div id="viewCopilot" class="hidden space-y-4">
      <div class="bg-dark-card border border-dark-border rounded-xl p-5 space-y-4">
        <div class="flex items-center justify-between">
          <div class="flex items-center space-x-3">
            <div class="w-9 h-9 rounded-lg bg-emerald-500/20 border border-emerald-500/40 flex items-center justify-center text-emerald-400 font-bold">
              ⚡
            </div>
            <div>
              <h2 class="text-sm font-bold text-white">Owner Copilot Interface</h2>
              <p class="text-xs text-gray-400">Strictly typed Pydantic API overlay. Zero direct SQL execution. Intelligent UI map RAG & log diagnostics.</p>
            </div>
          </div>
          <span class="text-xs font-mono text-emerald-400 bg-emerald-950/40 border border-emerald-800/40 px-2.5 py-1 rounded-md">Boundary: Enforced</span>
        </div>

        <div class="space-y-2">
          <div class="flex items-center space-x-2">
            <input id="copilotQueryInput" type="text" placeholder="e.g. 'Where do I configure agent token limits?' or 'Why did the OOM task fail in DLQ?'" class="flex-1 bg-dark-bg border border-dark-border rounded-lg px-3.5 py-2 text-xs text-white placeholder-gray-500 focus:outline-none focus:border-emerald-500 font-sans" onkeydown="if(event.key === 'Enter') submitCopilotQuery()">
            <button onclick="submitCopilotQuery()" id="copilotSendBtn" class="bg-emerald-600 hover:bg-emerald-500 text-white px-4 py-2 rounded-lg text-xs font-medium transition flex items-center space-x-1.5">
              <span>Send Query</span>
            </button>
          </div>
          <div class="flex flex-wrap gap-2 text-[11px] text-gray-400">
            <span class="text-gray-500">Quick queries:</span>
            <button onclick="setCopilotQuery('Where do I configure agent token limits?')" class="bg-slate-800 hover:bg-slate-700 px-2 py-0.5 rounded text-gray-300">"Where do I configure token limits?"</button>
            <button onclick="setCopilotQuery('Explain why recent tasks failed or got swept to DLQ')" class="bg-slate-800 hover:bg-slate-700 px-2 py-0.5 rounded text-gray-300">"Explain why task swept to DLQ"</button>
            <button onclick="setCopilotQuery('How do I enable the dark theme or war rooms?')" class="bg-slate-800 hover:bg-slate-700 px-2 py-0.5 rounded text-gray-300">"How do I enable War Rooms?"</button>
          </div>
        </div>

        <!-- Copilot Response Container -->
        <div id="copilotResponseBox" class="hidden bg-dark-bg border border-dark-border rounded-lg p-4 space-y-3 font-mono text-xs">
          <div class="flex items-center justify-between text-gray-400 border-b border-dark-border pb-2">
            <span class="text-emerald-400 font-semibold flex items-center space-x-1.5">
              <span>🤖</span>
              <span>Copilot Response (Typed & Validated)</span>
            </span>
            <span id="copilotIntentBadge" class="text-[10px] bg-slate-800 px-2 py-0.5 rounded text-gray-300 font-mono">INTENT</span>
          </div>
          <p id="copilotMessageText" class="text-gray-200 font-sans leading-relaxed"></p>
          <div id="copilotUiNavSection" class="hidden bg-slate-900 border border-slate-800 rounded p-3 text-[11px] space-y-1">
            <span class="text-gray-400 font-bold block">UI Navigation Route:</span>
            <div id="copilotUiNavContent" class="text-cyan-300"></div>
          </div>
          <div id="copilotDiagnosticsSection" class="hidden bg-slate-900 border border-slate-800 rounded p-3 text-[11px] space-y-1">
            <span class="text-amber-400 font-bold block">Diagnostic Log Summary:</span>
            <div id="copilotDiagnosticsContent" class="text-gray-300"></div>
          </div>
        </div>
      </div>
    </div>

    <!-- Tab 4: Live Telemetry Terminal -->
    <div id="viewTelemetry" class="space-y-3">
      <div class="bg-dark-card border border-dark-border rounded-xl p-4 flex flex-col h-[520px]">
        <div class="flex items-center justify-between pb-3 border-b border-dark-border">
          <div class="flex items-center space-x-2">
            <span class="w-3 h-3 rounded-full bg-emerald-500"></span>
            <span class="w-3 h-3 rounded-full bg-amber-500"></span>
            <span class="w-3 h-3 rounded-full bg-red-500"></span>
            <span class="text-xs font-mono font-bold text-gray-300 ml-2">LIVE REAL-TIME TELEMETRY // /ws/cockpit</span>
          </div>
          <div class="flex items-center space-x-2">
            <button onclick="clearTerminal()" class="text-[11px] bg-slate-800 hover:bg-slate-700 text-gray-300 px-2.5 py-1 rounded font-mono transition">Clear</button>
            <button onclick="toggleTerminalAutoscroll()" id="btnAutoscroll" class="text-[11px] bg-emerald-950 text-emerald-400 border border-emerald-800 px-2.5 py-1 rounded font-mono transition">Autoscroll: ON</button>
          </div>
        </div>

        <div id="terminalBody" class="flex-1 bg-black/90 p-3.5 font-mono text-xs overflow-y-auto space-y-1 terminal-scroll rounded-lg mt-3 text-gray-300">
          <div class="text-gray-500">[SYSTEM] Terminal initialized. Waiting for daemon heartbeats and orchestrator events...</div>
        </div>
      </div>
    </div>

  </main>

  <!-- Modal: Create New Task -->
  <div id="newTaskModal" class="hidden fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
    <div class="bg-dark-card border border-dark-border rounded-2xl max-w-lg w-full p-6 space-y-4 shadow-2xl">
      <div class="flex items-center justify-between border-b border-dark-border pb-3">
        <h3 class="text-sm font-bold text-white flex items-center space-x-2">
          <span>➕</span>
          <span>Create New Kanban Task</span>
        </h3>
        <button onclick="closeNewTaskModal()" class="text-gray-400 hover:text-white">&times;</button>
      </div>
      <div class="space-y-3 text-xs">
        <div>
          <label class="block text-gray-400 mb-1 font-medium">Task Title</label>
          <input id="modalTaskTitle" type="text" placeholder="e.g. Implement TLS pinning on CLI socket" class="w-full bg-dark-bg border border-dark-border rounded-lg px-3 py-2 text-white placeholder-gray-600 focus:outline-none focus:border-emerald-500">
        </div>
        <div>
          <label class="block text-gray-400 mb-1 font-medium">Description</label>
          <textarea id="modalTaskDesc" rows="3" placeholder="Execution requirements, success metrics, and constraints..." class="w-full bg-dark-bg border border-dark-border rounded-lg px-3 py-2 text-white placeholder-gray-600 focus:outline-none focus:border-emerald-500"></textarea>
        </div>
        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="block text-gray-400 mb-1 font-medium">Priority</label>
            <select id="modalTaskPriority" class="w-full bg-dark-bg border border-dark-border rounded-lg px-3 py-2 text-white focus:outline-none focus:border-emerald-500">
              <option value="LOW">LOW</option>
              <option value="MEDIUM" selected>MEDIUM</option>
              <option value="HIGH">HIGH</option>
              <option value="URGENT">URGENT</option>
            </select>
          </div>
          <div>
            <label class="block text-gray-400 mb-1 font-medium">Project Tag</label>
            <input id="modalTaskTag" type="text" value="folks_core" class="w-full bg-dark-bg border border-dark-border rounded-lg px-3 py-2 text-white focus:outline-none focus:border-emerald-500">
          </div>
        </div>
      </div>
      <div class="flex items-center justify-end space-x-2 pt-3 border-t border-dark-border">
        <button onclick="closeNewTaskModal()" class="px-3.5 py-1.5 text-xs text-gray-400 hover:text-white">Cancel</button>
        <button onclick="submitNewTask()" class="bg-emerald-600 hover:bg-emerald-500 text-white px-4 py-1.5 rounded-lg text-xs font-semibold shadow-sm transition">Create Task</button>
      </div>
    </div>
  </div>

  <!-- Modal: Advisory Session Prompt -->
  <div id="advisoryModal" class="hidden fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
    <div class="bg-dark-card border border-purple-900/60 rounded-2xl max-w-xl w-full p-6 space-y-4 shadow-2xl">
      <div class="flex items-center justify-between border-b border-dark-border pb-3">
        <div class="flex items-center space-x-2">
          <span class="text-xl">🧠</span>
          <h3 class="text-sm font-bold text-white">Board of Advisors Consultation</h3>
        </div>
        <button onclick="closeAdvisoryModal()" class="text-gray-400 hover:text-white">&times;</button>
      </div>
      <div class="space-y-3 text-xs">
        <div>
          <label class="block text-gray-400 mb-1 font-medium">Select Advisor</label>
          <select id="modalAdvisorSelect" class="w-full bg-dark-bg border border-dark-border rounded-lg px-3 py-2 text-white focus:outline-none focus:border-purple-500"></select>
        </div>
        <div>
          <label class="block text-gray-400 mb-1 font-medium">Topic / Strategic Dilemma</label>
          <input id="modalAdvisoryTopic" type="text" placeholder="e.g. Lock TTL Jitter under High Concurrency" class="w-full bg-dark-bg border border-dark-border rounded-lg px-3 py-2 text-white placeholder-gray-600 focus:outline-none focus:border-purple-500">
        </div>
        <div>
          <label class="block text-gray-400 mb-1 font-medium">Inquiry Details</label>
          <textarea id="modalAdvisoryInquiry" rows="4" placeholder="Detail the technical impasse, trade-offs, and evidence for deep reasoning..." class="w-full bg-dark-bg border border-dark-border rounded-lg px-3 py-2 text-white placeholder-gray-600 focus:outline-none focus:border-purple-500"></textarea>
        </div>
      </div>
      <div class="flex items-center justify-end space-x-2 pt-3 border-t border-dark-border">
        <button onclick="closeAdvisoryModal()" class="px-3.5 py-1.5 text-xs text-gray-400 hover:text-white">Cancel</button>
        <button onclick="submitAdvisorySession()" id="modalAdvisorSubmitBtn" class="bg-purple-600 hover:bg-purple-500 text-white px-4 py-1.5 rounded-lg text-xs font-semibold shadow-sm transition">Run Deep Reasoning</button>
      </div>
    </div>
  </div>

  <script>
    let autoscroll = true;
    let ws = null;
    let cachedAdvisors = [];

    // Switch View Tabs
    function switchTab(tabId) {
      ['kanban', 'advisors', 'copilot', 'telemetry'].forEach(t => {
        const view = document.getElementById('view' + t.charAt(0).toUpperCase() + t.slice(1));
        const btn = document.getElementById('tab' + t.charAt(0).toUpperCase() + t.slice(1));
        if (t === tabId) {
          view.classList.remove('hidden');
          btn.className = 'tab-btn px-4 py-2 text-xs font-semibold text-emerald-400 border-b-2 border-emerald-500 transition flex items-center space-x-2';
        } else {
          view.classList.add('hidden');
          btn.className = 'tab-btn px-4 py-2 text-xs font-semibold text-gray-400 hover:text-gray-200 border-b-2 border-transparent transition flex items-center space-x-2';
        }
      });
      if (tabId === 'advisors') fetchAdvisors();
    }

    // Modal Handlers
    function openNewTaskModal() { document.getElementById('newTaskModal').classList.remove('hidden'); }
    function closeNewTaskModal() { document.getElementById('newTaskModal').classList.add('hidden'); }
    function openAdvisoryModal() { 
      document.getElementById('advisoryModal').classList.remove('hidden'); 
      const sel = document.getElementById('modalAdvisorSelect');
      sel.innerHTML = cachedAdvisors.map(a => `<option value="${a.id}">${a.name} (${a.domain} - ${a.reasoning_model})</option>`).join('');
    }
    function closeAdvisoryModal() { document.getElementById('advisoryModal').classList.add('hidden'); }

    // WebSocket Telemetry Connection
    function initWebSocket() {
      const loc = window.location;
      const wsProtocol = loc.protocol === 'https:' ? 'wss:' : 'ws:';
      const wsUrl = `${wsProtocol}//${loc.host}/ws/cockpit`;

      ws = new WebSocket(wsUrl);

      ws.onopen = () => {
        document.getElementById('wsStatusDot').className = 'w-2 h-2 rounded-full bg-emerald-500 pulse-dot';
        document.getElementById('wsStatusText').innerText = 'WS Telemetry: Connected';
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
        document.getElementById('wsStatusText').innerText = 'WS Telemetry: Reconnecting...';
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
        refreshData();
      } else {
        logToTerminal(`[EVENT] ${JSON.stringify(msg)}`, 'blue');
      }
    }

    function logToTerminal(text, color = 'gray') {
      const term = document.getElementById('terminalBody');
      const row = document.createElement('div');
      const time = new Date().toLocaleTimeString();

      let colorClass = 'text-gray-300';
      if (color === 'emerald') colorClass = 'text-emerald-400 font-semibold';
      if (color === 'cyan') colorClass = 'text-cyan-300';
      if (color === 'red') colorClass = 'text-red-400 font-semibold';
      if (color === 'purple') colorClass = 'text-purple-300';
      if (color === 'blue') colorClass = 'text-blue-300';

      row.className = `leading-relaxed ${colorClass}`;
      row.innerHTML = `<span class="text-gray-600 mr-2">[${time}]</span>${escapeHtml(text)}`;
      term.appendChild(row);

      if (autoscroll) {
        term.scrollTop = term.scrollHeight;
      }
    }

    function clearTerminal() {
      document.getElementById('terminalBody').innerHTML = '<div class="text-gray-500">[SYSTEM] Terminal buffer cleared.</div>';
    }

    function toggleTerminalAutoscroll() {
      autoscroll = !autoscroll;
      const btn = document.getElementById('btnAutoscroll');
      btn.innerText = `Autoscroll: ${autoscroll ? 'ON' : 'OFF'}`;
      btn.className = autoscroll 
        ? 'text-[11px] bg-emerald-950 text-emerald-400 border border-emerald-800 px-2.5 py-1 rounded font-mono transition'
        : 'text-[11px] bg-slate-800 text-gray-400 border border-slate-700 px-2.5 py-1 rounded font-mono transition';
    }

    function escapeHtml(string) {
      const entityMap = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' };
      return String(string).replace(/[&<>"']/g, s => entityMap[s]);
    }

    // API Interactions
    async function refreshData() {
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

      document.getElementById('colCountBacklog').innerText = counts.backlog;
      document.getElementById('colCountInProgress').innerText = counts.inProgress;
      document.getElementById('colCountPaused').innerText = counts.paused;
      document.getElementById('colCountCompleted').innerText = counts.completed;
      document.getElementById('colCountDLQ').innerText = counts.dlq;
    }

    function createKanbanCard(t) {
      const div = document.createElement('div');
      div.className = 'bg-slate-900 border border-dark-border hover:border-slate-600 rounded-lg p-3 space-y-2 text-xs transition shadow-sm';

      let priorityColor = 'bg-slate-800 text-gray-300';
      if (t.priority === 'HIGH') priorityColor = 'bg-amber-500/20 text-amber-400 border border-amber-500/30';
      if (t.priority === 'URGENT' || t.priority === 'CRITICAL') priorityColor = 'bg-red-500/20 text-red-400 border border-red-500/30';

      let actionHtml = '';
      if (t.status === 'IN_PROGRESS') {
        actionHtml = `
          <div class="pt-2 border-t border-slate-800 flex items-center justify-between">
            <span class="text-[10px] text-blue-400 font-mono">🔒 Lock: Active (60s TTL)</span>
            <button onclick="suspendTask('${t.id}')" class="text-[10px] bg-amber-950/80 hover:bg-amber-900 text-amber-300 px-2 py-0.5 rounded border border-amber-800">Suspend</button>
          </div>
        `;
      } else if (t.status === 'PAUSED_FOR_CONSULTATION') {
        actionHtml = `
          <div class="pt-2 border-t border-slate-800 flex items-center justify-between">
            <span class="text-[10px] text-amber-400 font-mono">⏸️ TTL Frozen (${t.lock_suspended_remaining_seconds || 45}s left)</span>
            <button onclick="resumeTask('${t.id}')" class="text-[10px] bg-emerald-950 hover:bg-emerald-900 text-emerald-300 px-2 py-0.5 rounded border border-emerald-800">Resume</button>
          </div>
        `;
      } else if (t.status === 'DEAD_LETTER_QUEUE') {
        actionHtml = `
          <div class="pt-2 border-t border-red-950/80 space-y-1">
            <div class="text-[10px] text-red-400 font-sans leading-tight">Reason: ${escapeHtml(t.dlq_reason || 'Lock expired; swept by reaper')}</div>
            <div class="flex items-center justify-between pt-1">
              <span class="text-[10px] text-gray-500 font-mono">Retries: ${t.retry_count}</span>
              <button onclick="requeueDLQ('${t.id}')" class="text-[10px] bg-red-950 hover:bg-red-900 text-red-300 px-2 py-0.5 rounded border border-red-800">Requeue</button>
            </div>
          </div>
        `;
      }

      div.innerHTML = `
        <div class="flex items-center justify-between">
          <span class="text-[10px] font-mono text-gray-400">${t.project_tag}</span>
          <span class="text-[10px] font-semibold px-1.5 py-0.5 rounded ${priorityColor}">${t.priority}</span>
        </div>
        <div class="font-semibold text-gray-100">${escapeHtml(t.title)}</div>
        <p class="text-gray-400 text-[11px] line-clamp-2">${escapeHtml(t.description || 'No description provided.')}</p>
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
          logToTerminal(`[ACTION] Task ${taskId} suspended for consultation. Lock TTL frozen.`, 'amber');
          refreshData();
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
          logToTerminal(`[ACTION] Task ${taskId} resumed. Lock unfreezes and countdown continues.`, 'emerald');
          refreshData();
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
        container.innerHTML = '<div class="col-span-2 text-center text-gray-500 py-10">No advisors registered yet. Click "⚡ Seed Demo Data" above!</div>';
        return;
      }
      container.innerHTML = advisors.map(a => `
        <div class="bg-dark-card border border-purple-900/40 rounded-xl p-5 space-y-3 shadow-md">
          <div class="flex items-center justify-between">
            <div class="flex items-center space-x-2.5">
              <div class="w-8 h-8 rounded-lg bg-purple-950/80 border border-purple-700/50 flex items-center justify-center text-purple-300 font-bold">
                🧠
              </div>
              <div>
                <h3 class="text-sm font-bold text-white">${escapeHtml(a.name)}</h3>
                <span class="text-[10px] font-mono text-purple-400 bg-purple-950/40 border border-purple-800/40 px-2 py-0.5 rounded">${a.domain}</span>
              </div>
            </div>
            <span class="text-[11px] font-mono text-cyan-300 bg-cyan-950/40 border border-cyan-800/40 px-2 py-0.5 rounded">${a.reasoning_model}</span>
          </div>
          <p class="text-xs text-gray-300 leading-relaxed">${escapeHtml(a.system_prompt)}</p>
          <div class="pt-3 border-t border-dark-border flex items-center justify-between">
            <span class="text-[11px] text-gray-400">Status: <span class="text-emerald-400 font-semibold">${a.status}</span></span>
            <button onclick="promptConsultAdvisor('${a.id}', '${escapeHtml(a.name)}')" class="text-xs bg-purple-700 hover:bg-purple-600 text-white px-3 py-1 rounded-lg transition">Consult</button>
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

    // Copilot Query Interaction
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
        btn.innerText = 'Send Query';
        btn.disabled = false;
      }
    }

    // Create New Task
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
          refreshData();
        }
      } catch (err) {
        console.error(err);
      }
    }

    // Seed Demo Data
    async function seedDemoData() {
      const btn = document.getElementById('seedBtn');
      btn.innerText = 'Seeding...';
      btn.disabled = true;

      try {
        const res = await fetch('/api/v1/system/seed', { method: 'POST' });
        if (res.ok) {
          logToTerminal('[SEED] Demo squads, tasks, and advisors successfully seeded into database!', 'emerald');
          await refreshData();
          await fetchAdvisors();
        }
      } catch (err) {
        console.error(err);
      } finally {
        btn.innerText = '⚡ Seed Demo Data';
        btn.disabled = false;
      }
    }

    // Init on Load
    window.addEventListener('DOMContentLoaded', () => {
      initWebSocket();
      refreshData();
      fetchAdvisors();
      setInterval(refreshData, 10000); // 10s auto-poll
    });
  </script>
</body>
</html>
"""
