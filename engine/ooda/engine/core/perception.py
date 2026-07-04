"""
SOFI Perception Layer — Event-driven, no polling.

EventBus: async generator yielding filtered events.
NoiseFilter: rule-based, drops ~90% noise.
WebhookListener: FastAPI background thread.
LocalFileWatcher: watchdog-based, no polling.
"""

import asyncio
import json
import logging
import os
import threading
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, AsyncGenerator, Callable, Dict, List, Optional, Set

logger = logging.getLogger("sofi.perception")


# ── Event Schema ────────────────────────────────────────────────

@dataclass
class Event:
    """Single event from any source."""
    id: str = ""
    source: str = ""       # github|slack|email|file|api
    type: str = ""         # push|pr|issue|mention|file_change
    timestamp: str = ""
    raw: Dict = field(default_factory=dict)
    summary: str = ""      # one-line LLM summary
    entities: List[str] = field(default_factory=list)
    priority: float = 0.0  # 0.0–1.0
    requires_action: bool = False

    @classmethod
    def from_dict(cls, d: dict) -> "Event":
        return cls(
            id=d.get("id", str(uuid.uuid4())),
            source=d.get("source", "unknown"),
            type=d.get("type", "unknown"),
            timestamp=d.get("timestamp", datetime.now(timezone.utc).isoformat()),
            raw=d.get("raw", {}),
            summary=d.get("summary", ""),
            entities=d.get("entities", []),
            priority=d.get("priority", 0.0),
            requires_action=d.get("requires_action", False)
        )


# ── Noise Filter ────────────────────────────────────────────────

class NoiseFilter:
    """Rule-based filter: drops ~90% noise before LLM.

    Rules are cheap string/pattern checks — no LLM calls.
    """

    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.total = 0
        self.passed = 0
        self.dropped = 0

        # Ignored file patterns
        self.ignored_paths: Set[str] = set(self.config.get("ignored_paths", [
            "vendor/", "node_modules/", ".git/", "__pycache__/",
            "*.log", "*.min.js", "*.min.css", "dist/", "build/",
            ".env", ".DS_Store"
        ]))
        # Ignored email patterns
        self.ignored_email_patterns: List[str] = self.config.get("ignored_emails", [
            "out of office", "automatic reply", "mailer-daemon",
            "newsletter", "unsubscribe"
        ])
        # Low-priority event types (always dropped if not critical)
        self.low_priority_types: Set[str] = set(self.config.get("low_priority_types", [
            "typing", "presence_change", "reaction_added", "file_uploaded"
        ]))

    def filter(self, event: Event) -> bool:
        """True = event passes (is worthwhile). False = drop."""
        self.total += 1

        # 1. Check source-specific noise
        if event.source == "file" and self._is_ignored_path(event.raw.get("path", "")):
            self.dropped += 1
            return False

        if event.source == "email" and self._is_ignored_email(event.summary):
            self.dropped += 1
            return False

        if event.source == "slack" and event.type in self.low_priority_types:
            self.dropped += 1
            return False

        if event.source == "github" and event.type == "push":
            branch = event.raw.get("ref", "")
            if "feature/" in branch or "dependabot/" in branch:
                # Non-critical branch push — drop unless it's to main
                if "main" not in branch and "master" not in branch:
                    self.dropped += 1
                    return False

        # 2. Priority floor: events < 0.1 are dropped
        if event.priority < 0.1:
            self.dropped += 1
            return False

        # 3. Dedup: if same summary within 60s, drop
        # (implemented in EventBus via fingerprint map)

        self.passed += 1
        return True

    def _is_ignored_path(self, path: str) -> bool:
        for pat in self.ignored_paths:
            if pat.startswith("*.") and path.endswith(pat[1:]):
                return True
            if pat in path:
                return True
        return False

    def _is_ignored_email(self, subject: str) -> bool:
        subj_lower = subject.lower()
        for pat in self.ignored_email_patterns:
            if pat in subj_lower:
                return True
        return False

    def stats(self) -> Dict:
        return {
            "total": self.total,
            "passed": self.passed,
            "dropped": self.dropped,
            "drop_rate_pct": round(self.dropped / max(self.total, 1) * 100, 1)
        }


