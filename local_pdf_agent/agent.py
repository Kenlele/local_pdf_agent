from __future__ import annotations

from dataclasses import dataclass

from .models import ModelAdapter
from .pdf_tools import PDFDocument, PDFTools


@dataclass(frozen=True)
class AgentResponse:
    answer: str
    sources: tuple[str, ...]


class Agent:
    """A PDF-aware agent that retrieves relevant chunks before model generation."""

    def __init__(
        self,
        model: ModelAdapter,
        *,
        tools: PDFTools | None = None,
        context_limit: int = 5,
    ) -> None:
        self.model = model
        self.tools = tools or PDFTools()
        self.context_limit = context_limit

    def run(self, prompt: str, document: PDFDocument) -> AgentResponse:
        matches = self.tools.search(document, prompt, limit=self.context_limit)
        if matches:
            context = "\n\n".join(matches)
        else:
            context = document.text[: self.context_limit * 4000]

        full_prompt = (
            "You are analyzing a PDF. Answer the user's request using only the "
            "provided document context. When relevant, state the page number and "
            "do not invent information.\n\n"
            f"DOCUMENT CONTEXT:\n{context}\n\n"
            f"USER REQUEST:\n{prompt}"
        )
        return AgentResponse(
            answer=self.model.generate(full_prompt),
            sources=tuple(matches),
        )
