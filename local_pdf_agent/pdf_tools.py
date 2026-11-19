from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class PDFPage:
    number: int
    text: str


@dataclass(frozen=True)
class PDFDocument:
    path: str
    pages: tuple[PDFPage, ...]

    @property
    def page_count(self) -> int:
        return len(self.pages)

    @property
    def text(self) -> str:
        return "\n\n".join(
            f"[Page {page.number}]\n{page.text}" for page in self.pages
        )


class PDFTools:
    """Tools for extracting, normalizing, chunking, and searching PDFs."""

    def load(
        self,
        path: str | Path,
        *,
        start_page: int = 1,
        end_page: int | None = None,
    ) -> PDFDocument:
        try:
            from pypdf import PdfReader
        except ImportError as exc:
            raise RuntimeError(
                "PDF support requires pypdf. Install the project dependencies."
            ) from exc

        pdf_path = Path(path)
        if not pdf_path.is_file():
            raise FileNotFoundError(pdf_path)

        reader = PdfReader(str(pdf_path))
        if reader.is_encrypted:
            raise ValueError("Encrypted PDF files are not supported")

        total = len(reader.pages)
        first = max(1, start_page)
        last = min(total, end_page if end_page is not None else total)
        if first > last:
            return PDFDocument(path=str(pdf_path), pages=())

        pages = []
        for index in range(first - 1, last):
            text = reader.pages[index].extract_text() or ""
            pages.append(PDFPage(number=index + 1, text=self.normalize(text)))
        return PDFDocument(path=str(pdf_path), pages=tuple(pages))

    @staticmethod
    def normalize(text: str) -> str:
        text = text.replace("\u00a0", " ")
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r" +\n", "\n", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()

    def chunk(
        self,
        document: PDFDocument,
        *,
        chars_per_chunk: int = 4000,
        overlap: int = 200,
    ) -> list[str]:
        if chars_per_chunk <= 0:
            raise ValueError("chars_per_chunk must be positive")
        if overlap < 0 or overlap >= chars_per_chunk:
            raise ValueError("overlap must be non-negative and smaller than chars_per_chunk")

        chunks: list[str] = []
        for page in document.pages:
            if not page.text:
                continue
            start = 0
            while start < len(page.text):
                end = min(start + chars_per_chunk, len(page.text))
                chunks.append(f"[Page {page.number}] {page.text[start:end]}")
                if end == len(page.text):
                    break
                start = end - overlap
        return chunks

    def search(self, document: PDFDocument, query: str, limit: int = 5) -> list[str]:
        terms = [term.casefold() for term in re.findall(r"\w+", query) if term]
        if not terms:
            return []

        chunks = self.chunk(document)
        scored: list[tuple[int, str]] = []
        for chunk in chunks:
            lowered = chunk.casefold()
            score = sum(lowered.count(term) for term in terms)
            if score:
                scored.append((score, chunk))
        scored.sort(key=lambda item: item[0], reverse=True)
        return [chunk for _, chunk in scored[:limit]]