# ── Prioritizer ─────────────────────────────────────────────────

class Prioritizer:
    """Assigns priority (0.0–1.0) based on event source + type."""

    def __init__(self):
        self.rules = {
            "github": {
                "pr_review_requested": 0.9,
                "pr_opened": 0.8,
                "pr_merged": 0.7,
                "push_main": 0.7,
                "issue_opened": 0.6,
                "issue_comment": 0.5,
                "push": 0.3,
                "default": 0.2,
            },
            "slack": {
                "mention": 0.8,
                "direct_message": 0.8,
                "channel_message": 0.4,
                "thread_reply": 0.6,
                "default": 0.1,
            },
            "email": {
                "from_user": 0.9,
                "from_team": 0.6,
                "from_client": 0.8,
                "default": 0.1,
            },
            "file": {
                "config_change": 0.6,
                "code_change": 0.5,
                "critical": 0.8,
                "default": 0.2,
            },
            "api": {"default": 0.4},
        }

    def prioritize(self, event: Event) -> float:
        source_rules = self.rules.get(event.source, self.rules.get("api", {}))
        return source_rules.get(event.type, source_rules.get("default", 0.2))


# ── Webhook Listener ────────────────────────────────────────────

class WebhookListener:
    """Background HTTP server for receiving webhooks (GitHub, generic JSON)."""

    def __init__(self, host: str = "0.0.0.0", port: int = 8765):
        self.host = host
        self.port = port
        self.handlers: Dict[str, Callable] = {}
        self._server = None
        self._thread = None
        self._app = None

    def route(self, path: str, handler: Callable):
        """Register webhook path handler: handler(event_dict) -> Event."""
        self.handlers[path] = handler

    def start(self):
        """Start FastAPI server in background thread."""
        try:
            import uvicorn
            from fastapi import FastAPI, Request
        except ImportError:
            logger.warning("fastapi/uvicorn not installed. Webhooks unavailable.")
            return

        app = FastAPI(title="SOFI Webhooks", version="0.1.0")

        @app.post("/webhook/{source:path}")
        async def receive_webhook(source: str, request: Request):
            body = await request.json()
            event_dict = {
                "id": str(uuid.uuid4()),
                "source": source.split("/")[0],
                "type": request.headers.get("X-GitHub-Event", "webhook"),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "raw": body,
                "summary": f"Webhook from {source}: {str(body)[:100]}",
                "entities": [],
                "priority": 0.5,
                "requires_action": True,
            }
            event = Event.from_dict(event_dict)

            # Source-specific handler
            if source in self.handlers:
                event = self.handlers[source](body) or event

            # Push to global event bus
            from .perception import _global_bus
            if _global_bus:
                await _global_bus.emit(event)

            return {"status": "ok", "event_id": event.id}

        self._app = app
        self._thread = threading.Thread(
            target=lambda: uvicorn.run(app, host=self.host, port=self.port, log_level="warning"),
            daemon=True
        )
        self._thread.start()
        logger.info(f"Webhook listener on http://{self.host}:{self.port}")

    def stop(self):
        logger.info("Webhook listener stopped (thread daemon).")


# ── File Watcher ─────────────────────────────────────────────────

