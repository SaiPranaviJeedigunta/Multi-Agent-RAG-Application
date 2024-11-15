from langchain_core.runnables import RunnablePassthrough
from serpapi import GoogleSearch
from typing import List, Dict, Any
from ..models import WebSearchResult
from ..core.config import SERPAPI_API_KEY

class WebAgent:
    def __init__(self):
        self.api_key = SERPAPI_API_KEY
        self.chain = self._create_chain()

    def _create_chain(self):
        return RunnablePassthrough.assign(
            results=self.search_web
        )

    async def search_web(self, state: Dict[str, Any]) -> List[WebSearchResult]:
        search = GoogleSearch({
            "q": state["query"],
            "num": 5,
            "engine": "google",
            "api_key": self.api_key
        })
        
        results = []
        for item in search.get_dict().get("organic_results", []):
            result = WebSearchResult(
                title=item["title"],
                snippet=item["snippet"],
                link=item["link"]
            )
            results.append(result)
            
        return results

    def create_node(self):
        return self.chain