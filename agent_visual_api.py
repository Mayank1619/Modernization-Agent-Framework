from __future__ import annotations

import os
import sys
import threading
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


REPO_ROOT = Path(__file__).resolve().parent
FRAMEWORK_ROOT = REPO_ROOT / ".agentic-sdlc"
sys.path.insert(0, str(FRAMEWORK_ROOT))

from llm.factory import LlmSettings, build_llm_client, load_llm_settings  # noqa: E402
from orchestrator.config import load_pipeline_config  # noqa: E402
from orchestrator.dual_run import run_pipeline_dual_model  # noqa: E402
from orchestrator.pipeline import PipelineRunner  # noqa: E402


RUN_NOT_FOUND = "Run not found"
INVALID_ARTIFACT_NAME = "Invalid artifact name"
ARTIFACT_NOT_FOUND = "Artifact not found"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load_env_file(env_path: Path, locked_keys: set[str]) -> None:
    if not env_path.exists():
        return

    for line in env_path.read_text(encoding="utf-8").splitlines():
        text = line.strip()
        if not text or text.startswith("#") or "=" not in text:
            continue
        key, value = text.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in locked_keys:
            os.environ[key] = value


def load_local_dotenv(repo_root: Path) -> None:
    # Precedence: process env > .env.local > .env
    locked_keys = set(os.environ.keys())
    _load_env_file(repo_root / ".env", locked_keys)
    _load_env_file(repo_root / ".env.local", locked_keys)


@dataclass
class RunRecord:
    run_id: str
    status: str
    pipeline: str
    input_path: str
    output_path: str
    use_ai: bool
    compare_with_claude: bool
    demo_mode: bool
    parallel_dual_run: bool
    optimize_tokens: bool
    token_max_sources: int | None
    token_preview_chars: int | None
    started_at: str
    ended_at: str | None = None
    error: str | None = None
    events: List[Dict[str, object]] = field(default_factory=list)


class RunStore:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._runs: Dict[str, RunRecord] = {}

    def create(self, record: RunRecord) -> None:
        with self._lock:
            self._runs[record.run_id] = record

    def get(self, run_id: str) -> RunRecord:
        with self._lock:
            record = self._runs.get(run_id)
            if record is None:
                raise KeyError(run_id)
            return record

    def list(self) -> List[RunRecord]:
        with self._lock:
            return list(self._runs.values())

    def append_event(self, run_id: str, event: Dict[str, object]) -> None:
        with self._lock:
            record = self._runs.get(run_id)
            if record is None:
                return
            stamped = {
                "timestamp": _now_iso(),
                **event,
            }
            record.events.append(stamped)

    def complete(self, run_id: str, status: str, error: str | None = None) -> None:
        with self._lock:
            record = self._runs.get(run_id)
            if record is None:
                return
            record.status = status
            record.error = error
            record.ended_at = _now_iso()


class StartRunRequest(BaseModel):
    pipeline: str = "mainframe_modernization"
    input_path: str = ".agentic-sdlc/examples/inqacc/legacy"
    output_path: str = ".agentic-sdlc/examples/inqacc/output"
    system_intent: str | None = ".agentic-sdlc/examples/inqacc/legacy/system-intent.md"
    use_ai: bool = True
    compare_with_claude: bool = False
    demo_mode: bool = False
    parallel_dual_run: bool = True
    optimize_tokens: bool = True
    token_max_sources: int | None = None
    token_preview_chars: int | None = None
    ai_provider: str | None = None
    ai_model: str | None = None
    ai_base_url: str | None = None
    ai_api_key: str | None = None
    claude_model: str | None = None
    claude_base_url: str | None = None
    claude_api_key: str | None = None


