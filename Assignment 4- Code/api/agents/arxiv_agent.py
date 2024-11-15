from langchain_core.runnables import RunnablePassthrough
import arxiv
from typing import List, Dict, Any
from ..models import ArxivResult
import logging
 
logger = logging.getLogger(__name__)
 
class ArxivAgent:
    def __init__(self):
        self.client = arxiv.Client()
 
    async def search_papers(self, state: Dict[str, Any]) -> List[ArxivResult]:
        try:
            # Create search instance for each query
            search = arxiv.Search(
                query=state["query"],
                max_results=5,
                sort_by=arxiv.SortCriterion.Relevance
            )
           
            results = []
            for paper in self.client.results(search):
                result = ArxivResult(
                    title=paper.title,
                    summary=paper.summary,
                    published=paper.published.strftime("%Y-%m-%d"),
                    authors=[str(author) for author in paper.authors],
                    link=paper.pdf_url
                )
                results.append(result)
               
            return results
        except Exception as e:
            logger.error(f"ArXiv search error: {str(e)}")
            return []
 
    def create_node(self):
        return self.chain
 