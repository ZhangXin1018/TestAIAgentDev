"""Sustainability estimator agent (Agent B)."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from langchain.output_parsers import ResponseSchema, StructuredOutputParser
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import OutputParserException
from langchain_openai import ChatOpenAI

from src.agents.fashion_analyzer import FashionAnalysis
from src.config import get_settings
from src.tools.web_search import SustainabilityWebSearchTool


@dataclass
class SustainabilityEstimates:
    """Aggregated sustainability metrics for the analyzed garments."""

    water_liters: float
    co2_kg: float
    energy_kwh: float
    methodology_notes: str
    research_context: str


class SustainabilityEstimator:
    """Agent that forecasts sustainability impact using material breakdown data."""

    def __init__(
        self,
        analysis_agent: Optional[ChatOpenAI] = None,
        *,
        search_tool: Optional[SustainabilityWebSearchTool] = None,
    ) -> None:
        settings = get_settings()
        if analysis_agent is None:
            if not settings.openai_api_key:
                raise RuntimeError(
                    "OPENAI_API_KEY is required to instantiate SustainabilityEstimator."
                )

            analysis_agent = ChatOpenAI(
                model=settings.sustainability_analyzer_model,
                temperature=0.2,
                api_key=settings.openai_api_key,
            )

        self._llm = analysis_agent
        self._parser = self._build_parser()
        self._prompt = self._build_prompt()
        self._search_tool = search_tool or SustainabilityWebSearchTool(
            tavily_api_key=settings.tavily_api_key
        )

    def _build_parser(self) -> StructuredOutputParser:
        schemas = [
            ResponseSchema(
                name="water_liters",
                description="Estimated average water consumption in liters for the garments.",
                type="float",
            ),
            ResponseSchema(
                name="co2_kg",
                description="Estimated carbon emissions in kilograms of CO2e.",
                type="float",
            ),
            ResponseSchema(
                name="energy_kwh",
                description="Estimated energy consumption in kilowatt hours.",
                type="float",
            ),
            ResponseSchema(
                name="methodology_notes",
                description="Short justification that explains the estimation approach.",
            ),
            ResponseSchema(
                name="research_context",
                description=(
                    "Summary of supporting research pulled from the web search tool."
                ),
            ),
        ]
        return StructuredOutputParser.from_response_schemas(schemas)

    def _build_prompt(self) -> ChatPromptTemplate:
        format_instructions = self._parser.get_format_instructions()
        return ChatPromptTemplate.from_template(
            """
You are Agent B, a sustainability analyst collaborating with a textile analyst.
You are given structured JSON describing garments, their material composition,
and estimated weights. Use reputable sustainability research to estimate the
average water usage (liters), CO2 equivalent emissions (kg), and energy
consumption (kWh) associated with producing these garments.

Always combine the provided research context and your domain knowledge to
produce a concise but transparent methodology. Ensure that numbers are realistic
for modern apparel manufacturing supply chains.

Return JSON matching: {format_instructions}

Material analysis JSON:
{analysis_json}

Relevant research notes:
{research_notes}
"""
        ).partial(format_instructions=format_instructions)

    def estimate(self, analysis: FashionAnalysis) -> SustainabilityEstimates:
        """Estimate sustainability metrics from Agent A's output."""

        if not analysis.components:
            raise ValueError("Fashion analysis does not contain any components to estimate.")

        research_query = self._build_research_query(analysis)
        research_result = self._search_tool.run(research_query)

        analysis_json = {
            "garment_summary": analysis.garment_summary,
            "total_weight_grams": analysis.total_weight_grams,
            "components": [
                {
                    "name": component.name,
                    "percentage": component.percentage,
                    "weight_grams": component.weight_grams,
                }
                for component in analysis.components
            ],
        }

        message = self._prompt.format_messages(
            analysis_json=analysis_json,
            research_notes=research_result.raw_output,
        )
        response = self._llm.invoke(message)

        try:
            parsed = self._parser.parse(response.content)
        except OutputParserException as exc:  # pragma: no cover - defensive branch
            raise RuntimeError(f"Failed to parse LLM response: {exc}") from exc

        return SustainabilityEstimates(
            water_liters=float(parsed.get("water_liters", 0.0)),
            co2_kg=float(parsed.get("co2_kg", 0.0)),
            energy_kwh=float(parsed.get("energy_kwh", 0.0)),
            methodology_notes=str(parsed.get("methodology_notes", "")),
            research_context=str(parsed.get("research_context", "")),
        )

    def _build_research_query(self, analysis: FashionAnalysis) -> str:
        """Craft a targeted sustainability research query."""

        dominant_materials: List[str] = [component.name for component in analysis.components]
        return (
            "Lifecycle assessment water CO2 energy consumption for "
            + ", ".join(dominant_materials[:3])
        )


__all__ = ["SustainabilityEstimator", "SustainabilityEstimates"]
