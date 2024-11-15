from typing import Dict
import json
from ..models import ResearchSession, ResearchResult

class CodelabsExporter:
    def export_session(self, session: ResearchSession) -> Dict:
        """Export research session in Codelabs format"""
        return {
            "title": f"Research on {session.document_id}",
            "steps": [
                {
                    "title": f"Question {i+1}",
                    "duration": "5:00",
                    "content": self._format_question(question)
                }
                for i, question in enumerate(session.questions)
            ]
        } 

    def _format_question(self, result: ResearchResult) -> str:
        """Format a research result for Codelabs"""
        content = f"""
### Question
{result.query}

### Document Analysis
{result.rag_response}

### Academic Research
{"".join([f'''
* **{arxiv.title}**
  * Published: {arxiv.published}
  * Summary: {arxiv.summary[:200]}...
''' for arxiv in (result.arxiv_results or [])])}

### Web Research
{"".join([f'''
* **{web.title}**
  * {web.snippet}
''' for web in (result.web_results or [])])}

### Synthesis
{result.combined_analysis}
"""
        return content 