# local_pdf_agent

A small, model-agnostic PDF agent skeleton. It provides PDF extraction and
preprocessing tools, relevant-chunk retrieval, and an HTTP adapter for
OpenAI-compatible local model servers.

## Install

```bash
python -m pip install -e .
```

## Run

```bash
local-pdf-agent document.pdf "Summarize the key findings" \
  --base-url http://localhost:11434/v1 \
  --model local-model
```

Use `--stub` to test PDF loading and retrieval without a model server.

## Python API

```python
from local_pdf_agent import Agent, LocalHTTPModel, PDFTools

tools = PDFTools()
document = tools.load("document.pdf")
agent = Agent(LocalHTTPModel(model="my-local-model"))
response = agent.run("Extract all dates and actions", document)
print(response.answer)
```

The `ModelAdapter` protocol can also be implemented directly for llama.cpp,
Ollama bindings, Transformers, or another on-device runtime.