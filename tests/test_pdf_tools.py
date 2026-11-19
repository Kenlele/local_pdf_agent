from local_pdf_agent.pdf_tools import PDFDocument, PDFPage, PDFTools


def test_normalize_pdf_whitespace():
    tools = PDFTools()

    assert tools.normalize("  hello \t world \n\n\nnext  ") == "hello world\n\nnext"


def test_chunk_keeps_page_numbers():
    document = PDFDocument(
        path="sample.pdf",
        pages=(PDFPage(number=3, text="A" * 15),),
    )

    chunks = PDFTools().chunk(document, chars_per_chunk=10, overlap=2)

    assert len(chunks) == 2
    assert all(chunk.startswith("[Page 3]") for chunk in chunks)
    assert "[Page 3] " + "A" * 10 in chunks


def test_search_ranks_matching_chunk_first():
    document = PDFDocument(
        path="sample.pdf",
        pages=(
            PDFPage(number=1, text="A description of weather."),
            PDFPage(number=2, text="The invoice total is 120 dollars."),
        ),
    )

    matches = PDFTools().search(document, "invoice total")

    assert matches
    assert "[Page 2]" in matches[0]
