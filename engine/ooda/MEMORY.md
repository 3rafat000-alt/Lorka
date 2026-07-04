# Layer 2: Dual Memory — the dual-memory system

> SOFI operates with two memory systems: ephemeral context (short-term) and persistent vector storage (long-term).

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    DUAL MEMORY SYSTEM                        │
├─────────────────────────┬───────────────────────────────────┤
│   SHORT-TERM (L1)       │   LONG-TERM (L2)                 │
├─────────────────────────┼───────────────────────────────────┤
│ • Current session       │ • Vector DB (ChromaDB/pgvector)  │
│ • Active context window  │ • Past decisions & outcomes      │
│ • Last N observations   │ • Known failure patterns          │
│ • Tool call history     │ • Team preferences & personality  │
│ • Working state         │ • Reusable code patterns          │
│ • Volatile (lost on     │ • Persistent (survives restarts)  │
│   session end)          │ • Recency-weighted retrieval      │
└─────────────────────────┴───────────────────────────────────┘
```

## Short-Term Memory (L1)

Stored in the LLM context window. Managed via:

- **Sliding window**: keep last 50k tokens, oldest summarized
- **Session state**: JSON blob tracking current tasks, decisions, progress
- **Ephemeral cache**: Redis with TTL (default 3600s per key)

## Long-Term Memory (L2)

### Schema

Each memory entry:

```json
{
  "id": "mem_<ulid>",
  "type": "decision|error|pattern|preference|fact|reflection",
  "timestamp": "ISO8601",
  "vector": [0.1, 0.5, ...],   // embedding
  "content": {
    "summary": "Short description",
    "detail": "Full text / code / reasoning",
    "tags": ["security", "auth", "2fa"],
    "project": "PRJ-SAKK",
    "outcome": "success|failure|unknown"
  },
  "metadata": {
    "importance": 0.0–1.0,
    "access_count": 42,
    "last_accessed": "ISO8601"
  }
}
```

### Storage Backend

| Backend | Use Case | Config |
|---------|----------|--------|
| ChromaDB | Local dev, single-agent | `memory.backend: chroma` |
| pgvector | Production, multi-agent | `memory.backend: pgvector` |
| Pinecone | Cloud-scale, managed | `memory.backend: pinecone` |

### Retrieval

```python
def retrieve(self, query: str, k: int = 5, min_score: float = 0.6) -> List[Memory]:
    """Hybrid search: vector similarity + metadata filter + recency boost."""
    query_vec = self.embed(query)
    
    results = self.db.similarity_search(
        query_vec, 
        k=k * 2,  # fetch more for re-ranking
        filter={"project": self.project_id}
    )
    
    # Re-rank: boost recent + high-importance entries
    scored = []
    for r in results:
        recency_boost = 1.0 / (1 + hours_since(r.last_accessed))
        importance_boost = r.importance * 0.5
        score = r.similarity * 0.6 + recency_boost * 0.25 + importance_boost * 0.15
        scored.append((score, r))
    
    scored.sort(reverse=True)
    return [r for _, r in scored[:k] if r.similarity >= min_score]
```

### Memory Decay

- Entries with `access_count < 3` in 30 days → archived
- Archived entries not retrieved unless explicitly searched
- Importance decays by 0.01 per day without access

### Memory Consolidation

Every 24 hours, SOFI runs consolidation:
1. Cluster similar memories → merge into pattern
2. Delete low-importance expired entries
3. Re-embed updated entries
4. Generate weekly summary of learned patterns

## Dual Memory in Action

```
1. Observe: "Fix auth bug" ← perception
2. Retrieve L2: past auth bugs, similar fixes ← similar to query
3. L1 + L2 → reasoning: combine current context with past learning
4. Act: execute fix
5. Reflect: store outcome in L2 ← new memory entry
6. L1 updated: current state
```
