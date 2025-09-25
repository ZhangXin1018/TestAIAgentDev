"""Tooling to assist the fashion material analyzer agent."""
from __future__ import annotations

import base64
import mimetypes
from pathlib import Path


def _detect_mime_type(path: Path) -> str:
    mime_type, _ = mimetypes.guess_type(path)
    return mime_type or "application/octet-stream"


def encode_image_to_base64(image_path: str) -> tuple[str, str]:
    """Return a tuple of ``(mime_type, base64_data)`` for the provided image.

    This helper is useful when passing images to OpenAI's multimodal models via
    LangChain. The resulting data URI snippet can be concatenated as needed.
    """

    path = Path(image_path).expanduser().resolve()
    if not path.exists():
        raise FileNotFoundError(f"Image not found: {path}")

    mime_type = _detect_mime_type(path)
    encoded = base64.b64encode(path.read_bytes()).decode("utf-8")
    return mime_type, encoded


def build_data_uri(image_path: str) -> str:
    """Return a ``data:`` URI that can be supplied to a multimodal model."""

    mime_type, encoded = encode_image_to_base64(image_path)
    return f"data:{mime_type};base64,{encoded}"


__all__ = ["encode_image_to_base64", "build_data_uri"]