app = FastAPI(title="Agent Visual API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

store = RunStore()


def _resolve_repo_path(path_text: str) -> Path:
    candidate = (REPO_ROOT / path_text).resolve()
    if candidate.exists():
        return candidate
    return (FRAMEWORK_ROOT / path_text).resolve()


def _apply_ai_env_overrides(request_data: StartRunRequest) -> None:
    effective_use_ai = request_data.use_ai and not request_data.demo_mode
    os.environ["AGENTIC_AI_ENABLED"] = "true" if effective_use_ai else "false"
    if request_data.ai_provider:
        os.environ["AGENTIC_AI_PROVIDER"] = request_data.ai_provider
    if request_data.ai_model:
        os.environ["AGENTIC_AI_MODEL"] = request_data.ai_model
    if request_data.ai_base_url:
        os.environ["AGENTIC_AI_BASE_URL"] = request_data.ai_base_url
    if request_data.ai_api_key:
        os.environ["AGENTIC_AI_API_KEY"] = request_data.ai_api_key


def _apply_token_optimization_overrides(request_data: StartRunRequest) -> None:
    if not request_data.optimize_tokens:
        return

    if request_data.token_max_sources is not None:
        os.environ["AGENTIC_CONTEXT_MAX_SOURCES"] = str(request_data.token_max_sources)
    else:
        os.environ.setdefault("AGENTIC_CONTEXT_MAX_SOURCES", "12")

    if request_data.token_preview_chars is not None:
        os.environ["AGENTIC_CONTEXT_PREVIEW_CHARS"] = str(
            request_data.token_preview_chars
        )
    else:
        os.environ.setdefault("AGENTIC_CONTEXT_PREVIEW_CHARS", "1400")


def _resolve_system_intent(system_intent_path: str | None) -> str:
    if not system_intent_path:
        return ""
    resolved = _resolve_repo_path(system_intent_path)
    if resolved.exists() and resolved.is_file():
        return str(resolved)
    return ""


def _build_claude_client(
    request_data: StartRunRequest,
    timeout_seconds: int,
):
    claude_model = (
        request_data.claude_model
        or os.getenv("AGENTIC_CLAUDE_MODEL", "claude-haiku-4-5-20251001")
    ).strip()
    claude_base_url = (
        request_data.claude_base_url
        or os.getenv("AGENTIC_CLAUDE_BASE_URL", "https://api.anthropic.com")
    ).strip()
    claude_api_key = (
        request_data.claude_api_key or os.getenv("AGENTIC_CLAUDE_API_KEY", "")
    ).strip()
    if not claude_api_key:
        raise ValueError("Claude API key is required for dual-model mode")

    client = build_llm_client(
        LlmSettings(
            enabled=True,
            provider="claude",
            model=claude_model,
            base_url=claude_base_url,
            api_key=claude_api_key,
            timeout_seconds=timeout_seconds,
        )
    )
    if client is None:
        raise ValueError("Unable to initialize Claude client")
    return client


def _run_single_model_pipeline(
    *,
    pipeline,
    templates_dir: Path,
    input_root: Path,
    output_root: Path,
    request_data: StartRunRequest,
    llm_client,
    system_intent_path: str,
    event_sink,
) -> None:
    runner = PipelineRunner(
        pipeline=pipeline,
        templates_dir=templates_dir,
        input_root=input_root,
        output_root=output_root,
        dry_run=not request_data.use_ai,
        llm_client=llm_client,
        extra_context={"system_intent_path": system_intent_path},
        event_sink=event_sink,
    )
    runner.run()


def _run_dual_model_pipeline(
    *,
    run_id: str,
    pipeline,
    templates_dir: Path,
    input_root: Path,
    output_root: Path,
    request_data: StartRunRequest,
    llm_settings,
    llm_client,
    system_intent_path: str,
    event_sink,
) -> None:
    if not request_data.demo_mode and llm_client is None:
        raise ValueError("Primary AI client is required for dual-model mode")

    secondary_client = None
    if not request_data.demo_mode:
        secondary_client = _build_claude_client(
            request_data=request_data,
            timeout_seconds=llm_settings.timeout_seconds,
        )

    comparisons = run_pipeline_dual_model(
        pipeline=pipeline,
        templates_dir=templates_dir,
        input_root=input_root,
        output_root=output_root,
        primary_client=None if request_data.demo_mode else llm_client,
        secondary_client=secondary_client,
        extra_context={"system_intent_path": system_intent_path},
        event_sink=event_sink,
        parallel=request_data.parallel_dual_run,
        primary_dry_run=request_data.demo_mode,
        secondary_dry_run=request_data.demo_mode,
        use_llm_merge=not request_data.demo_mode,
    )
    store.append_event(
        run_id,
        {
            "event": "dual_model_summary",
            "artifacts_compared": len(comparisons),
            "demo_mode": request_data.demo_mode,
        },
    )


def _serialize_record(record: RunRecord) -> Dict[str, object]:
    payload = asdict(record)
    start = datetime.fromisoformat(record.started_at)
    end = datetime.fromisoformat(record.ended_at) if record.ended_at else datetime.now(timezone.utc)
    payload["elapsed_seconds"] = max(0.0, (end - start).total_seconds())
    return payload


def _run_pipeline_task(run_id: str, request_data: StartRunRequest) -> None:
    try:
        load_local_dotenv(REPO_ROOT)

        _apply_ai_env_overrides(request_data)
        _apply_token_optimization_overrides(request_data)

        llm_settings = load_llm_settings()
        llm_client = build_llm_client(llm_settings)

        pipeline_path = FRAMEWORK_ROOT / "pipelines" / f"{request_data.pipeline}.yaml"
        pipeline = load_pipeline_config(pipeline_path)

        input_root = _resolve_repo_path(request_data.input_path)
        output_root = _resolve_repo_path(request_data.output_path)
        templates_dir = FRAMEWORK_ROOT / "templates"
        system_intent_path = _resolve_system_intent(request_data.system_intent)

        event_sink = lambda event: store.append_event(run_id, event)

        compare_enabled = request_data.compare_with_claude or request_data.demo_mode

        if compare_enabled:
            _run_dual_model_pipeline(
                run_id=run_id,
                pipeline=pipeline,
                templates_dir=templates_dir,
                input_root=input_root,
                output_root=output_root,
                request_data=request_data,
                llm_settings=llm_settings,
                llm_client=llm_client,
                system_intent_path=system_intent_path,
                event_sink=event_sink,
            )
        else:
            _run_single_model_pipeline(
                pipeline=pipeline,
                templates_dir=templates_dir,
                input_root=input_root,
                output_root=output_root,
                request_data=request_data,
                llm_client=llm_client,
                system_intent_path=system_intent_path,
                event_sink=event_sink,
            )

        store.complete(run_id, status="completed")
    except Exception as exc:
        store.append_event(
            run_id,
            {
                "event": "run_error",
                "error": str(exc),
            },
        )
        store.complete(run_id, status="failed", error=str(exc))


@app.get("/api/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.get("/api/runs")
def list_runs() -> List[Dict[str, object]]:
    records = sorted(store.list(), key=lambda rec: rec.started_at, reverse=True)
    return [_serialize_record(rec) for rec in records]


@app.post("/api/runs/start")
def start_run(request_data: StartRunRequest) -> Dict[str, str]:
    run_id = uuid.uuid4().hex
    effective_compare_with_claude = request_data.compare_with_claude or request_data.demo_mode
    record = RunRecord(
        run_id=run_id,
        status="running",
        pipeline=request_data.pipeline,
        input_path=request_data.input_path,
        output_path=request_data.output_path,
        use_ai=request_data.use_ai and not request_data.demo_mode,
        compare_with_claude=effective_compare_with_claude,
        demo_mode=request_data.demo_mode,
        parallel_dual_run=request_data.parallel_dual_run,
        optimize_tokens=request_data.optimize_tokens,
        token_max_sources=request_data.token_max_sources,
        token_preview_chars=request_data.token_preview_chars,
        started_at=_now_iso(),
    )
    store.create(record)
    thread = threading.Thread(target=_run_pipeline_task, args=(run_id, request_data), daemon=True)
    thread.start()
    return {"run_id": run_id}


@app.get("/api/runs/{run_id}", responses={404: {"description": RUN_NOT_FOUND}})
def get_run(run_id: str) -> Dict[str, object]:
    try:
        return _serialize_record(store.get(run_id))
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=RUN_NOT_FOUND) from exc


@app.get("/api/runs/{run_id}/artifacts", responses={404: {"description": RUN_NOT_FOUND}})
def list_artifacts(run_id: str) -> Dict[str, object]:
    try:
        record = store.get(run_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=RUN_NOT_FOUND) from exc

    output_root = _resolve_repo_path(record.output_path)
    if not output_root.exists():
        return {"artifacts": []}

    artifacts = [
        path.name
        for path in sorted(output_root.glob("*"))
        if path.is_file() and path.suffix.lower() in {".md", ".yaml", ".yml"}
    ]
    return {"artifacts": artifacts}


@app.get(
    "/api/runs/{run_id}/artifacts/{artifact_name}",
    responses={
        400: {"description": INVALID_ARTIFACT_NAME},
        404: {"description": ARTIFACT_NOT_FOUND},
    },
)
def read_artifact(run_id: str, artifact_name: str) -> Dict[str, str]:
    try:
        record = store.get(run_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=RUN_NOT_FOUND) from exc

    if "/" in artifact_name or "\\" in artifact_name:
        raise HTTPException(status_code=400, detail=INVALID_ARTIFACT_NAME)

    output_root = _resolve_repo_path(record.output_path)
    artifact_path = output_root / artifact_name
    if not artifact_path.exists() or not artifact_path.is_file():
        raise HTTPException(status_code=404, detail=ARTIFACT_NOT_FOUND)

    return {
        "name": artifact_name,
        "content": artifact_path.read_text(encoding="utf-8", errors="ignore"),
    }
