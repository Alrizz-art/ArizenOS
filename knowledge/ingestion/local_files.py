"""
Local Files Connector — ingests text-based files from the local filesystem.

Supported extensions: .txt, .log, .json, .yaml, .toml, .csv, .xml, .html,
                      .py, .rs, .ts, .js, .go, .c, .cpp, .sh, .sql
"""
from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import AsyncIterator

from knowledge.ingestion.base import BaseConnector, ConnectorConfig, Document

logger = logging.getLogger("arizen.knowledge.localfiles")

SUPPORTED_EXTS = {
    ".txt", ".log", ".json", ".yaml", ".yml", ".toml", ".csv", ".xml", ".html",
    ".py", ".rs", ".ts", ".tsx", ".js", ".jsx", ".go", ".c", ".cpp", ".h",
    ".sh", ".bash", ".sql", ".env.example", ".gitignore", ".dockerfile",
}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB


class LocalFilesConnector(BaseConnector):
    """
    Ingests text files from one or more local paths.

    Config credentials:
      paths    : list of file paths or directories
      recursive: bool (default True)
      exclude  : list of partial path strings to skip
      extensions: list of file extensions (overrides SUPPORTED_EXTS)
    """

    def __init__(self, config: ConnectorConfig) -> None:
        super().__init__(config)
        self._paths    = config.credentials.get("paths", ["."])
        self._recursive = config.credentials.get("recursive", True)
        self._exclude   = set(config.credentials.get("exclude", [
            "node_modules", ".git", "__pycache__", ".venv", "venv",
            "dist", "build", ".DS_Store",
        ]))
        self._exts = set(config.credentials.get("extensions", list(SUPPORTED_EXTS)))

    async def health_check(self) -> bool:
        return any(Path(p).exists() for p in self._paths)

    async def ingest(self) -> AsyncIterator[Document]:
        for root in self._paths:
            p = Path(root)
            if p.is_file():
                doc = self._read_file(p)
                if doc:
                    yield doc
            elif p.is_dir():
                pattern = "**/*" if self._recursive else "*"
                for f in sorted(p.glob(pattern)):
                    if not f.is_file():
                        continue
                    if any(ex in str(f) for ex in self._exclude):
                        continue
                    if f.suffix.lower() not in self._exts:
                        continue
                    if f.stat().st_size > MAX_FILE_SIZE:
                        logger.debug("Skipping large file: %s (%d bytes)", f, f.stat().st_size)
                        continue
                    doc = self._read_file(f)
                    if doc:
                        yield doc

    def _read_file(self, path: Path) -> None:
        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
        except (OSError, PermissionError) as exc:
            logger.warning("Cannot read %s: %s", path, exc)
            return None
        if not content.strip():
            return None
        # For JSON, pretty-print to make it more readable/chunkable
        if path.suffix == ".json":
            try:
                content = json.dumps(json.loads(content), indent=2, ensure_ascii=False)
            except json.JSONDecodeError:
                pass
        stat = path.stat()
        return Document(
            id        = "",
            source    = "local",
            source_id = str(path.resolve()),
            title     = path.name,
            content   = content,
            url       = path.as_uri(),
            created_at = datetime.utcfromtimestamp(stat.st_ctime),
            updated_at = datetime.utcfromtimestamp(stat.st_mtime),
            metadata  = {
                "file_path": str(path),
                "file_name": path.name,
                "extension": path.suffix.lower(),
                "size_bytes": stat.st_size,
                "type":       "file",
            },
        )
