from fpdf import FPDF
from ..models import ResearchSession, ResearchResult
import logging

class ResearchPDFExporter:
    def __init__(self):
        self.pdf = FPDF()
        
    def export_session(self, session: ResearchSession) -> bytes:
        """Export research session to PDF"""
        try:
            self.pdf.add_page()
            self.pdf.set_font("Arial", "B", 16)
            self.pdf.cell(0, 10, f"Research Report - {session.document_id}", ln=True)
            
            for i, question in enumerate(session.questions, 1):
                self._add_question_section(i, question)
                
            return self.pdf.output(dest='S').encode('latin-1')
            
        except Exception as e:
            logging.error(f"PDF export error: {str(e)}")
            raise

    def _add_question_section(self, index: int, result: ResearchResult):
        """Add a question section to the PDF"""
        self.pdf.set_font("Arial", "B", 12)
        self.pdf.cell(0, 10, f"Question {index}: {result.query}", ln=True)
        
        # Add RAG Response
        self.pdf.set_font("Arial", "", 10)
        if result.rag_response:
            self.pdf.multi_cell(0, 10, f"Document Analysis: {result.rag_response}")
        
        # Add Arxiv Results
        if result.arxiv_results:
            self.pdf.set_font("Arial", "B", 11)
            self.pdf.cell(0, 10, "Related Academic Research:", ln=True)
            for arxiv in result.arxiv_results:
                self.pdf.set_font("Arial", "B", 10)
                self.pdf.multi_cell(0, 10, f"• {arxiv.title}")
                self.pdf.set_font("Arial", "", 9)
                self.pdf.multi_cell(0, 10, f"  Summary: {arxiv.summary[:200]}...")
        
        # Add Web Results
        if result.web_results:
            self.pdf.set_font("Arial", "B", 11)
            self.pdf.cell(0, 10, "Web Research:", ln=True)
            for web in result.web_results[:3]:
                self.pdf.multi_cell(0, 10, f"• {web.title}\n  {web.snippet}")
        
        # Add Combined Analysis
        self.pdf.set_font("Arial", "B", 11)
        self.pdf.cell(0, 10, "Synthesis:", ln=True)
        self.pdf.set_font("Arial", "", 10)
        self.pdf.multi_cell(0, 10, result.combined_analysis)
        
        self.pdf.ln(10)