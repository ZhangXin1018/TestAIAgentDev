"""Coordinator that allows Agent A and Agent B to collaborate."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict

from src.agents.fashion_analyzer import FashionAnalysis, FashionMaterialAnalyzer
from src.agents.sustainability_estimator import (
    SustainabilityEstimator,
    SustainabilityEstimates,
)


@dataclass
class OrchestratedResponse:
    """Combined response from the two-agent collaboration."""

    fashion_analysis: FashionAnalysis
    sustainability_estimates: SustainabilityEstimates

    def to_dict(self) -> Dict[str, Any]:
        """Convert the orchestrated response to a serializable dictionary."""

        return {
            "fashion_analysis": {
                "garment_summary": self.fashion_analysis.garment_summary,
                "total_weight_grams": self.fashion_analysis.total_weight_grams,
                "components": [
                    asdict(component) for component in self.fashion_analysis.components
                ],
            },
            "sustainability_estimates": asdict(self.sustainability_estimates),
        }


class CollaborativeAgentOrchestrator:
    """High-level façade to run the full multi-agent workflow."""

    def __init__(
        self,
        fashion_agent: FashionMaterialAnalyzer | None = None,
        sustainability_agent: SustainabilityEstimator | None = None,
    ) -> None:
        self._fashion_agent = fashion_agent or FashionMaterialAnalyzer()
        self._sustainability_agent = sustainability_agent or SustainabilityEstimator()

    def run(self, image_reference: str, *, user_prompt: str = "") -> OrchestratedResponse:
        """Execute Agent A followed by Agent B using the provided prompt."""

        fashion_analysis = self._fashion_agent.analyze(
            image_reference=image_reference,
            user_context=user_prompt,
        )
        sustainability_estimates = self._sustainability_agent.estimate(fashion_analysis)
        return OrchestratedResponse(
            fashion_analysis=fashion_analysis,
            sustainability_estimates=sustainability_estimates,
        )


__all__ = ["CollaborativeAgentOrchestrator", "OrchestratedResponse"]
