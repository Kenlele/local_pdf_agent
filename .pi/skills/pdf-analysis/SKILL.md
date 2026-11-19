---
name: pdf-analysis
description: Analyze long PDF documents (financial reports, contracts, manuals) step-by-step using pdf_outline, pdf_search, and pdf_read_pages with exact page citations.
---

# PDF Analysis Workflow

When asked to analyze, summarize, or answer questions about a PDF file (especially long financial reports, contracts, or technical manuals), follow this workflow strictly:

1. **Inspect structure first**:
   - Call `pdf_outline` with the file path to check total page count and table of contents.
2. **Locate relevant pages**:
   - If the outline shows the target section, note its page range.
   - Otherwise (or when looking for specific terms, clauses, or line items like `營業收入`, `違約`, `Termination`), call `pdf_search` to find exact matching page numbers.
3. **Read small page chunks**:
   - Call `pdf_read_pages` for **1 to 3 pages at a time** around the relevant page numbers (never try to read an entire long document at once).
   - If a table or clause continues onto the next page, read the following page before concluding.
4. **Verify & cite**:
   - Do not guess numbers, dates, or contract obligations.
   - Always cite the exact page number(s) (e.g., `p. 12`) and quote or summarize directly from the pages you read.
   - If calculations are needed, use a shell/code tool rather than mental arithmetic.
