"""Fashion material analyzer agent (Agent A)."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from langchain.output_parsers import ResponseSchema, StructuredOutputParser
from langchain.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import OutputParserException
from langchain_openai import ChatOpenAI

from src.config import get_settings


@dataclass
class MaterialComponent:
    """Normalized representation of a garment material component."""

    name: str
    percentage: float
    weight_grams: float


@dataclass
class FashionAnalysis:
    """Structured output from the fashion material analyzer."""

    garment_summary: str
    components: List[MaterialComponent]
    total_weight_grams: Optional[float]


class FashionMaterialAnalyzer:
    """LangChain-powered agent that extracts material data from an image."""

    def __init__(self, llm: Optional[ChatOpenAI] = None) -> None:
        settings = get_settings()
        if llm is None:
            if not settings.openai_api_key:
                raise RuntimeError(
                    "OPENAI_API_KEY is required to instantiate FashionMaterialAnalyzer."
                )

            llm = ChatOpenAI(
                model=settings.fashion_analyzer_model,
                temperature=0,
                api_key=settings.openai_api_key,
            )

        self._llm = llm
        self._parser = self._build_parser()
        self._prompt = self._build_prompt()

    def _build_parser(self) -> StructuredOutputParser:
        schemas = [
            ResponseSchema(
                name="garment_summary",
                description="High level textual summary of every garment in the image.",
            ),
            ResponseSchema(
                name="components",
                description=(
                    "Array of material components with `name`, `percentage`, and "
                    "`weight_grams` keys. Percentages should sum to roughly 100%."
                ),
                type="list",
            ),
            ResponseSchema(
                name="total_weight_grams",
                description="Estimated total weight of all garments combined in grams.",
                type="float",
            ),
        ]
        return StructuredOutputParser.from_response_schemas(schemas)

    def _build_prompt(self) -> ChatPromptTemplate:
        format_instructions = self._parser.get_format_instructions()
        return ChatPromptTemplate.from_messages(
            [
                SystemMessage(
                    content=(
                        "You are Agent A, an expert textile analyst specializing in "
                        "identifying garment materials, their composition, and weight." \
                        " Use the provided image to identify each distinct garment and "
                        "estimate material breakdown. Provide realistic percentages and "
                        "weight estimates."
                    )
                ),
                HumanMessage(
                    content=(
                        "Image reference: {image_reference}\n"
                        "User context: {user_context}\n"
                        "Return JSON matching: {format_instructions}"
                    )
                ),
            ]
        ).partial(format_instructions=format_instructions)

    def analyze(self, image_reference: str, *, user_context: str = "") -> FashionAnalysis:
        """Run the analysis pipeline against an image."""

        messages = self._prompt.format_messages(
            image_reference=image_reference,
            user_context=user_context or "No additional context provided.",
        )
        response = self._llm.invoke(messages)
        try:
            parsed = self._parser.parse(response.content)
        except OutputParserException as exc:  # pragma: no cover - defensive branch
            raise RuntimeError(f"Failed to parse LLM response: {exc}") from exc

        components_raw: List[Dict[str, Any]] = parsed.get("components", [])  # type: ignore[index]
        components = [
            MaterialComponent(
                name=str(item.get("name", "")),
                percentage=float(item.get("percentage", 0.0)),
                weight_grams=float(item.get("weight_grams", 0.0)),
            )
            for item in components_raw
        ]

        total_weight = parsed.get("total_weight_grams")
        total_weight_grams = float(total_weight) if total_weight is not None else None

        return FashionAnalysis(
            garment_summary=str(parsed.get("garment_summary", "")),
            components=components,
            total_weight_grams=total_weight_grams,
        )


__all__ = [
    "FashionMaterialAnalyzer",
    "FashionAnalysis",
    "MaterialComponent",
]
