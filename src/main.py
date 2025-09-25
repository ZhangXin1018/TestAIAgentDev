"""Entrypoint to run the collaborative fashion sustainability agents."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

from src.agents.orchestrator import CollaborativeAgentOrchestrator
from src.tools.image_material_tool import build_data_uri


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Collaborative fashion sustainability agent runner",
    )
    parser.add_argument(
        "image",
        type=str,
        help=(
            "Path or URL referencing the garment image to analyze. Local paths will "
            "be automatically encoded as data URIs."
        ),
    )
    parser.add_argument(
        "--prompt",
        type=str,
        default="",
        help="Optional user instructions or additional garment context.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Optional file path to store the resulting JSON payload.",
    )
    return parser.parse_args()


def normalize_image_reference(image: str) -> str:
    path = Path(image)
    if path.exists():
        return build_data_uri(str(path))
    return image


def main() -> None:
    load_dotenv()
    args = parse_args()

    orchestrator = CollaborativeAgentOrchestrator()
    response = orchestrator.run(
        image_reference=normalize_image_reference(args.image),
        user_prompt=args.prompt,
    )
    payload: dict[str, Any] = response.to_dict()

    if args.output:
        args.output.write_text(json.dumps(payload, indent=2))
        print(f"Results written to {args.output}")
    else:
        print(json.dumps(payload, indent=2))


if __name__ == "__main__":  # pragma: no cover - CLI entrypoint
    main()
