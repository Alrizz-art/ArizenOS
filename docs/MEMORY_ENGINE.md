# Arizen Memory Engine

> **Version:** 1.0.0 | **Status:** Implementation

The Memory Engine gives every ArizenOS agent durable, queryable, scoped
memory. It is built on top of the Knowledge Engine's storage and retrieval
infrastructure, with three purpose-built layers.

---

## Architecture

```
Agent / Commander
      │
      ▼
┌─────────────────────────────────────────────────────────┐
│                  MEMORY ENGINE                           │
│                                                          │
│  ┌─────────────────┐  ┌─────────────────┐               │
│  │  EpisodicBuffer │  │  ProjectMemory  │               │
│  │  (in-memory     │  │  (project-      │               │
│  │   ring buffer)  │  │   scoped LTM)   │               │
│  └────────┬────────┘  └────────┬────────┘               │
│           │                    │                         │
│           └────────┬───────────┘                         │
│                    ▼                                      │
│          ┌──────────────────┐                            │
│          │  LongTermMemory  │                            │
│          │  persistent      │                            │
│          │  session         │                            │
│          │  episodic (TTL)  │                            │
│          └───────┬──────────┘                            │
└──────────────────╪──────────────────────────────────────┘
                   │
        ┌──────────┴──────────┐
        ▼                     ▼
   ChromaDB              SQLite FTS5
   (semantic              (keyword +
    recall)               metadata +
                           TTL pruning)
```

---

## Memory Scopes

| Scope | TTL | Description |
|---|---|---|
| `persistent` | forever | User preferences, learned facts, key decisions |
| `episodic` | 7 days | Recent interactions, task outcomes |
| `session` | 1 hour | Current task working memory |

---

## Memory Layers

### 1. EpisodicBuffer (in-memory)

```python
engine.push_interaction(role="user",  content="fix the auth bug", agent="commander")
engine.push_interaction(role="agent", content="Applied patch...",  agent="fixer")
ctx = engine.episodic_context(n=6)   # last 6 turns as string
```

- Ring buffer (default 30 turns max)
- Never persisted to disk — cleared on process restart
- Used to prime the LLM with recent conversational context

### 2. LongTermMemory (ChromaDB + SQLite)

```python
# Store
record_id = await engine.store(
    "User always wants security scans before deployment",
    scope="persistent",
    tags=["preference", "security", "deployment"],
    importance=0.9,
)

# Query
records = await engine.query("deployment preferences", limit=5)
for r in records:
    print(r.content, r.importance, r.tags)
```

Importance scoring (0.0–1.0):
- `1.0` — critical system facts, irreversible decisions
- `0.8` — strong user preferences, architectural choices
- `0.5` — general learned knowledge (default)
- `0.2` — low-signal observations

### 3. ProjectMemory (LongTermMemory + project namespace)

```python
# Store project-scoped knowledge
await engine.store_project(
    "ArizenOS",
    "Chosen stack: SQLite WAL + ChromaDB dual-write for memory persistence",
    tags=["architecture", "storage"],
    record_type="decision",
    importance=0.9,
)

# Query project-specific memory
ctx = await engine.project_context("ArizenOS", "how is memory stored?")
# Returns formatted markdown block ready for LLM injection

# Full project summary
summary = await engine.project_summary("ArizenOS")
print(summary.as_context())  # topics, key decisions, record count
```

---

## MemoryRAGPipeline

The memory engine exposes a dedicated RAG pipeline scoped to the
`arizen_memory` ChromaDB collection:

```python
rag_ctx = await engine.rag_context("user coding preferences")
# Returns RAGContext with .prompt_block, .source_citations, .tokens_used

# In LLM prompt:
prompt = f"""
{SYSTEM_PROMPT}

{rag_ctx.prompt_block}

User: {query}
"""
```

The memory RAG uses the same Hybrid RRF fusion as the Knowledge Engine
but queries only the memory collection — not the full document index.

---

## Memory Agent Integration

The Memory agent (`agents/memory.py`) is the gatekeeper:

```
Commander → bus.delegate("memory", "memory.store", {...})
Commander → bus.delegate("memory", "memory.query", {"query": "..."})
Commander → bus.delegate("memory", "memory.forget", {"scope": "session"})
```

Playbook steps use the Memory agent:
```yaml
steps:
  - id: recall_context
    agent: memory
    tool: memory.query
    inputs:
      query: "{{ inputs.project_name }} architecture decisions"
      scope: persistent
      limit: 5
    output_var: prior_knowledge
```

---

## Retrieval Quality

### Hybrid Search (semantic + keyword)

Memory uses the same Reciprocal Rank Fusion approach as the Knowledge Engine:
- ChromaDB cosine similarity → semantic relevance
- SQLite FTS5 BM25 → keyword precision
- RRF merge → balanced ranking

### Importance-weighted Retrieval

After RRF fusion, records are re-sorted by:
```
final_score = rrf_score × importance
```

High-importance records (user preferences, architectural decisions) naturally
surface over low-importance observations for the same semantic query.

### TTL Pruning

```python
# Prune all expired records
pruned = await engine.forget()

# Prune specific scope
pruned = await engine.forget(scope="session")

# Prune all memory for a project
pruned = await engine.forget(project="old_project")
```

SQLite prunes expired records on every search query (lazy GC).
Explicit prune via `engine.forget()` for immediate cleanup.

---

## Storage Layout

```
memory/
├── chroma/                          ← ChromaDB persistent collections
│   ├── arizen_knowledge/            ← all ingested documents
│   ├── arizen_memory/               ← agent long-term memory
│   └── arizen_projects/             ← project-scoped memory
└── persistent/
    ├── knowledge.db                 ← SQLite: docs + chunks + memory + logs
    └── checkpoints.db               ← SQLite: playbook execution checkpoints
```

---

## Example: Full Memory Lifecycle

```python
# System boots → build MemoryEngine
chroma   = ChromaStore("memory/chroma")
sqlite   = SQLiteStore("memory/persistent/knowledge.db")
embedder = Embedder()
memory   = MemoryEngine(chroma, sqlite, embedder)

# User says: "I always prefer Rust for perf-critical code"
await memory.store(
    "User prefers Rust for performance-critical code",
    scope="persistent", tags=["preference","language","rust"], importance=0.85
)

# Commander handles "create project" → primes context
records = await memory.query("user language preferences", limit=5)
# → ["User prefers Rust for performance-critical code", ...]

# PlaybookEngine runs create_project playbook:
#   step: recall_prior_projects → memory.query("project ArizenOS rust")
#   step: scaffold_structure    → coder.code.generate (uses recalled context)
#   step: store_in_memory       → memory.store(scaffold_result)

# Project stores its decision:
await memory.store_project(
    "ArizenOS", "Used nomic-embed-text 768-dim for local embeddings",
    record_type="decision", importance=0.8
)

# Next session: Commander asks for project context
ctx = await memory.project_context("ArizenOS", "embedding model")
# → "## Project Memory: ArizenOS\n[1] Used nomic-embed-text..."

# User says: "forget everything about the old_experiment project"
await memory.forget(project="old_experiment")
```

---

## File Structure

```
knowledge/memory/
├── engine.py          ← MemoryEngine — primary interface for agents ✅
│                         store / query / store_project / project_context
│                         rag_context / episodic_context / forget / stats
├── long_term.py       ← LongTermMemory — 3 scopes, ChromaDB+SQLite dual-write ✅
│                         importance scoring, TTL management, hybrid retrieval
└── project_memory.py  ← ProjectMemory — project-scoped namespacing ✅
                          store/query/summarize/forget per project
```
