# Local PDF Agent Instructions

- User-provided PDFs (financial reports, contracts, manuals) are placed in the `pdfs/` folder.
- When the user asks about a PDF without specifying the full path, call `pdf_list` first to see what files are in `pdfs/`.
- Always analyze PDFs step-by-step:
  1. `pdf_outline` to check total pages and table of contents.
  2. `pdf_search` to locate relevant page numbers by keyword.
  3. `pdf_read_pages` (1–3 pages at a time) to verify exact figures, tables, or clauses.
- When asked to fill out forms, templates, or generate output files based on PDF content, read/verify the exact source pages first, cite page numbers (`p. X`), and use `read` / `write` / `edit` tools to update or create the target file.
