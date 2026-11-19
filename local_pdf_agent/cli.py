from __future__ import annotations

import argparse
import sys

from .agent import Agent
from .models import LocalHTTPModel, StubModel
from .pdf_tools import PDFTools


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Analyze a PDF with a local model")
    parser.add_argument("pdf")
    parser.add_argument("prompt")
    parser.add_argument("--base-url", default="http://localhost:11434/v1")
    parser.add_argument("--model", default="local-model")
    parser.add_argument("--api-key", default="not-needed")
    parser.add_argument("--stub", action="store_true", help="Use a local stub model")
    args = parser.parse_args(argv)

    tools = PDFTools()
    try:
        document = tools.load(args.pdf)
    except (FileNotFoundError, RuntimeError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    model = StubModel() if args.stub else LocalHTTPModel(
        base_url=args.base_url,
        model=args.model,
        api_key=args.api_key,
    )
    response = Agent(model, tools=tools).run(args.prompt, document)
    print(response.answer)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