class LocalFileWatcher:
    """Event-driven file watcher via watchdog. No polling."""

    def __init__(self, paths: List[str], patterns: Optional[List[str]] = None):
        self.paths = paths
        self.patterns = patterns or ["*"]
        self._observer = None
        self._queue: asyncio.Queue = asyncio.Queue()
        self._ignore_dirs = {"vendor", "node_modules", ".git", "__pycache__", "dist", "build"}

    def start(self):
        try:
            from watchdog.observers import Observer
            from watchdog.events import FileSystemEventHandler
        except ImportError:
            logger.warning("watchdog not installed. File watcher unavailable.")
            return

        class _Handler(FileSystemEventHandler):
            def __init__(self, queue: asyncio.Queue, ignore_dirs: set):
                self.queue = queue
                self.ignore_dirs = ignore_dirs

            def _ignore(self, path: str) -> bool:
                parts = path.replace("\\", "/").split("/")
                return any(d in parts for d in self.ignore_dirs)

            def _emit(self, event_type: str, src_path: str):
                if self._ignore(src_path):
                    return
                ev = Event(
                    id=str(uuid.uuid4()),
                    source="file",
                    type=event_type,
                    timestamp=datetime.now(timezone.utc).isoformat(),
                    raw={"path": src_path, "event": event_type},
                    summary=f"{event_type}: {os.path.basename(src_path)}",
                    entities=[src_path],
                    priority=0.3,
                    requires_action=False,
                )
                try:
                    self.queue.put_nowait(ev)
                except asyncio.QueueFull:
                    pass

            def on_modified(self, e):
                self._emit("file_modified", e.src_path)

            def on_created(self, e):
                self._emit("file_created", e.src_path)

            def on_deleted(self, e):
                self._emit("file_deleted", e.src_path)

        handler = _Handler(self._queue, self._ignore_dirs)
        self._observer = Observer()
        for path in self.paths:
            if os.path.isdir(path):
                self._observer.schedule(handler, path, recursive=True)
        self._observer.start()
        logger.info(f"File watcher on {self.paths}")

    def stop(self):
        if self._observer:
            self._observer.stop()
            self._observer.join()

    async def events(self) -> AsyncGenerator[Event, None]:
        while True:
            try:
                event = await asyncio.wait_for(self._queue.get(), timeout=1.0)
                yield event
            except asyncio.TimeoutError:
                continue


# ── Global Event Bus ─────────────────────────────────────────────

_global_bus: Optional["EventBus"] = None


class EventBus:
    """Async event bus — single source of truth for all events.

    Usage:
        bus = EventBus()
        bus.register_adapter("github", webhook_listener)
        async for event in bus.stream():
            agent.process(event)
    """

    def __init__(self, noise_filter: Optional[NoiseFilter] = None):
        self._queue: asyncio.Queue = asyncio.Queue(maxsize=1000)
        self._filter = noise_filter or NoiseFilter()
        self._prioritizer = Prioritizer()
        self._adapters: Dict[str, Any] = {}
        self._fingerprints: Dict[str, float] = {}  # dedup within 60s
        self._running = False
        global _global_bus
        _global_bus = self

    def register_adapter(self, name: str, adapter: Any):
        """Register a source adapter."""
        self._adapters[name] = adapter
        logger.info(f"Adapter registered: {name}")

    async def emit(self, event: Event):
        """Push event into bus (from adapters)."""
        # Assign priority if not set
        if event.priority == 0.0:
            event.priority = self._prioritizer.prioritize(event)

        # Noise filter
        if not self._filter.filter(event):
            logger.debug(f"Dropped: [{event.source}] {event.summary[:60]}")
            return

        # Dedup: same summary within 60s
        fp = f"{event.source}:{event.summary}"
        now = time.time()
        if fp in self._fingerprints and now - self._fingerprints[fp] < 60:
            logger.debug(f"Dedup dropped: {fp[:60]}")
            return
        self._fingerprints[fp] = now
        # Clean old fingerprints
        for k in list(self._fingerprints.keys()):
            if now - self._fingerprints[k] > 120:
                del self._fingerprints[k]

        try:
            self._queue.put_nowait(event)
            logger.info(f"Event queued: [{event.source}/{event.type}] p={event.priority:.1f} — {event.summary[:80]}")
        except asyncio.QueueFull:
            logger.warning("Event queue full — dropping event")

    async def stream(self) -> AsyncGenerator[Event, None]:
        """Yield events one at a time. Blocking efficient."""
        self._running = True
        # Start adapters
        for name, adap in self._adapters.items():
            if hasattr(adap, "start"):
                if asyncio.iscoroutinefunction(adap.start):
                    await adap.start()
                else:
                    adap.start()

        logger.info(f"EventBus streaming — {len(self._adapters)} adapters, "
                     f"filter: {self._filter.stats()['drop_rate_pct']}% avg drop rate")

        while self._running:
            try:
                event = await asyncio.wait_for(self._queue.get(), timeout=0.5)
                yield event
            except asyncio.TimeoutError:
                continue

    def stop(self):
        self._running = False
        for name, adap in self._adapters.items():
            if hasattr(adap, "stop"):
                adap.stop()
        logger.info("EventBus stopped")
