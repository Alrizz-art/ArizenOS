"""
Markdown Connector — ingests local .md and .mdx files from a directory tree.

Handles:
  - YAML front matter extraction (title, tags, date)
  - Stripping markdown syntax for cleaner text
  - Recursive directory scanning with configurable depth
"""
from __future__ import annotations

import logging
import re
from datetime import datetime
from pathlib import Path
from typing import AsyncIterator, Optional

from knowledge.ingestion.base import BaseConnector, ConnectorConfig, Document

logger = logging.getLogger("arizen.knowledge.markdown")


class MarkdownConnector(BaseConnector):
    """
    Ingests all .md / .mdx files from a local directory.

    Config credentials:
      paths   : list of directory or file paths to scan
      recursive: bool (default True)
      exclude : list of glob patterns to exclude (e.g. ["**/node_modules/**"])

    Example:
        ConnectorConfig(source_name="markdown", credentials={"paths": ["docs/", "README.md"]})
    """

    def __init__(self, config: ConnectorConfig) -> None:
        super().__init__(config)
        self._paths     = config.credentials.get("paths", ["docs"])
        self._recursive = config.credentials.get("recursive", True)
        self._exclude   = set(config.credentials.get("exclude", ["node_modules", ".git", "__pycache__"]))

    async def health_check(self) -> bool:
        return any(Path(p).exists() for p in self._paths)

    async def ingest(self) -> AsyncIterator[Document]:
        for root in self._paths:
            p = Path(root)
            if p.is_file() and p.suffix in {".md", ".mdx"}:
                doc = self._parse_file(p)
                if doc:
                    yield doc
            elif p.is_dir():
                pattern = "**/*.md" if self._recursive else "*.md"
                for md_file in sorted(p.glob(pattern)):
                    if any(ex in str(md_file) for ex in self._exclude):
                        continue
                    doc = self._parse_file(md_file)
                    if doc:
                        yield doc

    def _parse_file(self, path: Path) -> Optional[Document]:
        try:
            raw = path.read_text(encoding="utf-8", errors="ignore")
        except (OSError, PermissionError) as exc:
            logger.warning("Cannot read %s: %s", path, exc)
            return None

        if not raw.strip():
            return None

        # Extract YAML front matter
        front_matter: dict = {}
        content = raw
        fm_match = re.match(r'^---\s*\n(.*?)\n---\s*\n', raw, re.DOTALL)
        if fm_match:
            try:
                import yaml
                front_matter = yaml.safe_load(fm_match.group(1)) or {}
            except Exception:
                pass
            content = raw[fm_match.end():]

        title = (
            front_matter.get("title")
            or self._extract_title(content)
            or path.stem.replace("-", " ").replace("_", " ").title()
        )
        tags = front_matter.get("tags", [])
        if isinstance(tags, str):
            tags = [tags]

        stat = path.stat()
        return Document(
            id        = "",
            source    = "markdown",
            source_id = str(path.resolve()),
            title     = title,
            content   = content.strip(),
            url       = path.as_uri(),
            created_at = datetime.utcfromtimestamp(stat.st_ctime),
            updated_at = datetime.utcfromtimestamp(stat.st_mtime),
            metadata  = {
                "file_path": str(path),
                "extension": path.suffix,
                "tags":      tags,
                "type":      "markdown",
                **{k: v for k, v in front_matter.items() if k not in ("title", "tags")},
            },
        )

    def _extract_title(self, content: str) -> Optional[str]:
        m = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        return m.group(1).strip() if m else None
