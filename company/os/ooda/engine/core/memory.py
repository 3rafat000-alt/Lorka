#!/usr/bin/env python3
"""
Vector Memory Module — SOFI OODA Autonomous Agent
=================================================
Hybrid search (BM25 + vector) with ChromaDB backend.
Structured metadata, importance filtering, token counting, context compression.

Production: swap hash embedding for sentence-transformers or OpenAI embeddings.
"""

from __future__ import annotations

import hashlib
import json
import logging
import math
import os
import re
import sqlite3
import time
import uuid
from collections import Counter, defaultdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set, Tuple

import numpy as np

logger = logging.getLogger(__name__)

try:
    from pydantic import BaseModel, Field
    HAS_PYDANTIC = True
except ImportError:
    HAS_PYDANTIC = False

# ── Constants ──────────────────────────────────────────────────

MEMORY_TYPES: Set[str] = {
    "decision",
    "error",
    "insight",
    "context",
    "preference",
    "reflection",
}

SOURCES: Set[str] = {"slack", "email", "code", "human", "system"}

DEFAULT_EMBEDDING_DIM = 384
MAX_COMPRESS_TOKENS = 500
COMPRESS_TOP_K = 5
BM25_K1 = 1.5
BM25_B = 0.75


# ── Token counter ──────────────────────────────────────────────


def estimate_tokens(text: str) -> int:
    """Estimate token count for text.

    Approximation: 1 token ~ 4 Latin chars, 1 token ~ 1 CJK char.
    """
    if not text:
        return 0
    cjk = sum(
        1
        for c in text
        if "\u4e00" <= c <= "\u9fff"
        or "\u3040" <= c <= "\u309f"
        or "\uac00" <= c <= "\ud7af"
        or "\u3000" <= c <= "\u303f"
    )
    latin = len(text) - cjk
    return math.ceil(latin / 4) + cjk


def _hash_embed(text: str, dim: int = DEFAULT_EMBEDDING_DIM) -> List[float]:
    """Deterministic hash-based embedding for MVP.

    Uses SHA-256, truncates/pads to dim, L2-normalizes.
    Production: replace with sentence-transformers/all-MiniLM-L6-v2
    or OpenAI text-embedding-3-small.
    """
    h = hashlib.sha256(text.encode("utf-8")).digest()
    raw = np.frombuffer(h, dtype=np.uint8)
    if dim > len(raw):
        repeats = dim // len(raw) + 1
        raw = np.tile(raw, repeats)
    vec = raw[:dim].astype(np.float32)
    norm = np.linalg.norm(vec)
    if norm > 1e-12:
        vec = vec / norm
    return vec.tolist()


def _tokenize(text: str) -> List[str]:
    """Simple tokenizer: lowercase, split on non-alphanumeric, min 2 chars."""
    text = text.lower()
    tokens = re.findall(r"\b[a-z0-9]+\b", text)
    return [t for t in tokens if len(t) > 1]


# ── Schemas ────────────────────────────────────────────────────


if HAS_PYDANTIC:

    class MemoryMetadata(BaseModel):
        type: str = "context"
        project: str = "default"
        timestamp: str = ""
        importance: float = Field(default=0.5, ge=0.0, le=1.0)
        source: str = "system"
        tags: List[str] = Field(default_factory=list)

        def dump(self) -> Dict[str, Any]:
            return self.model_dump()

    class MemoryEntry(BaseModel):
        id: str = ""
        metadata: MemoryMetadata = Field(default_factory=MemoryMetadata)
        content: Dict[str, Any] = Field(default_factory=dict)
        text: str = ""
        vector: List[float] = Field(default_factory=list)
        token_count: int = 0

        class Config:
            arbitrary_types_allowed = True

else:
    from dataclasses import dataclass, field

    @dataclass
    class MemoryMetadata:
        type: str = "context"
        project: str = "default"
        timestamp: str = ""
        importance: float = 0.5
        source: str = "system"
        tags: List[str] = field(default_factory=list)

        def dump(self) -> Dict[str, Any]:
            return {
                "type": self.type,
                "project": self.project,
                "timestamp": self.timestamp,
                "importance": self.importance,
                "source": self.source,
                "tags": self.tags,
            }

    @dataclass
    class MemoryEntry:
        id: str = ""
        metadata: MemoryMetadata = field(default_factory=MemoryMetadata)
        content: Dict[str, Any] = field(default_factory=dict)
        text: str = ""
        vector: List[float] = field(default_factory=list)
        token_count: int = 0


