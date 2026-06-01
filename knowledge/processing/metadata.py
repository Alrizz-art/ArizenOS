"""
Metadata extractor — enriches Documents with structured metadata before indexing.

Extracts:
  - language detection (code vs prose, language name)
  - estimated reading time
  - keyword extraction (TF-IDF approximation, no external model needed)
  - content type classification
  - named entity hints (regex-based: URLs, emails, file paths, version strings)
"""
from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass
from typing import Any

from knowledge.ingestion.base import Document


STOP_WORDS = {
    "a","an","the","and","or","but","in","on","at","to","for","of","with",
    "by","from","up","about","into","is","it","its","be","was","were","are",
    "has","had","have","that","this","these","those","as","not","no","so",
    "if","then","than","when","while","also","i","we","you","he","she","they",
}

CODE_TOKENS = {"def ","fn ","class ","impl ","import ","#include","function ","async def","export"}


@dataclass
class ExtractedMetadata:
    is_code:       bool
    language:      str        # "python" | "rust" | "typescript" | "prose" | "markdown" | ...
    content_type:  str        # "code" | "documentation" | "message" | "note" | "report"
    keywords:      list[str]
    reading_time_sec: int
    urls:          list[str]
    file_paths:    list[str]
    version_refs:  list[str]
    word_count:    int
    char_count:    int


class MetadataExtractor:
    """Enriches a Document with structured metadata."""

    def extract(self, doc: Document) -> dict[str, Any]:
        text   = doc.content
        source = doc.source
        ext    = doc.metadata.get("extension", "")

        is_code     = self._detect_code(text, ext, source)
        language    = self._detect_language(text, ext, source, is_code)
        content_type = self._detect_content_type(source, is_code)
        keywords    = self._extract_keywords(text, top_n=10)
        wcount      = len(text.split())
        reading_sec = max(1, wcount // 3)   # ~3 words/sec reading speed

        urls       = re.findall(r'https?://[^\s\'"<>]+', text)[:10]
        file_paths = re.findall(r'(?:^|[\s"])(/[\w/._-]+\.\w+)', text)[:10]
        versions   = re.findall(r'\bv?\d+\.\d+(?:\.\d+)?\b', text)[:5]

        return {
            "is_code":          is_code,
            "language":         language,
            "content_type":     content_type,
            "keywords":         keywords,
            "reading_time_sec": reading_sec,
            "urls_found":       urls,
            "file_paths_found": file_paths,
            "version_refs":     versions,
            "word_count":       wcount,
            "char_count":       len(text),
            **doc.metadata,   # source-specific metadata takes precedence
        }

    def _detect_code(self, text: str, ext: str, source: str) -> bool:
        if ext in {".py", ".rs", ".ts", ".tsx", ".js", ".jsx", ".go", ".c", ".cpp", ".h",
                   ".java", ".rb", ".php", ".swift", ".kt"}:
            return True
        if source == "github":
            return True
        code_hits = sum(1 for tok in CODE_TOKENS if tok in text[:2000])
        return code_hits >= 2

    def _detect_language(self, text: str, ext: str, source: str, is_code: bool) -> str:
        ext_map = {
            ".py": "python", ".rs": "rust", ".ts": "typescript", ".tsx": "typescript",
            ".js": "javascript", ".jsx": "javascript", ".go": "golang",
            ".c": "c", ".cpp": "cpp", ".h": "c", ".java": "java",
            ".rb": "ruby", ".md": "markdown", ".yaml": "yaml", ".toml": "toml",
        }
        if ext in ext_map:
            return ext_map[ext]
        if source == "markdown":
            return "markdown"
        if source == "notion":
            return "markdown"
        if not is_code:
            return "prose"
        # Heuristic fallback
        if "def " in text and "import " in text:
            return "python"
        if "fn " in text and "let " in text:
            return "rust"
        if "function " in text or "const " in text:
            return "javascript"
        return "unknown"

    def _detect_content_type(self, source: str, is_code: bool) -> str:
        if is_code:
            return "code"
        match source:
            case "telegram" | "discord":
                return "message"
            case "notion":
                return "note"
            case "markdown":
                return "documentation"
            case "pdf":
                return "report"
            case _:
                return "documentation"

    def _extract_keywords(self, text: str, top_n: int = 10) -> list[str]:
        words = re.findall(r'\b[a-zA-Z_][a-zA-Z0-9_]{2,}\b', text.lower())
        filtered = [w for w in words if w not in STOP_WORDS]
        counts = Counter(filtered)
        return [word for word, _ in counts.most_common(top_n)]
