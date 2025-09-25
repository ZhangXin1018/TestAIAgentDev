"""Utility wrapper around web search providers for sustainability research."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from langchain_core.tools import Tool


@dataclass
class WebSearchResult:
    """Container for search outcomes."""

    query: str
    raw_output: str


class SustainabilityWebSearchTool:
    """Provide a uniform API for sustainability-related research queries."""

    def __init__(self, tavily_api_key: Optional[str] = None, *, k: int = 5) -> None:
        self._k = k
        self._tavily_api_key = tavily_api_key
        self._tool = self._build_tool()

    def _build_tool(self) -> Tool:
        if self._tavily_api_key:
            from langchain_community.tools import TavilySearchResults

            return TavilySearchResults(k=self._k, tavily_api_key=self._tavily_api_key)

        def _disabled_search(_: str) -> str:
            return (
                "Web search is currently disabled. Provide `TAVILY_API_KEY` in the "
                "environment to enable live sustainability research."
            )

        return Tool(
            name="disabled_web_search",
            description="Fallback tool used when no web search provider is configured.",
            func=_disabled_search,
        )

    @property
    def tool(self) -> Tool:
        """Expose the underlying LangChain :class:`Tool` instance."""

        return self._tool

    def run(self, query: str) -> WebSearchResult:
        """Execute the search tool and wrap the result."""

        output = self._tool.run(query)
        return WebSearchResult(query=query, raw_output=str(output))


__all__ = ["SustainabilityWebSearchTool", "WebSearchResult"]
