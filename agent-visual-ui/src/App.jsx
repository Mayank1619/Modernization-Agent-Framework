import { useEffect, useMemo, useState } from "react";

const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";
const DUAL_FLOW_STEPS = [
    {
        id: "primary",
        title: "OpenAI Agent",
        detail: "Primary generation phase"
    },
    {
        id: "claude",
        title: "Claude Agent",
        detail: "Secondary verification phase"
    },
    {
        id: "merge",
        title: "Compare + Merge",
        detail: "Reconcile and publish final output"
    }
];
const DUAL_PHASE_IDS = new Set(["primary", "claude", "merge"]);
const COST_RATES_PER_1K = {
    primary: { prompt: 0.00015, completion: 0.0006, label: "OpenAI primary (est)" },
    claude: { prompt: 0.0008, completion: 0.004, label: "Claude secondary (est)" },
    merge: { prompt: 0.00015, completion: 0.0006, label: "Merge via primary (est)" },
    single: { prompt: 0.00015, completion: 0.0006, label: "Single-model primary (est)" }
};

function deriveAgents(events) {
    const agents = new Map();
    for (const event of events) {
        if (event.event === "agent_started") {
            agents.set(event.agent, {
                name: event.agent,
                status: "running",
                durationSeconds: null,
                outputs: []
            });
        }
        if (event.event === "agent_completed") {
            agents.set(event.agent, {
                name: event.agent,
                status: "completed",
                durationSeconds: event.duration_seconds,
                outputs: event.outputs || []
            });
        }
        if (event.event === "agent_failed") {
            agents.set(event.agent, {
                name: event.agent,
                status: "failed",
                durationSeconds: null,
                outputs: []
            });
        }
    }
    return Array.from(agents.values());
}

function selectActivePhase(events) {
    const latestAgentEvent = [...events]
        .reverse()
        .find((event) => event.event === "agent_started" || event.event === "agent_completed");
    if (latestAgentEvent?.phase) {
        return latestAgentEvent.phase;
    }
    return "single";
}

function getPhaseEvents(events, activePhase) {
    if (activePhase === "single") {
        return events.filter((event) => !event.phase);
    }
    return events.filter((event) => event.phase === activePhase);
}

function buildAgentStatuses(enabledAgents, phaseEvents) {
    const agentState = new Map(
        enabledAgents.map((name) => [name, { name, status: "queued" }])
    );
    let latestRunning = "";
    let failedAgent = "";

    for (const event of phaseEvents) {
        if (!event.agent || !agentState.has(event.agent)) {
            continue;
        }
        if (event.event === "agent_started") {
            latestRunning = event.agent;
            agentState.set(event.agent, { name: event.agent, status: "running" });
            continue;
        }
        if (event.event === "agent_completed") {
            agentState.set(event.agent, { name: event.agent, status: "completed" });
            if (latestRunning === event.agent) {
                latestRunning = "";
            }
            continue;
        }
        if (event.event === "agent_failed") {
            failedAgent = event.agent;
            latestRunning = "";
            agentState.set(event.agent, { name: event.agent, status: "failed" });
        }
    }

    return {
        agents: enabledAgents.map((name) => agentState.get(name)),
        latestRunning,
        failedAgent
    };
}

function resolveOutputStatus(runStatus, completedCount, totalAgents) {
    if (runStatus === "failed") {
        return "failed";
    }
    if (completedCount === totalAgents && totalAgents > 0) {
        return "completed";
    }
    return "queued";
}

function resolvePulseIndex(enabledAgents, failedAgent, latestRunning, outputStatus, completedCount, nodeCount) {
    if (failedAgent) {
        return enabledAgents.indexOf(failedAgent) + 1;
    }
    if (latestRunning) {
        return enabledAgents.indexOf(latestRunning) + 1;
    }
    if (outputStatus === "completed") {
        return nodeCount - 1;
    }
    return Math.max(0, completedCount);
}

