from langchain_core.runnables import RunnablePassthrough
from typing import Dict, Any
import logging
from ..agents.rag_agent import RAGAgent
from ..agents.arxiv_agent import ArxivAgent
from ..agents.web_agent import WebAgent
 
logger = logging.getLogger(__name__)
 
class ResearchGraph:
    def __init__(self, rag_agent, arxiv_agent, web_agent):
        self.rag_agent = rag_agent
        self.arxiv_agent = arxiv_agent
        self.web_agent = web_agent
        self.chain = self._create_chain()
 
    def _create_chain(self):
        return RunnablePassthrough.assign(
            rag=self._run_rag,
            arxiv=self._run_arxiv,
            web=self._run_web,
            combined=self._combine_results
        )
 
    async def _run_rag(self, state: Dict[str, Any]) -> str:
        try:
            return await self.rag_agent.execute_rag(
                query=state["query"],
                document_id=state["document_id"]
            )
        except Exception as e:
            logger.error(f"RAG processing error: {str(e)}")
            return f"Error in RAG processing: {str(e)}"
 
    async def _run_arxiv(self, state: Dict[str, Any]) -> list:
        if not state.get("use_arxiv", True):
            return []
        try:
            return await self.arxiv_agent.search_papers(state)
        except Exception as e:
            logger.error(f"ArXiv search error: {str(e)}")
            return []
 
    async def _run_web(self, state: Dict[str, Any]) -> list:
        if not state.get("use_web", True):
            return []
        try:
            return await self.web_agent.search_web(state)
        except Exception as e:
            logger.error(f"Web search error: {str(e)}")
            return []
 
    async def _combine_results(self, state: Dict[str, Any]) -> str:
        try:
            rag_response = state.get("rag", {}).get("answer", "No document analysis available.")
            arxiv_results = state.get("arxiv", [])
            web_results = state.get("web", [])
           
            combined = f"""
            Document Analysis:
            {rag_response}
           
            Related Research:
            {self._format_arxiv_results(arxiv_results)}
           
            Web Resources:
            {self._format_web_results(web_results)}
            """
           
            return combined.strip()
        except Exception as e:
            logger.error(f"Error combining results: {str(e)}")
            return "Error combining research results"
 
    def _format_arxiv_results(self, results: list) -> str:
        if not results:
            return "No relevant academic papers found."
        return "\n".join([f"- {r.title}: {r.summary[:200]}..." for r in results[:3]])
 
    def _format_web_results(self, results: list) -> str:
        if not results:
            return "No relevant web resources found."
        return "\n".join([f"- {r.title}: {r.snippet[:200]}..." for r in results[:3]])
 
    async def execute(self, document_id: str, query: str, use_rag: bool = True,
                     use_arxiv: bool = True, use_web: bool = True) -> Dict[str, Any]:
        """Execute the research workflow"""
        try:
            state = {
                "document_id": document_id,
                "query": query,
                "use_rag": use_rag,
                "use_arxiv": use_arxiv,
                "use_web": use_web
            }
           
            logger.info(f"Executing research workflow for document: {document_id}")
            result = await self.chain.ainvoke(state)
            logger.info("Research workflow completed successfully")
           
            return result
        except Exception as e:
            logger.error(f"Research workflow failed: {str(e)}")
            raise ValueError(f"Research workflow failed: {str(e)}")
 
# Initialize agents
rag_agent = RAGAgent()
arxiv_agent = ArxivAgent()
web_agent = WebAgent()
 
# Create and export the research graph instance
research_graph = ResearchGraph(rag_agent, arxiv_agent, web_agent)
 
 