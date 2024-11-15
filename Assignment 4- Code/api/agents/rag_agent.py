from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from ..core.pinecone_client import index
from ..core.config import OPENAI_API_KEY
import logging
from typing import Dict, Any, TypedDict
 
logger = logging.getLogger(__name__)
 
class RAGState(TypedDict):
    query: str
    document_id: str
    context: list
    context_summary: str
    rag_response: str
    results: Dict[str, Any]
 
class RAGAgent:
    def __init__(self):
        logger.info("Initializing RAG Agent...")
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            openai_api_key=OPENAI_API_KEY
        )
        self.llm = ChatOpenAI(
            model="gpt-4-turbo-preview",
            openai_api_key=OPENAI_API_KEY
        )
        self.chain = self._create_chain()
       
    def _create_chain(self):
        context_prompt = ChatPromptTemplate.from_template("""
        Process and organize the retrieved contexts:
        Contexts: {context}
        Query: {query}
       
        Instructions:
        1. Analyze the relevance of each context
        2. Identify key information related to the query
        3. Organize information by importance
        4. Remove redundant information
        5. Create a coherent summary""")
 
        response_prompt = ChatPromptTemplate.from_template("""
        Based on the processed context, answer the question.
        Context Summary: {context_summary}
        Question: {query}
       
        Instructions:
        1. Provide a comprehensive answer
        2. Cite specific documents or sections
        3. Maintain factual accuracy
        4. Address all aspects of the query
        5. Include relevant quotes if available""")
 
        chain = (
            RunnablePassthrough.assign(
                context=self.get_relevant_context
            )
            | RunnablePassthrough.assign(
                context_summary=context_prompt | self.llm
            )
            | RunnablePassthrough.assign(
                rag_response=response_prompt | self.llm
            )
        )
       
        return chain
 
    async def get_relevant_context(self, state: Dict[str, Any]) -> list:
        try:
            query_embedding = await self.embeddings.aembed_query(state["query"])
           
            filter_dict = {"document_id": state["document_id"]} if state.get("document_id") else {}
           
            results = index.query(
                vector=query_embedding,
                top_k=3,
                filter=filter_dict,
                include_metadata=True
            )
           
            return [self._process_match(match) for match in results.matches] if results.matches else []
           
        except Exception as e:
            logging.error(f"Error in vector search: {str(e)}")
            raise ValueError(f"Vector search failed: {str(e)}")
 
    def _process_match(self, match):
        return {
            "text": match.metadata.get("text", ""),
            "document_id": match.metadata.get("document_id", ""),
            "score": match.score
        }
 
    def create_node(self):
        return self.chain
 
    async def execute_rag(self, query: str, document_id: str = None) -> Dict[str, Any]:
        try:
            logger.info(f"Executing RAG workflow for query: {query}")
           
            query_embedding = await self.embeddings.aembed_query(query)
           
            filter_dict = {"document_id": document_id} if document_id else {}
           
            results = index.query(
                vector=query_embedding,
                top_k=3,
                filter=filter_dict,
                include_metadata=True
            )
           
            if not results.matches:
                return {
                    "answer": "No relevant information found in the document.",
                    "context_summary": "",
                    "query": query,
                    "document_id": document_id
                }
           
            contexts = [match.metadata.get("text", "") for match in results.matches]
            context_text = "\n".join(contexts)
           
            context_prompt = f"""
            Analyze these document excerpts related to the query: {query}
           
            Document excerpts:
            {context_text}
           
            Provide a clear and comprehensive answer focusing on the query.
            Include specific details and examples from the document where relevant.
            """
           
            response = await self.llm.ainvoke(context_prompt)
           
            return {
                "answer": response.content,
                "context_summary": context_text,
                "query": query,
                "document_id": document_id
            }
 
        except Exception as e:
            logger.error(f"RAG execution error: {str(e)}")
            raise ValueError(f"RAG execution failed: {str(e)}")
 