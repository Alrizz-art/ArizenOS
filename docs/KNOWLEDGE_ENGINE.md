# Arizen Knowledge Engine

> **Version:** 1.0.0 | **Status:** Implementation

The Knowledge Engine is the universal ingestion, indexing, and retrieval
layer for ArizenOS. It pulls knowledge from all configured sources,
deduplicates, chunks, embeds, and stores it for semantic search and RAG.

---

## Architecture

```
Data Sources                   Processing Pipeline              Storage
─────────────                  ────────────────────             ───────
GitHub  ──────────┐
Telegram ─────────┤             ┌─────────────────┐            ┌──────────────┐
Discord ──────────┤             │   MetadataEx-   │            │   ChromaDB   │
Notion ───────────┤──►[Connector]►  tractor        │──► embed ──►  (vectors)  │
Markdown ─────────┤             │   Chunker        │            └──────────────┘
PDF ──────────────┤             │   Embedder       │                   ▲
Local Files ──────┘             └─────────────────┘            ┌──────────────┐
                                                                │ SQLite FTS5  │
                                                                │ (metadata +  │
                                                                │  BM25 index) │
                                                                └──────────────┘

Query Layer
───────────
User/Agent query
     │
     ▼
SemanticSearch
  ├── ChromaDB (cosine similarity)     ─┐
  └── SQLite FTS5 (BM25 keyword)       ─┴── RRF Fusion ──► ranked SearchResult[]
                                                │
                                          RAGPipeline
                                                │
                                       score filter → dedup → pack → RAGContext
                                                │
                                       .prompt_block ──► LLM
```

---

## Data Flow

```
1. Connector.ingest() → AsyncIterator[Document]

2. For each Document:
   a. MetadataExtractor.extract(doc) → enriched metadata dict
      - language detection (prose / python / rust / typescript / ...)
      - content type (code / documentation / message / note)
      - keyword extraction (TF-IDF approximation, top 10)
      - named entity hints (URLs, file paths, version strings)
   b. SQLiteStore.upsert_document(doc) → is_new (bool, via checksum)
      - skip if checksum unchanged (incremental ingestion)
   c. Chunker.chunk(doc) → list[Chunk]
      - auto-selects strategy: recursive | markdown | code | sentence
   d. Embedder.embed_all(chunks) → chunks with .embedding filled
      - Ollama local model (nomic-embed-text, 768-dim)
      - falls back to zero-vector if Ollama unavailable
   e. ChromaStore.upsert_chunks(chunks) → vector index write
   f. SQLiteStore.upsert_chunks(chunks) → metadata index write

3. IngestResult returned with counts and errors
```

---

## Data Sources

### GitHub (`knowledge/ingestion/github.py`)
```yaml
sources:
  github:
    credentials:
      token: "${GITHUB_TOKEN}"
      repos: ["Alrizz-art/ArizenOS"]
      ingest: [readme, files, issues, prs, commits]
      file_exts: [.py, .rs, .ts, .md, .yaml, .toml]
```
Ingests: README, source files (whitelist by extension), issues, PRs, recent commits.
Rate-limited with courtesy sleep between file fetches.

### Telegram (`knowledge/ingestion/telegram.py`)
```yaml
sources:
  telegram:
    since_days: 90
    credentials:
      api_id: 12345
      api_hash: "${TELEGRAM_API_HASH}"
      session: "${TELEGRAM_SESSION}"
      targets: ["@arizendev", "me"]
```
Uses Telethon async client. Messages batched by day → one Document per channel/day.
`me` = Saved Messages (personal note channel).

### Discord (`knowledge/ingestion/discord_connector.py`)
```yaml
sources:
  discord:
    since_days: 60
    credentials:
      token: "Bot ${DISCORD_TOKEN}"
      guild_ids: ["1234567890"]
      channels: []   # empty = all text channels
```
Crawls guild channels via Discord REST API v10. Batches messages by day.

