from local_pdf_agent.agent import Agent
from local_pdf_agent.pdf_tools import PDFDocument, PDFPage


class RecordingModel:
    def __init__(self):
        self.prompt = ""

    def generate(self, prompt):
        self.prompt = prompt
        return "The answer"


def test_agent_retrieves_context_and_reports_answer():
    document = PDFDocument(
        path="sample.pdf",
        pages=(PDFPage(number=1, text="The deadline is November 20."),),
    )
    model = RecordingModel()

    response = Agent(model, context_limit=2).run(
        "What is the deadline?", document
    )

    assert response.answer == "The answer"
    assert "November 20" in model.prompt
    assert "DOCUMENT CONTEXT" in model.prompt
    assert "What is the deadline?" in model.prompt
    assert response.sources