function deriveExecutionFlow(run) {
    const events = run?.events || [];
    const activePhase = selectActivePhase(events);
    const phaseEvents = getPhaseEvents(events, activePhase);

    const runStarted = [...phaseEvents]
        .reverse()
        .find((event) => event.event === "run_started");
    const enabledAgents = runStarted?.enabled_agents || [];

    const { agents, latestRunning, failedAgent } = buildAgentStatuses(enabledAgents, phaseEvents);
    const completedCount = agents.filter((agent) => agent.status === "completed").length;
    const outputStatus = resolveOutputStatus(run?.status, completedCount, enabledAgents.length);

    const laneNodes = [
        {
            id: "input",
            label: "Input",
            detail: run?.input_path || "-",
            status: run ? "completed" : "queued",
            kind: "io"
        },
        ...agents.map((agent) => ({
            id: agent.name,
            label: agent.name,
            detail: "Agent",
            status: agent.status,
            kind: "agent"
        })),
        {
            id: "output",
            label: "Output",
            detail: run?.output_path || "-",
            status: outputStatus,
            kind: "io"
        }
    ];

    const pulseIndex = resolvePulseIndex(
        enabledAgents,
        failedAgent,
        latestRunning,
        outputStatus,
        completedCount,
        laneNodes.length
    );

    return {
        activePhase,
        nodes: laneNodes,
        runningAgent: latestRunning,
        pulseIndex
    };
}

function deriveExecutionFlowForPhase(run, phase) {
    const events = run?.events || [];
    const phaseEvents = getPhaseEvents(events, phase);

    const runStarted = [...phaseEvents]
        .reverse()
        .find((event) => event.event === "run_started");
    const enabledAgents = runStarted?.enabled_agents || [];

    const { agents, latestRunning, failedAgent } = buildAgentStatuses(enabledAgents, phaseEvents);
    const completedCount = agents.filter((agent) => agent.status === "completed").length;
    const outputStatus = resolveOutputStatus(run?.status, completedCount, enabledAgents.length);

    const laneNodes = [
        {
            id: `${phase}-input`,
            label: "Input",
            detail: run?.input_path || "-",
            status: run ? "completed" : "queued",
            kind: "io"
        },
        ...agents.map((agent) => ({
            id: `${phase}-${agent.name}`,
            label: agent.name,
            detail: "Agent",
            status: agent.status,
            kind: "agent"
        })),
        {
            id: `${phase}-output`,
            label: "Output",
            detail: phase === "primary" ? "output_primary" : "output_claude",
            status: outputStatus,
            kind: "io"
        }
    ];

    const pulseIndex = resolvePulseIndex(
        enabledAgents,
        failedAgent,
        latestRunning,
        outputStatus,
        completedCount,
        laneNodes.length
    );

    return {
        activePhase: phase,
        nodes: laneNodes,
        runningAgent: latestRunning,
        pulseIndex
    };
}

async function fetchJson(path, options) {
    const response = await fetch(`${API_BASE}${path}`, options);
    if (!response.ok) {
        let detail = `HTTP ${response.status}`;
        try {
            const payload = await response.json();
            if (payload?.detail) {
                detail = payload.detail;
            }
        } catch {
            // Keep generic message if response is not JSON.
        }
        throw new Error(detail);
    }
    return response.json();
}

function getRunSignal(status) {
    if (status === "completed") {
        return "green";
    }
    if (status === "failed") {
        return "red";
    }
    if (status === "running") {
        return "yellow";
    }
    return "neutral";
}

function formatNumber(value) {
    const n = Number(value || 0);
    return Number.isFinite(n) ? n.toLocaleString() : "0";
}

function getTokenUsage(run) {
    const usage = run?.token_usage || {};
    return {
        prompt: Number(usage.prompt_tokens || 0),
        completion: Number(usage.completion_tokens || 0),
        total: Number(usage.total_tokens || 0),
        estimated: Number(usage.estimated_tokens || 0)
    };
}

function normalizeUsage(raw) {
    const prompt = Number(raw?.prompt_tokens || 0);
    const completion = Number(raw?.completion_tokens || 0);
    const total = Number(raw?.total_tokens || 0);
    const estimated = Number(raw?.estimated_tokens || 0);
    return {
        prompt: Number.isFinite(prompt) ? prompt : 0,
        completion: Number.isFinite(completion) ? completion : 0,
        total: Number.isFinite(total) ? total : 0,
        estimated: Number.isFinite(estimated) ? estimated : 0
    };
}