### Notion (`knowledge/ingestion/notion.py`)
```yaml
sources:
  notion:
    credentials:
      token: "${NOTION_TOKEN}"
      page_ids: ["abc123"]
      database_ids: ["def456"]
```
Recursively ingests pages and child pages. Block-to-Markdown conversion
preserves headings, code blocks, callouts, to-dos.

### Markdown (`knowledge/ingestion/markdown.py`)
```yaml
sources:
  markdown:
    credentials:
      paths: ["docs/", "README.md"]
      recursive: true
      exclude: ["node_modules", ".git"]
```
Extracts YAML front matter (title, tags, date). Handles `.md` and `.mdx`.

### PDF (`knowledge/ingestion/pdf.py`)
```yaml
sources:
  pdf:
    credentials:
      paths: ["papers/", "docs/reports/"]
      recursive: false
      ocr: false
```
Primary extractor: `pdfplumber`. Fallback: `pymupdf (fitz)`.
Files > 5 MB are skipped. OCR via pytesseract for scanned PDFs (optional).

### Local Files (`knowledge/ingestion/local_files.py`)
```yaml
sources:
  local:
    credentials:
      paths: ["."]
      recursive: true
      extensions: [.py, .rs, .ts, .md, .yaml, .toml, .txt]
      exclude: [node_modules, .git, __pycache__, dist, build]
```
Max file size: 5 MB. JSON files are pretty-printed for better chunking.

---

## Chunking Strategies

| Strategy | When auto-selected | Description |
|---|---|---|
| `recursive` | prose text (default) | Split on `\n\n` → `\n` → `. ` → ` ` |
| `markdown`  | `.md` / Notion | Split on `#` / `##` / `###` headers |
| `code`      | `.py` / `.rs` / `.ts` / GitHub source | Split on `def` / `class` / `fn` / `function` |
| `sentence`  | explicit | Split on `.!?` boundaries |
| `fixed`     | explicit | Fixed character window with overlap |

**Defaults:** `chunk_size=1200` chars, `chunk_overlap=200` chars.
Token count estimated at 4 chars/token.

---

## Embeddings

**Model:** `nomic-embed-text` (default) via Ollama  
**Dimension:** 768  
**Batch size:** 32 chunks per Ollama request  
**Cache:** in-memory `content_hash → embedding` (avoids re-embedding unchanged chunks)  
**Fallback:** zero-vector `[0.0] * 768` if Ollama unavailable — keyword search still works  

Alternative model: `mxbai-embed-large` (1024-dim, higher quality, slower)

---

## Storage

### ChromaDB (`memory/chroma/`)
```
Collections:
  arizen_knowledge  ← all source documents
  arizen_memory     ← agent long-term memory
  arizen_projects   ← project-scoped memory

Index: HNSW with cosine similarity
Metadata: str | int | float | bool (lists flattened to comma-separated strings)
```

### SQLite (`memory/persistent/knowledge.db`)
```sql
documents          — source registry, checksum dedup, URL, metadata JSON
documents_fts      — FTS5 virtual table with porter stemmer
chunks             — chunk registry, embedding presence flag
memory_records     — long-term memory records with TTL
memory_fts         — FTS5 virtual table for memory search
ingest_log         — ingestion audit trail
```

---

## Search

### Hybrid Search (default)

```python
results = await engine.search("ArizenOS checkpoint design", top_k=8)
```

```
1. Semantic search (ChromaDB cosine similarity) → top 16 results
2. Keyword search (SQLite FTS5 BM25)            → top 16 results
3. Reciprocal Rank Fusion (RRF k=60):
   score(doc) = Σ 1 / (60 + rank(doc))
4. Merge, deduplicate, return top_k
```

RRF consistently outperforms either method alone — especially for queries
that mix technical terms (BM25 strength) with semantic intent (vector strength).

### Semantic Only
```python
results = await engine.search(query, strategy="semantic")
```

### Keyword Only
```python
results = await engine.search(query, strategy="keyword")
```

