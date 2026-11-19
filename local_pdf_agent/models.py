from __future__ import annotations

import json
from typing import Protocol
from urllib import request


class ModelAdapter(Protocol):
    def generate(self, prompt: str) -> str:
        """Generate an answer for the supplied prompt."""


class StubModel:
    """Deterministic adapter useful for development and tests."""

    def generate(self, prompt: str) -> str:
        return "I need a local model adapter to generate an answer."


class LocalHTTPModel:
    """OpenAI-compatible adapter for an Ollama/vLLM/LM Studio server."""

    def __init__(
        self,
        base_url: str = "http://localhost:11434/v1",
        model: str = "local-model",
        api_key: str = "not-needed",
        timeout: float = 120.0,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.api_key = api_key
        self.timeout = timeout

    def generate(self, prompt: str) -> str:
        url = f"{self.base_url}/chat/completions"
        body = json.dumps({
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0,
            "stream": False,
        }).encode("utf-8")
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + self.api_key,
        }
        req = request.Request(url, data=body, headers=headers, method="POST")
        with request.urlopen(req, timeout=self.timeout) as response:
            payload = json.loads(response.read().decode("utf-8"))
        choices = payload.get("choices") or []
        if not choices:
            raise RuntimeError("Local model returned no choices")
        message = choices[0].get("message") or {}
        return message.get("content", "")