function addUsage(a, b) {
    return {
        prompt: a.prompt + b.prompt,
        completion: a.completion + b.completion,
        total: a.total + b.total,
        estimated: a.estimated + b.estimated
    };
}

function applyRunCompletedUsage(event, phases) {
    const phase = event.phase || "single";
    if (phase in phases) {
        phases[phase] = normalizeUsage(event.token_usage);
    }
    return Boolean(event.phase);
}

function applyEventTokenUsage(event, phases) {
    if (event.event === "run_completed" && event.token_usage) {
        return applyRunCompletedUsage(event, phases);
    }

    if (event.event === "merge_completed" && event.token_usage) {
        phases.merge = normalizeUsage(event.token_usage);
        return true;
    }

    return false;
}

function resolveTokenTotals(phases, sawDualPhase, run) {
    if (!sawDualPhase && run?.token_usage) {
        phases.single = normalizeUsage(run.token_usage);
    }

    const dualTotal = addUsage(addUsage(phases.primary, phases.claude), phases.merge);
    return {
        total: sawDualPhase ? dualTotal : phases.single,
        mode: sawDualPhase ? "dual" : "single"
    };
}

function derivePhaseTokenBreakdown(run) {
    const events = run?.events || [];
    const phases = {
        primary: normalizeUsage(),
        claude: normalizeUsage(),
        merge: normalizeUsage(),
        single: normalizeUsage()
    };

    let sawDualPhase = false;
    for (const event of events) {
        sawDualPhase = applyEventTokenUsage(event, phases) || sawDualPhase;
    }

    const { total, mode } = resolveTokenTotals(phases, sawDualPhase, run);
    return {
        phases,
        total,
        mode
    };
}

function estimateUsageCost(usage, phase) {
    const rate = COST_RATES_PER_1K[phase] || COST_RATES_PER_1K.single;
    return ((usage.prompt / 1000) * rate.prompt) + ((usage.completion / 1000) * rate.completion);
}

function formatCurrency(value) {
    return `$${Number(value || 0).toFixed(4)}`;
}

function applyPhaseStatusFromEvent(status, event) {
    const phase = event.phase;
    if (!DUAL_PHASE_IDS.has(phase)) {
        return;
    }

    const transitions = {
        phase_started: "running",
        phase_completed: "completed",
        run_completed: "completed",
        run_error: "failed"
    };
    const next = transitions[event.event];
    if (next) {
        status[phase] = next;
    }
}

function applyMergeStatusFromEvent(status, event) {
    if (event.event === "merge_started") {
        status.merge = "running";
    }
    if (event.event === "merge_completed") {
        status.merge = "completed";
    }
}

function finalizeDualFlowStatus(status, run) {
    if (run?.status === "completed" && run?.compare_with_claude) {
        for (const phaseId of DUAL_PHASE_IDS) {
            if (status[phaseId] === "idle") {
                status[phaseId] = "completed";
            }
        }
    }

    if (run?.status === "failed") {
        for (const phaseId of ["merge", "claude", "primary"]) {
            if (status[phaseId] === "running") {
                status[phaseId] = "failed";
                break;
            }
        }
    }
}

function deriveDualFlow(events, run) {
    const status = {
        primary: "idle",
        claude: "idle",
        merge: "idle"
    };

    let comparedArtifacts = 0;
    for (const event of events) {
        applyPhaseStatusFromEvent(status, event);
        applyMergeStatusFromEvent(status, event);
        if (event.event === "dual_model_summary") {
            comparedArtifacts = Number(event.artifacts_compared || 0);
        }
    }

    finalizeDualFlowStatus(status, run);
    return { status, comparedArtifacts };
}

function RunModeHints({ form }) {
    if (form.demo_mode) {
        return (
            <p className="hint">
                Demo mode runs non-AI primary, claude, and merge phases so you can visualize full flow without keys.
            </p>
        );
    }
    if (form.use_ai && !form.compare_with_claude) {
        return <p className="hint">AI mode uses primary provider credentials from env or request fields.</p>;
    }
    if (form.use_ai && form.compare_with_claude) {
        return (
            <p className="hint">
                Dual mode requires both primary AI key and Claude key. Missing keys will fail fast.
            </p>
        );
    }
    return null;
}