### Source-filtered
```python
results = await engine.search(query, source="github")
```

---

## RAG Pipeline

```python
ctx = await engine.rag_context("how does the retry engine work?")
prompt = f"{SYSTEM_PROMPT}\n\n{ctx.prompt_block}\n\nUser: {query}"
```

```
RAGContext {
  .context_str       ← formatted chunk list
  .source_citations  ← [1] GITHUB: Alrizz-art/ArizenOS (score=0.847)
  .prompt_block      ← <knowledge_context>...</knowledge_context><sources>...</sources>
  .tokens_used       ← ~800
  .token_budget      ← 3000
  .sources           ← list[SearchResult]
}
```

**Pipeline:**
1. Hybrid search → top_k × 2 candidates
2. Score threshold filter (default 0.30) — always keep ≥ 3
3. Deduplicate: max 2 chunks per document
4. Pack: fit within token budget (3000 tokens ≈ 12 000 chars)
5. Format: numbered sections with header + content
6. Citations: source type + URL + score

---

## Configuration (`config/knowledge.yaml`)

```yaml
engine:
  chroma_path:   memory/chroma
  sqlite_path:   memory/persistent/knowledge.db
  embed_model:   nomic-embed-text
  chunk_size:    1200
  chunk_overlap: 200
  rag_top_k:     8
  rag_threshold: 0.30
  rag_tokens:    3000

sources:
  github:
    enabled: true
    since_days: 365
    credentials:
      token: "${GITHUB_TOKEN}"
      repos: ["Alrizz-art/ArizenOS"]
      ingest: [readme, files, issues]

  markdown:
    enabled: true
    credentials:
      paths: ["docs/", "README.md"]

  local:
    enabled: true
    credentials:
      paths: ["."]
      extensions: [.py, .rs, .ts, .md]
      exclude: [node_modules, .git, __pycache__, target, dist]

  telegram:
    enabled: false   # enable when credentials are ready
    credentials:
      api_id: "${TELEGRAM_API_ID}"
      api_hash: "${TELEGRAM_API_HASH}"
      session: "${TELEGRAM_SESSION}"
      targets: ["me"]

  discord:
    enabled: false
    credentials:
      token: "Bot ${DISCORD_TOKEN}"
      guild_ids: []

  notion:
    enabled: false
    credentials:
      token: "${NOTION_TOKEN}"
      page_ids: []

  pdf:
    enabled: false
    credentials:
      paths: []
```

---

## File Structure

```
knowledge/
├── engine.py                    ← KnowledgeEngine — main orchestrator ✅
├── ingestion/
│   ├── base.py                  ← Document, Chunk, SearchResult, BaseConnector ✅
│   ├── github.py                ← GitHub connector ✅
│   ├── telegram.py              ← Telegram connector ✅
│   ├── discord_connector.py     ← Discord connector ✅
│   ├── notion.py                ← Notion connector ✅
│   ├── markdown.py              ← Markdown connector ✅
│   ├── pdf.py                   ← PDF connector (pdfplumber + pymupdf) ✅
│   └── local_files.py           ← Local files connector ✅
├── processing/
│   ├── chunker.py               ← 5 chunking strategies (auto-select) ✅
│   ├── embedder.py              ← Ollama embedding + cache + fallback ✅
│   └── metadata.py              ← Language detection, keyword extraction ✅
├── storage/
│   ├── chroma_store.py          ← ChromaDB vector store ✅
│   └── sqlite_store.py          ← SQLite FTS5 + metadata store ✅
├── query/
│   ├── semantic_search.py       ← Hybrid RRF search ✅
│   └── rag.py                   ← RAG pipeline + MemoryRAGPipeline ✅
└── memory/
    ├── engine.py                ← MemoryEngine (primary interface) ✅
    ├── long_term.py             ← LongTermMemory (persist+episodic+session) ✅
    └── project_memory.py        ← ProjectMemory (scoped per project) ✅
```
