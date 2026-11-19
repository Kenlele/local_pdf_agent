#!/usr/bin/env python3
"""Lightweight PDF inspection CLI for Pi Agent tools."""

import argparse
import contextlib
import io
import json
import re
import sys
from pathlib import Path

import pymupdf


def open_pdf(pdf_path: str) -> tuple[pymupdf.Document, Path]:
    path = Path(pdf_path).expanduser().resolve()
    if not path.exists():
        raise FileNotFoundError(f"PDF file not found: {path}")
    if not path.is_file():
        raise ValueError(f"Path is not a file: {path}")
    doc = pymupdf.open(str(path))
    return doc, path


def cmd_outline(args: argparse.Namespace) -> None:
    doc, path = open_pdf(args.pdf_path)
    try:
        toc = doc.get_toc(simple=True)
        outline = [
            {"level": level, "title": title.strip(), "page": page}
            for level, title, page in toc
        ]
        result = {
            "path": str(path),
            "pages": doc.page_count,
            "metadata": {
                "title": (doc.metadata or {}).get("title") or "",
                "author": (doc.metadata or {}).get("author") or "",
            },
            "outline": outline[: args.max_items],
            "outline_total": len(outline),
        }
        print(json.dumps(result, ensure_ascii=False, indent=2))
    finally:
        doc.close()


def cmd_search(args: argparse.Namespace) -> None:
    doc, path = open_pdf(args.pdf_path)
    try:
        query = args.query.strip()
        if not query:
            raise ValueError("Search query cannot be empty")

        pattern = re.compile(re.escape(query), re.IGNORECASE)
        hits = []
        for idx in range(doc.page_count):
            text = doc.load_page(idx).get_text("text") or ""
            matches = list(pattern.finditer(text))
            if not matches:
                continue
            snippets = []
            for m in matches[:3]:
                start = max(0, m.start() - 80)
                end = min(len(text), m.end() + 120)
                snippet = re.sub(r"\s+", " ", text[start:end]).strip()
                snippets.append(snippet)
            hits.append(
                {
                    "page": idx + 1,
                    "count": len(matches),
                    "snippets": snippets,
                }
            )
            if len(hits) >= args.max_hits:
                break

        result = {
            "path": str(path),
            "query": query,
            "total_pages": doc.page_count,
            "matched_pages": len(hits),
            "hits": hits,
        }
        print(json.dumps(result, ensure_ascii=False, indent=2))
    finally:
        doc.close()


def extract_page_markdown(doc: pymupdf.Document, page_index: int) -> str:
    page = doc.load_page(page_index)
    text = (page.get_text("text") or "").strip()
    tables_md = []
    try:
        for table in page.find_tables():
            md = table.to_markdown()
            if md and md.strip():
                tables_md.append(md.strip())
    except Exception:
        pass
    if tables_md:
        return f"{text}\n\n### Detected Tables\n\n" + "\n\n".join(tables_md)
    return text


def cmd_read(args: argparse.Namespace) -> None:
    doc, path = open_pdf(args.pdf_path)
    try:
        total = doc.page_count
        start = max(1, args.start_page)
        end = args.end_page if args.end_page is not None else start
        end = min(total, max(start, end))

        # Cap per-call page count to protect small local LLM context windows
        max_span = args.max_pages
        truncated = False
        if end - start + 1 > max_span:
            end = start + max_span - 1
            truncated = True

        pages_out = []
        for p in range(start, end + 1):
            content = extract_page_markdown(doc, p - 1)
            pages_out.append({"page": p, "content": content})

        result = {
            "path": str(path),
            "total_pages": total,
            "start_page": start,
            "end_page": end,
            "truncated_to_max_pages": truncated,
            "pages": pages_out,
        }
        print(json.dumps(result, ensure_ascii=False, indent=2))
    finally:
        doc.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="PDF helper for Pi Agent")
    sub = parser.add_subparsers(dest="command", required=True)

    p_outline = sub.add_parser("outline", help="Get PDF page count and outline")
    p_outline.add_argument("pdf_path")
    p_outline.add_argument("--max-items", type=int, default=100)
    p_outline.set_defaults(func=cmd_outline)

    p_search = sub.add_parser("search", help="Search keyword across PDF pages")
    p_search.add_argument("pdf_path")
    p_search.add_argument("query")
    p_search.add_argument("--max-hits", type=int, default=15)
    p_search.set_defaults(func=cmd_search)

    p_read = sub.add_parser("read", help="Read specific page range as Markdown")
    p_read.add_argument("pdf_path")
    p_read.add_argument("start_page", type=int)
    p_read.add_argument("end_page", type=int, nargs="?", default=None)
    p_read.add_argument("--max-pages", type=int, default=5)
    p_read.set_defaults(func=cmd_read)

    args = parser.parse_args()
    try:
        args.func(args)
    except Exception as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