function ExecutionSignalPanel({
    run,
    runSignal,
    executionFlow,
    showDualFlow,
    primaryFlow,
    claudeFlow,
    dualFlow,
    completedCount,
    runningAgent,
    failedCount,
    tokenUsage
}) {
    return (
        <section className="panel flow-panel">
            <div className="flow-head">
                <h2>Execution Signal</h2>
                <span className={`status-pill ${runSignal}`}>{run?.status || "idle"}</span>
            </div>
            {showDualFlow ? (
                <>
                    <p className="flow-caption">
                        Parallel live workflows. OpenAI and Claude run side-by-side, then merge.
                    </p>
                    <div className="parallel-execution" role="img" aria-label="Parallel OpenAI and Claude execution workflows with merge">
                        <section className="workflow-column">
                            <h3>OpenAI Workflow</h3>
                            <p className="workflow-meta">
                                {primaryFlow.runningAgent
                                    ? `Running: ${primaryFlow.runningAgent}`
                                    : "Waiting for next agent"}
                            </p>
                            <div className="execution-vertical">
                                {primaryFlow.nodes.map((node, index) => (
                                    <div key={node.id} className={`exec-node vertical ${node.status} ${node.kind}`}>
                                        <span className="exec-dot" />
                                        <div>
                                            <span className="exec-label">{node.label}</span>
                                            <span className="exec-detail">{node.detail}</span>
                                        </div>
                                        {index < primaryFlow.nodes.length - 1 ? (
                                            <span className="exec-link vertical" aria-hidden="true" />
                                        ) : null}
                                    </div>
                                ))}
                                <div
                                    className={`exec-pulse vertical ${run?.status === "running" ? "moving" : ""}`}
                                    style={{ "--exec-step-y": String(primaryFlow.pulseIndex) }}
                                />
                            </div>
                        </section>

                        <section className="workflow-column">
                            <h3>Claude Workflow</h3>
                            <p className="workflow-meta">
                                {claudeFlow.runningAgent
                                    ? `Running: ${claudeFlow.runningAgent}`
                                    : "Waiting for next agent"}
                            </p>
                            <div className="execution-vertical">
                                {claudeFlow.nodes.map((node, index) => (
                                    <div key={node.id} className={`exec-node vertical ${node.status} ${node.kind}`}>
                                        <span className="exec-dot" />
                                        <div>
                                            <span className="exec-label">{node.label}</span>
                                            <span className="exec-detail">{node.detail}</span>
                                        </div>
                                        {index < claudeFlow.nodes.length - 1 ? (
                                            <span className="exec-link vertical" aria-hidden="true" />
                                        ) : null}
                                    </div>
                                ))}
                                <div
                                    className={`exec-pulse vertical ${run?.status === "running" ? "moving" : ""}`}
                                    style={{ "--exec-step-y": String(claudeFlow.pulseIndex) }}
                                />
                            </div>
                        </section>
                    </div>

                    <div className={`merge-stage ${dualFlow.status.merge}`}>
                        <h3>Merge + Compare</h3>
                        <p>Status: {dualFlow.status.merge}</p>
                        <p>Artifacts Compared: {dualFlow.comparedArtifacts || "-"}</p>
                    </div>
                </>
            ) : (
                <>
                    <p className="flow-caption">
                        Live phase: <strong>{executionFlow.activePhase}</strong>
                        {executionFlow.runningAgent
                            ? ` | Running: ${executionFlow.runningAgent}`
                            : " | Waiting for next agent"}
                    </p>
                    <div className="execution-lane" role="img" aria-label="Input to agent to output live process flow">
                        {executionFlow.nodes.map((node, index) => (
                            <div key={node.id} className={`exec-node ${node.status} ${node.kind}`}>
                                <span className="exec-dot" />
                                <div>
                                    <span className="exec-label">{node.label}</span>
                                    <span className="exec-detail">{node.detail}</span>
                                </div>
                                {index < executionFlow.nodes.length - 1 ? (
                                    <span className="exec-link" aria-hidden="true" />
                                ) : null}
                            </div>
                        ))}
                        <div
                            className={`exec-pulse ${run?.status === "running" ? "moving" : ""}`}
                            style={{ "--exec-step": String(executionFlow.pulseIndex) }}
                        />
                    </div>
                </>
            )}
            <div className="signal-grid">
                <article className="signal-card green">
                    <h3>Completed</h3>
                    <p>{completedCount}</p>
                </article>
                <article className="signal-card yellow">
                    <h3>Running</h3>
                    <p>{run?.status === "running" ? runningAgent || "Starting..." : "-"}</p>
                </article>
                <article className="signal-card red">
                    <h3>Failed</h3>
                    <p>{failedCount}</p>
                </article>
                <article className="signal-card blue">
                    <h3>Tokens</h3>
                    <p>{formatNumber(tokenUsage.total || tokenUsage.estimated)}</p>
                </article>
            </div>
        </section>
    );
}

