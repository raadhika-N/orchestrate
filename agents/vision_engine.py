from __future__ import annotations

import base64
import io
import json
import time
from pathlib import Path
from typing import Any

from backend.core.config import Settings, get_settings
from backend.core.logging import get_logger
from agents.tools.submit_claim_review import SAFE_FALLBACK_RESPONSE, get_response_schema
from agents.prompts.system_prompt import _load_system_prompt

logger = get_logger(__name__)


def _encode_image_base64(image_path: Path, settings: Settings) -> str:
    """Opens image, resizes it, returns base64 string."""
    try:
        from PIL import Image

        img = Image.open(image_path).convert("RGB")
        max_dim = settings.image_max_dimension
        if max(img.size) > max_dim:
            img.thumbnail((max_dim, max_dim), Image.LANCZOS)
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=settings.image_jpeg_quality)
        image_bytes = buf.getvalue()
    except ImportError:
        logger.warning("Pillow not installed. Sending raw image bytes.")
        image_bytes = image_path.read_bytes()
    except Exception as exc:
        logger.error("Failed to encode image %s: %s", image_path, exc)
        raise

    return base64.b64encode(image_bytes).decode("utf-8")


def _build_contents(
    *,
    claim_context_text: str,
    image_paths: list[Path],
    settings: Settings,
) -> list[dict[str, Any]]:
    """
    Builds the messages list for Groq API.
    Groq expects content as a list of parts inside the user message.
    Structure: [{"role": "user", "content": [text_part, image_part, ...]}]
    """
    if len(image_paths) > settings.max_images_per_request:
        logger.warning(
            "Claim has %d images but limit is %d. Truncating.",
            len(image_paths), settings.max_images_per_request,
        )
        image_paths = image_paths[: settings.max_images_per_request]

    # Start with the text part
    content_parts: list[dict[str, Any]] = [
        {"type": "text", "text": claim_context_text}
    ]

    # Add each image as a base64 encoded part
    for path in image_paths:
        try:
            b64 = _encode_image_base64(path, settings)
            content_parts.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{b64}"
                }
            })
        except Exception as exc:
            logger.error("Skipping image %s due to error: %s", path, exc)

    return [{"role": "user", "content": content_parts}]


def _call_groq(
    *,
    messages: list[dict[str, Any]],
    system_prompt: str,
    settings: Settings,
) -> dict[str, Any]:
    """
    Calls the Groq API with JSON mode.
    Retries on rate limit errors with exponential backoff.
    """
    from groq import Groq

    client = Groq(api_key=settings.groq_api_key)

    last_error: Exception | None = None
    delay = settings.retry_delay_seconds

    for attempt in range(1, settings.max_retries + 1):
        try:
            logger.debug("Groq API call attempt %d/%d", attempt, settings.max_retries)

            response = client.chat.completions.create(
                model=settings.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    *messages,
                ],
                temperature=settings.temperature,
                max_tokens=settings.max_output_tokens,
                response_format={"type": "json_object"},
            )

            raw_text = response.choices[0].message.content
            parsed = json.loads(raw_text)
            logger.debug("Groq responded successfully on attempt %d", attempt)
            return parsed

        except json.JSONDecodeError as exc:
            logger.error("JSON decode error on attempt %d: %s", attempt, exc)
            last_error = exc
            if attempt < settings.max_retries:
                time.sleep(delay)
                delay *= 2

        except Exception as exc:
            error_str = str(exc).lower()
            is_retryable = any(
                code in error_str
                for code in ("429", "503", "rate", "quota", "overloaded")
            )
            logger.warning(
                "Groq API error on attempt %d (retryable=%s): %s",
                attempt, is_retryable, exc,
            )
            last_error = exc
            if is_retryable and attempt < settings.max_retries:
                logger.info("Waiting %.1f seconds before retry...", delay)
                time.sleep(delay)
                delay *= 2
            else:
                break

    raise RuntimeError(
        f"Groq API failed after {settings.max_retries} attempts: {last_error}"
    ) from last_error


def run_claim_review(
    *,
    claim_context_text: str,
    image_paths: list[Path],
    settings: Settings | None = None,
) -> dict[str, Any]:
    """
    Main function called by the pipeline.
    Takes claim text + images, returns Groq decision dict.
    On any failure returns SAFE_FALLBACK_RESPONSE.
    """
    if settings is None:
        settings = get_settings()

    if not settings.groq_api_key:
        raise EnvironmentError(
            "GROQ_API_KEY is not set. "
            "Add it to your .env file. "
            "Get a free key at https://console.groq.com/"
        )

    system_prompt = _load_system_prompt()
    messages = _build_contents(
        claim_context_text=claim_context_text,
        image_paths=image_paths,
        settings=settings,
    )

    try:
        result = _call_groq(
            messages=messages,
            system_prompt=system_prompt,
            settings=settings,
        )
        logger.info(
            "Claim review completed. claim_status=%s",
            result.get("claim_status"),
        )
        return result
    except Exception as exc:
        logger.error("run_claim_review failed. Returning safe fallback: %s", exc)
        return {**SAFE_FALLBACK_RESPONSE}