# ── BM25 Index ─────────────────────────────────────────────────


class BM25Index:
    """In-memory BM25 keyword index for hybrid search pre-filter."""

    def __init__(self, k1: float = BM25_K1, b: float = BM25_B):
        self.k1 = k1
        self.b = b
        self.doc_count: int = 0
        self.doc_lengths: Dict[str, int] = {}
        self.avgdl: float = 0.0
        self.term_freqs: Dict[str, Counter] = defaultdict(Counter)
        self.doc_freqs: Counter = Counter()
        self.idf_cache: Dict[str, float] = {}
        self._dirty = True

    def add_document(self, doc_id: str, text: str) -> None:
        """Index a document's text for BM25 retrieval."""
        tokens = _tokenize(text)
        if not tokens:
            return
        self.doc_lengths[doc_id] = len(tokens)
        tf = Counter(tokens)
        self.term_freqs[doc_id] = tf
        for term in tf:
            self.doc_freqs[term] += 1
        self.doc_count += 1
        self._dirty = True

    def remove_document(self, doc_id: str) -> None:
        """Remove a document from the index."""
        if doc_id not in self.term_freqs:
            return
        for term in self.term_freqs[doc_id]:
            self.doc_freqs[term] -= 1
            if self.doc_freqs[term] <= 0:
                del self.doc_freqs[term]
        del self.term_freqs[doc_id]
        del self.doc_lengths[doc_id]
        self.doc_count -= 1
        self._dirty = True

    def _refresh_stats(self) -> None:
        """Recalculate average doc length and IDF cache."""
        if not self._dirty:
            return
        self.avgdl = (
            sum(self.doc_lengths.values()) / self.doc_count if self.doc_count else 0.0
        )
        self.idf_cache.clear()
        for term, df in self.doc_freqs.items():
            self.idf_cache[term] = math.log(
                1 + (self.doc_count - df + 0.5) / (df + 0.5)
            )
        self._dirty = False

    def score(self, query: str, doc_id: str) -> float:
        """BM25 score for a single query-document pair."""
        self._refresh_stats()
        if doc_id not in self.term_freqs:
            return 0.0
        query_tokens = _tokenize(query)
        if not query_tokens or not self.avgdl:
            return 0.0
        dl = self.doc_lengths[doc_id]
        tf = self.term_freqs[doc_id]
        score = 0.0
        for term in set(query_tokens):
            idf = self.idf_cache.get(term, 0.0)
            if idf <= 0:
                continue
            freq = tf.get(term, 0)
            numerator = freq * (self.k1 + 1)
            denominator = freq + self.k1 * (1 - self.b + self.b * dl / self.avgdl)
            score += idf * numerator / denominator
        return score

    def search(self, query: str, k: int = 10) -> List[Tuple[str, float]]:
        """Return top-k (doc_id, score) pairs sorted by BM25 score descending."""
        self._refresh_stats()
        query_tokens = _tokenize(query)
        if not query_tokens:
            return []
        scores: Dict[str, float] = {}
        for doc_id in self.term_freqs:
            s = self.score(query, doc_id)
            if s > 0:
                scores[doc_id] = s
        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return ranked[:k]

    def clear(self) -> None:
        """Reset the entire index."""
        self.doc_count = 0
        self.doc_lengths.clear()
        self.avgdl = 0.0
        self.term_freqs.clear()
        self.doc_freqs.clear()
        self.idf_cache.clear()
        self._dirty = True


# ── Vector Memory ──────────────────────────────────────────────


