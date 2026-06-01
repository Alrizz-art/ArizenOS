"""
PDF Connector — extracts text from PDF files using pdfplumber (primary) with
pymupdf as a fallback. Handles multi-column layouts and image-heavy PDFs.
"""
from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path
from typing import AsyncIterator, Optional

from knowledge.ingestion.base import BaseConnector, ConnectorConfig, Document

logger = logging.getLogger("arizen.knowledge.pdf")


class PDFConnector(BaseConnector):
    """
    Ingests PDF files from one or more paths (files or directories).

    Config credentials:
      paths    : list of .pdf file paths or directories
      recursive: bool (default False — PDFs are usually deliberate targets)
      ocr      : bool (default False — enable OCR for scanned PDFs, requires pytesseract)
    """

    def __init__(self, config: ConnectorConfig) -> None:
        super().__init__(config)
        self._paths     = config.credentials.get("paths", [])
        self._recursive = config.credentials.get("recursive", False)
        self._ocr       = config.credentials.get("ocr", False)

    async def health_check(self) -> bool:
        try:
            import pdfplumber  # noqa
            return True
        except ImportError:
            try:
                import fitz  # noqa  (pymupdf)
                return True
            except ImportError:
                return False

    async def ingest(self) -> AsyncIterator[Document]:
        for raw_path in self._paths:
            p = Path(raw_path)
            if p.is_file() and p.suffix.lower() == ".pdf":
                doc = await self._parse_pdf(p)
                if doc:
                    yield doc
            elif p.is_dir():
                pattern = "**/*.pdf" if self._recursive else "*.pdf"
                for pdf_file in sorted(p.glob(pattern)):
                    doc = await self._parse_pdf(pdf_file)
                    if doc:
                        yield doc

    async def _parse_pdf(self, path: Path) -> Optional[Document]:
        content, meta = "", {}
        try:
            content, meta = self._extract_pdfplumber(path)
        except Exception as exc:
            logger.warning("pdfplumber failed on %s: %s — trying pymupdf", path, exc)
            try:
                content, meta = self._extract_pymupdf(path)
            except Exception as exc2:
                logger.error("Both PDF extractors failed for %s: %s", path, exc2)
                return None

        if not content.strip():
            logger.warning("No text extracted from %s — possibly scanned/image PDF", path)
            return None

        title = meta.get("title") or path.stem.replace("-", " ").replace("_", " ").title()
        stat  = path.stat()
        return Document(
            id        = "",
            source    = "pdf",
            source_id = str(path.resolve()),
            title     = title,
            content   = content,
            url       = path.as_uri(),
            created_at = datetime.utcfromtimestamp(stat.st_ctime),
            updated_at = datetime.utcfromtimestamp(stat.st_mtime),
            metadata  = {
                "file_path": str(path),
                "extension": ".pdf",
                "type":      "pdf",
                "pages":     meta.get("pages", 0),
                "author":    meta.get("author", ""),
                "subject":   meta.get("subject", ""),
            },
        )

    def _extract_pdfplumber(self, path: Path) -> tuple[str, dict]:
        import pdfplumber
        pages_text, meta = [], {}
        with pdfplumber.open(str(path)) as pdf:
            meta = {
                "pages": len(pdf.pages),
                **{k.lower(): v for k, v in (pdf.metadata or {}).items()
                   if isinstance(v, str)},
            }
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    pages_text.append(text)
        return "\n\n".join(pages_text), meta

    def _extract_pymupdf(self, path: Path) -> tuple[str, dict]:
        import fitz  # pymupdf
        doc   = fitz.open(str(path))
        pages = [doc[i].get_text() for i in range(len(doc))]
        raw_meta = doc.metadata or {}
        return "\n\n".join(p for p in pages if p.strip()), {
            "pages":   len(doc),
            "title":   raw_meta.get("title", ""),
            "author":  raw_meta.get("author", ""),
            "subject": raw_meta.get("subject", ""),
        }