function formatElapsedSeconds(seconds) {
    const safeSeconds = Math.max(0, Math.floor(seconds));
    const hrs = Math.floor(safeSeconds / 3600);
    const mins = Math.floor((safeSeconds % 3600) / 60);
    const secs = safeSeconds % 60;
    if (hrs > 0) {
        return `${String(hrs).padStart(2, "0")}:${String(mins).padStart(2, "0")}:${String(secs).padStart(2, "0")}`;
    }
    return `${String(mins).padStart(2, "0")}:${String(secs).padStart(2, "0")}`;
}

function computeElapsedSeconds(run, nowMs) {
    if (!run?.started_at) {
        return 0;
    }
    const startMs = Date.parse(run.started_at);
    const endMs = run.ended_at ? Date.parse(run.ended_at) : nowMs;
    if (Number.isNaN(startMs) || Number.isNaN(endMs)) {
        return 0;
    }
    return Math.max(0, Math.floor((endMs - startMs) / 1000));
}

export default function App() {
    const [form, setForm] = useState({
        pipeline: "mainframe_modernization",
        input_path: ".agentic-sdlc/examples/inqacc/legacy",
        output_path: ".agentic-sdlc/examples/inqacc/output",
        system_intent: ".agentic-sdlc/examples/inqacc/legacy/system-intent.md",
        use_ai: true,
        compare_with_claude: true,
        demo_mode: false,
        parallel_dual_run: true,
        optimize_tokens: true,
        token_max_sources: 12,
        token_preview_chars: 1400
    });
    const [runId, setRunId] = useState("");
    const [run, setRun] = useState(null);
    const [artifacts, setArtifacts] = useState([]);
    const [selectedArtifact, setSelectedArtifact] = useState("");
    const [artifactContent, setArtifactContent] = useState("");
    const [error, setError] = useState("");
    const [theme, setTheme] = useState(
        () => window.localStorage.getItem("agent-visual-theme") || "classic"
    );
    const [nowMs, setNowMs] = useState(Date.now());

    const agents = useMemo(() => deriveAgents(run?.events || []), [run]);
    const completedCount = agents.filter((agent) => agent.status === "completed").length;
    const failedCount = agents.filter((agent) => agent.status === "failed").length;
    const runningAgent = [...(run?.events || [])]
        .reverse()
        .find((event) => event.event === "agent_started")?.agent;
    const runSignal = getRunSignal(run?.status);
    const executionFlow = useMemo(() => deriveExecutionFlow(run), [run]);
    const showDualFlow = Boolean(run?.compare_with_claude || form.compare_with_claude || form.demo_mode);
    const primaryFlow = useMemo(() => deriveExecutionFlowForPhase(run, "primary"), [run]);
    const claudeFlow = useMemo(() => deriveExecutionFlowForPhase(run, "claude"), [run]);
    const dualFlow = useMemo(
        () => deriveDualFlow(run?.events || [], run),
        [run?.events, run?.status, run?.compare_with_claude]
    );
    const tokenUsage = useMemo(() => getTokenUsage(run), [run]);
    const phaseBreakdown = useMemo(() => derivePhaseTokenBreakdown(run), [run]);
    const displayedUsage = useMemo(() => {
        const hasRunUsage = (tokenUsage.total || tokenUsage.estimated || tokenUsage.prompt || tokenUsage.completion) > 0;
        return hasRunUsage ? tokenUsage : phaseBreakdown.total;
    }, [tokenUsage, phaseBreakdown]);
    const estimatedCostTotal = useMemo(() => {
        if (phaseBreakdown.mode === "dual") {
            return (
                estimateUsageCost(phaseBreakdown.phases.primary, "primary")
                + estimateUsageCost(phaseBreakdown.phases.claude, "claude")
                + estimateUsageCost(phaseBreakdown.phases.merge, "merge")
            );
        }
        return estimateUsageCost(phaseBreakdown.phases.single, "single");
    }, [phaseBreakdown]);
    const elapsedSeconds = useMemo(() => computeElapsedSeconds(run, nowMs), [run, nowMs]);

    useEffect(() => {
        document.documentElement.dataset.theme = theme;
        window.localStorage.setItem("agent-visual-theme", theme);
    }, [theme]);

    useEffect(() => {
        const timerId = setInterval(() => setNowMs(Date.now()), 1000);
        return () => clearInterval(timerId);
    }, []);

    useEffect(() => {
        if (!runId) {
            return undefined;
        }

        const tick = async () => {
            try {
                const nextRun = await fetchJson(`/api/runs/${runId}`);
                setRun(nextRun);
                const artifactResp = await fetchJson(`/api/runs/${runId}/artifacts`);
                setArtifacts(artifactResp.artifacts || []);
            } catch (err) {
                setError(String(err));
            }
        };

        tick();
        const id = setInterval(tick, 1500);
        return () => clearInterval(id);
    }, [runId]);

    const onStart = async (event) => {
        event.preventDefault();
        setError("");
        setSelectedArtifact("");
        setArtifactContent("");
        try {
            const result = await fetchJson("/api/runs/start", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(form)
            });
            setRun(null);
            setArtifacts([]);
            setRunId(result.run_id);
        } catch (err) {
            setError(String(err));
        }
    };

    const onReadArtifact = async (name) => {
        if (!runId) {
            return;
        }
        setSelectedArtifact(name);
        try {
            const payload = await fetchJson(
                `/api/runs/${runId}/artifacts/${encodeURIComponent(name)}`
            );
            setArtifactContent(payload.content || "");
        } catch (err) {
            setError(String(err));
        }
    };

    return (
        <div className="layout">
            <header>
                <h1>Agent Visual Dashboard</h1>
                <p>Watch input move through agents into outputs with live traffic-signal states.</p>
                <button
                    type="button"
                    className="theme-toggle"
                    onClick={() => setTheme((prev) => (prev === "classic" ? "neon" : "classic"))}
                >
                    Theme: {theme === "neon" ? "Neon" : "Classic"}
                </button>
            </header>

            <ExecutionSignalPanel
                run={run}
                runSignal={runSignal}
                executionFlow={executionFlow}
                showDualFlow={showDualFlow}
                primaryFlow={primaryFlow}
                claudeFlow={claudeFlow}
                dualFlow={dualFlow}
                completedCount={completedCount}
                runningAgent={runningAgent}
                failedCount={failedCount}
                tokenUsage={displayedUsage}
            />

            <section className="panel">
                <h2>Run Controls</h2>
                <form onSubmit={onStart} className="grid">
                    <label>
                        <span>Pipeline</span>
                        <input
                            value={form.pipeline}
                            onChange={(e) => setForm({ ...form, pipeline: e.target.value })}
                        />
                    </label>
                    <label>
                        <span>Input Path</span>
                        <input
                            value={form.input_path}
                            onChange={(e) => setForm({ ...form, input_path: e.target.value })}
                        />
                    </label>
                    <label>
                        <span>Output Path</span>
                        <input
                            value={form.output_path}
                            onChange={(e) => setForm({ ...form, output_path: e.target.value })}
                        />
                    </label>
                    <label>
                        <span>System Intent</span>
                        <input
                            value={form.system_intent}
                            onChange={(e) => setForm({ ...form, system_intent: e.target.value })}
                        />
                    </label>
                    <label className="check">
                        <input
                            type="checkbox"
                            checked={form.use_ai}
                            disabled={form.demo_mode}
                            onChange={(e) => setForm({ ...form, use_ai: e.target.checked })}
                        />
                        <span>Use AI</span>
                    </label>
                    <label className="check">
                        <input
                            type="checkbox"
                            checked={form.compare_with_claude || form.demo_mode}
                            disabled={form.demo_mode}
                            onChange={(e) => setForm({ ...form, compare_with_claude: e.target.checked })}
                        />
                        <span>Compare with Claude</span>
                    </label>
                    <label className="check">
                        <input
                            type="checkbox"
                            checked={form.demo_mode}
                            onChange={(e) => {
                                const enabled = e.target.checked;
                                setForm({
                                    ...form,
                                    demo_mode: enabled,
                                    use_ai: enabled ? false : form.use_ai,
                                    compare_with_claude: enabled ? true : form.compare_with_claude
                                });
                            }}
                        />
                        <span>Demo Mode (non-AI dual phases)</span>
                    </label>
                    <label className="check">
                        <input
                            type="checkbox"
                            checked={form.parallel_dual_run}
                            onChange={(e) => setForm({ ...form, parallel_dual_run: e.target.checked })}
                        />
                        <span>Run OpenAI + Claude in Parallel</span>
                    </label>
                    <label className="check">
                        <input
                            type="checkbox"
                            checked={form.optimize_tokens}
                            onChange={(e) => setForm({ ...form, optimize_tokens: e.target.checked })}
                        />
                        <span>Optimize Token Usage</span>
                    </label>
                    <label>
                        <span>Max Context Sources</span>
                        <input
                            type="number"
                            min={4}
                            max={30}
                            value={form.token_max_sources}
                            disabled={!form.optimize_tokens}
                            onChange={(e) =>
                                setForm({
                                    ...form,
                                    token_max_sources: Number(e.target.value || 12)
                                })
                            }
                        />
                    </label>
                    <label>
                        <span>Preview Chars Per Source</span>
                        <input
                            type="number"
                            min={400}
                            max={4000}
                            step={100}
                            value={form.token_preview_chars}
                            disabled={!form.optimize_tokens}
                            onChange={(e) =>
                                setForm({
                                    ...form,
                                    token_preview_chars: Number(e.target.value || 1400)
                                })
                            }
                        />
                    </label>
                    <button type="submit">Start Run</button>
                </form>
                {runId ? <p className="meta">Active Run ID: {runId}</p> : null}
                {run ? (
                    <p className="meta">
                        Run Status: {run.status}
                        <span className="timer-badge">Elapsed: {formatElapsedSeconds(elapsedSeconds)}</span>
                        <span className="timer-badge token">Tokens: {formatNumber(displayedUsage.total || displayedUsage.estimated)}</span>
                        <span className="timer-badge token">Estimated Cost: {formatCurrency(estimatedCostTotal)}</span>
                        <span className="timer-badge token-sub">
                            Prompt: {formatNumber(displayedUsage.prompt)} | Completion: {formatNumber(displayedUsage.completion)} | Est: {formatNumber(displayedUsage.estimated)}
                        </span>
                        {phaseBreakdown.mode === "dual" ? (
                            <span className="timer-badge token-sub">
                                Primary: {formatNumber(phaseBreakdown.phases.primary.total || phaseBreakdown.phases.primary.estimated)} | Claude: {formatNumber(phaseBreakdown.phases.claude.total || phaseBreakdown.phases.claude.estimated)} | Merge: {formatNumber(phaseBreakdown.phases.merge.total || phaseBreakdown.phases.merge.estimated)}
                            </span>
                        ) : null}
                    </p>
                ) : null}
                <RunModeHints form={form} />
                {error ? <p className="error">{error}</p> : null}
            </section>

            <section className="panel">
                <h2>Token and Cost Breakdown</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Phase</th>
                            <th>Prompt Tokens</th>
                            <th>Completion Tokens</th>
                            <th>Total Tokens</th>
                            <th>Estimated Cost</th>
                        </tr>
                    </thead>
                    <tbody>
                        {phaseBreakdown.mode === "dual" ? (
                            <>
                                <tr>
                                    <td>Primary</td>
                                    <td>{formatNumber(phaseBreakdown.phases.primary.prompt)}</td>
                                    <td>{formatNumber(phaseBreakdown.phases.primary.completion)}</td>
                                    <td>{formatNumber(phaseBreakdown.phases.primary.total || phaseBreakdown.phases.primary.estimated)}</td>
                                    <td>{formatCurrency(estimateUsageCost(phaseBreakdown.phases.primary, "primary"))}</td>
                                </tr>
                                <tr>
                                    <td>Claude</td>
                                    <td>{formatNumber(phaseBreakdown.phases.claude.prompt)}</td>
                                    <td>{formatNumber(phaseBreakdown.phases.claude.completion)}</td>
                                    <td>{formatNumber(phaseBreakdown.phases.claude.total || phaseBreakdown.phases.claude.estimated)}</td>
                                    <td>{formatCurrency(estimateUsageCost(phaseBreakdown.phases.claude, "claude"))}</td>
                                </tr>
                                <tr>
                                    <td>Merge</td>
                                    <td>{formatNumber(phaseBreakdown.phases.merge.prompt)}</td>
                                    <td>{formatNumber(phaseBreakdown.phases.merge.completion)}</td>
                                    <td>{formatNumber(phaseBreakdown.phases.merge.total || phaseBreakdown.phases.merge.estimated)}</td>
                                    <td>{formatCurrency(estimateUsageCost(phaseBreakdown.phases.merge, "merge"))}</td>
                                </tr>
                            </>
                        ) : (
                            <tr>
                                <td>Single</td>
                                <td>{formatNumber(phaseBreakdown.phases.single.prompt)}</td>
                                <td>{formatNumber(phaseBreakdown.phases.single.completion)}</td>
                                <td>{formatNumber(phaseBreakdown.phases.single.total || phaseBreakdown.phases.single.estimated)}</td>
                                <td>{formatCurrency(estimateUsageCost(phaseBreakdown.phases.single, "single"))}</td>
                            </tr>
                        )}
                        <tr>
                            <td><strong>Total</strong></td>
                            <td><strong>{formatNumber(phaseBreakdown.total.prompt)}</strong></td>
                            <td><strong>{formatNumber(phaseBreakdown.total.completion)}</strong></td>
                            <td><strong>{formatNumber(phaseBreakdown.total.total || phaseBreakdown.total.estimated)}</strong></td>
                            <td><strong>{formatCurrency(estimatedCostTotal)}</strong></td>
                        </tr>
                    </tbody>
                </table>
                <p className="hint">Cost uses model-rate estimates for showcase and may differ from billed provider totals.</p>
            </section>

            <section className="panel">
                <h2>Agent Activity</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Agent</th>
                            <th>Status</th>
                            <th>Duration (s)</th>
                            <th>Outputs</th>
                        </tr>
                    </thead>
                    <tbody>
                        {agents.map((agent) => (
                            <tr key={agent.name}>
                                <td>{agent.name}</td>
                                <td>
                                    <span className={`badge ${agent.status}`}>{agent.status}</span>
                                </td>
                                <td>
                                    {agent.durationSeconds == null
                                        ? "-"
                                        : agent.durationSeconds.toFixed(2)}
                                </td>
                                <td>{agent.outputs.join(", ") || "-"}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </section>

            <section className="panel split">
                <div>
                    <h2>Artifacts</h2>
                    <ul className="artifact-list">
                        {artifacts.map((name) => (
                            <li key={name}>
                                <button onClick={() => onReadArtifact(name)}>{name}</button>
                            </li>
                        ))}
                    </ul>
                </div>
                <div>
                    <h2>{selectedArtifact || "Artifact Viewer"}</h2>
                    <pre>{artifactContent || "Select an artifact to view content."}</pre>
                </div>
            </section>

            <section className="panel">
                <h2>Event Stream</h2>
                <div className="events">
                    {(run?.events || []).map((event, index) => (
                        <div key={`${event.timestamp}-${index}`} className={`event ${event.event}`}>
                            <strong>{event.timestamp}</strong> [{event.event}] {event.agent || ""}
                        </div>
                    ))}
                </div>
            </section>
        </div>
    );
}