class VectorMemory:
    """Hybrid vector + keyword long-term memory.

    Backend: ChromaDB PersistentClient with SQLite metadata index.
    Embedding: hash-based deterministic (MVP). Swap for sentence-transformers in prod.
    Search: BM25 keyword pre-filter -> cosine vector rerank.
    Compression: hash-based truncation for long entries (>500 tokens), rerank by query.

    Config:
        memory.path: str = "/tmp/sofi-memory"
        memory.collection: str = "sofi_long_term"
        memory.embedding_dim: int = 384
        memory.backend: str = "chroma"
    """

    def __init__(self, config: Dict[str, Any]):
        cfg = config.get("memory", config)
        self.path: str = cfg.get("path", "/tmp/sofi-memory")
        self.collection_name: str = cfg.get("collection", "sofi_long_term")
        self.embedding_dim: int = cfg.get("embedding_dim", DEFAULT_EMBEDDING_DIM)
        self.backend: str = cfg.get("backend", "chroma")

        self.collection = None
        self.db_conn: Optional[sqlite3.Connection] = None
        self.bm25 = BM25Index()

        os.makedirs(self.path, exist_ok=True)
        self._init_sqlite()
        self._init_chroma()

        logger.info(
            "VectorMemory ready | path=%s collection=%s dim=%d backend=%s",
            self.path,
            self.collection_name,
            self.embedding_dim,
            self.backend,
        )

    # ── Initialization ─────────────────────────────────────────

    def _init_chroma(self) -> None:
        """Initialize ChromaDB PersistentClient collection."""
        try:
            import chromadb
            client = chromadb.PersistentClient(path=self.path)
            self.collection = client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"},
            )
            logger.debug("ChromaDB collection ready: %s", self.collection_name)
        except ImportError:
            logger.warning(
                "ChromaDB not installed — SQLite-only storage. "
                "Vector similarity search disabled."
            )
        except Exception as exc:
            logger.error("ChromaDB init failed: %s — using SQLite fallback", exc)

    def _init_sqlite(self) -> None:
        """Initialize SQLite metadata index with tagged columns."""
        db_path = os.path.join(self.path, "metadata.db")
        try:
            self.db_conn = sqlite3.connect(db_path)
            self.db_conn.row_factory = sqlite3.Row
            self.db_conn.execute("PRAGMA journal_mode=WAL")
            self.db_conn.execute("PRAGMA synchronous=NORMAL")

            self.db_conn.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    id            TEXT PRIMARY KEY,
                    type          TEXT NOT NULL,
                    project       TEXT NOT NULL DEFAULT 'default',
                    timestamp     TEXT NOT NULL,
                    importance    REAL NOT NULL DEFAULT 0.5,
                    source        TEXT NOT NULL DEFAULT 'system',
                    tags          TEXT NOT NULL DEFAULT '[]',
                    content       TEXT NOT NULL DEFAULT '{}',
                    doc_text      TEXT NOT NULL DEFAULT '',
                    vector        TEXT,
                    token_count   INTEGER NOT NULL DEFAULT 0,
                    created_at    REAL NOT NULL
                )
            """)
            self.db_conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_mem_type ON memories(type)"
            )
            self.db_conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_mem_importance ON memories(importance)"
            )
            self.db_conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_mem_timestamp ON memories(timestamp)"
            )
            self.db_conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_mem_project ON memories(project)"
            )
            self.db_conn.commit()
            logger.debug("SQLite metadata index ready: %s", db_path)
        except Exception as exc:
            logger.error("SQLite init failed: %s", exc)
            self.db_conn = None

    # ── Embedding ──────────────────────────────────────────────

    def _embed(self, text: str) -> List[float]:
        """Generate deterministic embedding vector for text.

        MVP: hash-based. Replace with sentence-transformers for production.
        """
        return _hash_embed(text, self.embedding_dim)

    def _make_search_text(self, entry: MemoryEntry) -> str:
        """Build a flat searchable text string from a memory entry."""
        parts = [entry.metadata.type, entry.text]
        if entry.content:
            parts.append(json.dumps(entry.content, ensure_ascii=False))
        return " ".join(parts)

    # ── Store ──────────────────────────────────────────────────

    def store(self, entry: MemoryEntry) -> MemoryEntry:
        """Persist a memory entry to all backends.

        Generates ID, timestamp, embedding, and token count.
        Stores in ChromaDB (vector), SQLite (metadata), and BM25 (keyword).
        """
        if not entry.id:
            entry.id = f"mem_{uuid.uuid4().hex[:16]}"
        if not entry.metadata.timestamp:
            entry.metadata.timestamp = datetime.now(timezone.utc).strftime(
                "%Y-%m-%dT%H:%M:%SZ"
            )

        search_text = self._make_search_text(entry)
        entry.vector = self._embed(search_text)
        entry.token_count = estimate_tokens(search_text)

        # ChromaDB vector store
        if self.collection is not None:
            try:
                self.collection.add(
                    ids=[entry.id],
                    embeddings=[entry.vector],
                    metadatas=[{
                        "type": entry.metadata.type,
                        "project": entry.metadata.project,
                        "timestamp": entry.metadata.timestamp,
                        "importance": entry.metadata.importance,
                        "source": entry.metadata.source,
                        "tags": json.dumps(entry.metadata.tags, ensure_ascii=False),
                    }],
                    documents=[search_text],
                )
            except Exception as exc:
                logger.error("ChromaDB store failed for %s: %s", entry.id, exc)

        # SQLite metadata index
        if self.db_conn is not None:
            try:
                self.db_conn.execute(
                    """
                    INSERT OR REPLACE INTO memories
                        (id, type, project, timestamp, importance, source,
                         tags, content, doc_text, vector, token_count, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        entry.id,
                        entry.metadata.type,
                        entry.metadata.project,
                        entry.metadata.timestamp,
                        entry.metadata.importance,
                        entry.metadata.source,
                        json.dumps(entry.metadata.tags, ensure_ascii=False),
                        json.dumps(entry.content, ensure_ascii=False),
                        entry.text,
                        json.dumps(entry.vector),
                        entry.token_count,
                        time.time(),
                    ),
                )
                self.db_conn.commit()
            except Exception as exc:
                logger.error("SQLite store failed for %s: %s", entry.id, exc)

        # BM25 keyword index
        self.bm25.add_document(entry.id, search_text)

        logger.info(
            "Memory stored | id=%s type=%s importance=%.2f tokens=%d",
            entry.id,
            entry.metadata.type,
            entry.metadata.importance,
            entry.token_count,
        )
        return entry

    # ── Retrieve ───────────────────────────────────────────────

    def retrieve(
        self,
        query: str,
        k: int = 5,
        min_importance: float = 0.0,
    ) -> List[Tuple[float, MemoryEntry]]:
        """Hybrid retrieve: BM25 keyword pre-filter then cosine vector rerank.

        Args:
            query: Natural language or keyword query.
            k: Number of results to return.
            min_importance: Minimum importance threshold (0.0 = no filter).

        Returns:
            List of (relevance_score, MemoryEntry) sorted descending by score.
        """
        bm25_results = self.bm25.search(query, k=k * 5)
        candidate_ids = [doc_id for doc_id, _ in bm25_results]

        if not candidate_ids and self.db_conn is not None:
            try:
                cursor = self.db_conn.execute(
                    "SELECT id FROM memories ORDER BY timestamp DESC LIMIT ?",
                    (k * 5,),
                )
                candidate_ids = [row["id"] for row in cursor.fetchall()]
            except Exception:
                pass

        query_vec = np.array(self._embed(query))
        results: List[Tuple[float, MemoryEntry]] = []

        for cid in candidate_ids:
            entry = self._load_entry(cid)
            if entry is None:
                continue
            if entry.metadata.importance < min_importance:
                continue

            entry_vec = np.array(entry.vector) if entry.vector else None
            if entry_vec is not None and np.linalg.norm(entry_vec) > 1e-12:
                sim = float(np.dot(query_vec, entry_vec))
                sim = max(-1.0, min(1.0, sim))
            else:
                sim = 0.0

            results.append((sim, entry))

        bm25_scores = dict(bm25_results)
        results.sort(
            key=lambda x: (x[0], bm25_scores.get(x[1].id, 0.0)), reverse=True
        )

        top = results[:k]
        logger.debug(
            "Retrieve | query=%s candidates=%d returned=%d min_imp=%.2f",
            query[:60],
            len(candidate_ids),
            len(top),
            min_importance,
        )
        return top

    def retrieve_by_tags(
        self,
        tags: List[str],
        k: int = 10,
    ) -> List[MemoryEntry]:
        """Retrieve memories containing all specified tags.

        Args:
            tags: List of tag strings (AND logic — all must match).
            k: Maximum results.

        Returns:
            Matching MemoryEntry list, sorted by importance desc.
        """
        if not tags or self.db_conn is None:
            return []

        try:
            tag_set = set(tags)
            cursor = self.db_conn.execute(
                "SELECT id, tags FROM memories ORDER BY importance DESC LIMIT ?",
                (k * 5,),
            )
            ids: List[str] = []
            for row in cursor.fetchall():
                stored_tags = set(json.loads(row["tags"]))
                if tag_set.issubset(stored_tags):
                    ids.append(row["id"])
                    if len(ids) >= k:
                        break
        except Exception as exc:
            logger.error("Tag query failed: %s", exc)
            return []

        entries = []
        for eid in ids:
            entry = self._load_entry(eid)
            if entry is not None:
                entries.append(entry)

        logger.debug("Retrieve by tags | tags=%s count=%d", tags, len(entries))
        return entries

    def retrieve_by_type(
        self,
        mem_type: str,
        k: int = 10,
    ) -> List[MemoryEntry]:
        """Retrieve memories of a specific type.

        Args:
            mem_type: One of MEMORY_TYPES.
            k: Maximum results.

        Returns:
            Matching MemoryEntry list, sorted by importance desc.
        """
        if mem_type not in MEMORY_TYPES:
            logger.warning("Unknown memory type: %s", mem_type)
            return []

        if self.db_conn is None:
            return []

        try:
            cursor = self.db_conn.execute(
                "SELECT id FROM memories WHERE type = ? "
                "ORDER BY importance DESC, timestamp DESC LIMIT ?",
                (mem_type, k),
            )
            ids = [row["id"] for row in cursor.fetchall()]
        except Exception as exc:
            logger.error("Type query failed: %s", exc)
            return []

        entries = []
        for eid in ids:
            entry = self._load_entry(eid)
            if entry is not None:
                entries.append(entry)

        logger.debug("Retrieve by type | type=%s count=%d", mem_type, len(entries))
        return entries

    def recent(self, count: int = 50) -> List[MemoryEntry]:
        """Return most recent memories by timestamp.

        Args:
            count: Maximum number to return.

        Returns:
            List of MemoryEntry sorted newest-first.
        """
        if self.db_conn is None:
            return []
        try:
            cursor = self.db_conn.execute(
                "SELECT id FROM memories ORDER BY timestamp DESC, created_at DESC LIMIT ?",
                (count,),
            )
            ids = [row["id"] for row in cursor.fetchall()]
        except Exception as exc:
            logger.error("Recent query failed: %s", exc)
            return []

        entries = []
        for eid in ids:
            entry = self._load_entry(eid)
            if entry is not None:
                entries.append(entry)
        return entries

    def count(self) -> int:
        """Return total number of stored memories."""
        if self.db_conn is None:
            return 0
        try:
            cursor = self.db_conn.execute("SELECT COUNT(*) AS cnt FROM memories")
            row = cursor.fetchone()
            return row["cnt"] if row else 0
        except Exception as exc:
            logger.error("Count query failed: %s", exc)
            return 0

    def delete_old(self, before: str) -> int:
        """Delete memories older than a given timestamp.

        Args:
            before: ISO 8601 timestamp. Entries with timestamp < before are removed.

        Returns:
            Number of entries deleted.
        """
        ids: List[str] = []

        if self.db_conn is not None:
            try:
                cursor = self.db_conn.execute(
                    "SELECT id FROM memories WHERE timestamp < ?",
                    (before,),
                )
                ids = [row["id"] for row in cursor.fetchall()]
                if ids:
                    placeholders = ",".join("?" for _ in ids)
                    self.db_conn.execute(
                        f"DELETE FROM memories WHERE id IN ({placeholders})",
                        ids,
                    )
                    self.db_conn.commit()
            except Exception as exc:
                logger.error("Delete old failed (SQLite): %s", exc)

        if self.collection is not None and ids:
            try:
                self.collection.delete(ids=ids)
            except Exception as exc:
                logger.warning("ChromaDB delete failed: %s", exc)

        for eid in ids:
            self.bm25.remove_document(eid)

        deleted = len(ids)
        if deleted:
            logger.info("Deleted %d memories older than %s", deleted, before)
        return deleted

    # ── Compression ────────────────────────────────────────────

    def compress(
        self,
        memories: List[MemoryEntry],
        query: str,
        top_k: int = COMPRESS_TOP_K,
    ) -> List[MemoryEntry]:
        """Compress and rerank memories for a query context.

        Long memories (>500 tokens) are hash-truncated:
        first 60% + last 40% with a separator.
        Remaining memories are reranked by cosine similarity to the query.

        Args:
            memories: Candidate memories to compress and rerank.
            query: Query string for relevance scoring.
            top_k: Number of compressed results to return (3-5 recommended).

        Returns:
            Compressed and reranked top_k MemoryEntry list.
        """
        if not memories:
            return []

        query_vec = np.array(self._embed(query)) if query else None
        scored: List[Tuple[float, MemoryEntry]] = []

        for mem in memories:
            if mem.token_count > MAX_COMPRESS_TOKENS:
                compressed = self._truncate_text(mem.text, MAX_COMPRESS_TOKENS)
                mem.text = compressed
                search_text = self._make_search_text(mem)
                mem.vector = self._embed(search_text)
                mem.token_count = estimate_tokens(search_text)

            if query_vec is not None and mem.vector:
                mem_vec = np.array(mem.vector)
                if np.linalg.norm(mem_vec) > 1e-12:
                    sim = float(np.dot(query_vec, mem_vec))
                    sim = max(-1.0, min(1.0, sim))
                else:
                    sim = 0.0
            else:
                sim = 0.0

            scored.append((sim, mem))

        scored.sort(key=lambda x: x[0], reverse=True)
        result = [mem for _, mem in scored[:top_k]]

        logger.debug(
            "Compressed %d -> %d memories | query=%s",
            len(memories),
            len(result),
            query[:60],
        )
        return result

    # ── Internal helpers ───────────────────────────────────────

    def _load_entry(self, entry_id: str) -> Optional[MemoryEntry]:
        """Load a single memory entry from the SQLite metadata index."""
        if self.db_conn is None:
            return None
        try:
            cursor = self.db_conn.execute(
                "SELECT * FROM memories WHERE id = ?",
                (entry_id,),
            )
            row = cursor.fetchone()
            if row is None:
                return None

            metadata = MemoryMetadata(
                type=row["type"],
                project=row["project"],
                timestamp=row["timestamp"],
                importance=row["importance"],
                source=row["source"],
                tags=json.loads(row["tags"]) if row["tags"] else [],
            )
            content = json.loads(row["content"]) if row["content"] else {}
            vector = json.loads(row["vector"]) if row["vector"] else []
            entry = MemoryEntry(
                id=row["id"],
                metadata=metadata,
                content=content,
                text=row["doc_text"],
                vector=vector,
                token_count=row["token_count"],
            )
            return entry

        except Exception as exc:
            logger.error("Failed to load entry %s: %s", entry_id, exc)
            return None

    @staticmethod
    def _truncate_text(text: str, max_tokens: int) -> str:
        """Hash-based truncation for long text.

        Keeps first ~60% and last ~40% of whitespace-delimited tokens
        with a summary marker. Cheap deterministic approach for MVP —
        no LLM call.
        """
        tokens = text.split()
        if len(tokens) <= max_tokens:
            return text

        head_count = int(max_tokens * 0.6)
        tail_count = max_tokens - head_count

        head = " ".join(tokens[:head_count])
        tail = " ".join(tokens[-tail_count:])
        removed = len(tokens) - max_tokens

        return (
            f"{head}\n"
            f"[... truncated: {removed} tokens ({len(tokens)} -> {max_tokens}) ...]\n"
            f"{tail}"
        )

    def __del__(self) -> None:
        """Clean up database connection on destruction."""
        if self.db_conn is not None:
            try:
                self.db_conn.close()
            except Exception:
                pass
