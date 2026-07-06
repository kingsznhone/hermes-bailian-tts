"""
Bailian (百炼) TTS Provider — Qwen-TTS via DashScope HTTP API.

Environment variables:
  - DASHSCOPE_API_KEY  : Aliyun Bailian / DashScope API key (required)
  - BAILIAN_WORKSPACE_ID: Aliyun Bailian workspace / business-space ID (required)

Default model: qwen3-tts-instruct-flash  (HTTP, supports instruction control)
Default voice: Maia
"""

from __future__ import annotations

import json
import logging
import os
import time
from typing import Any, Dict, List, Optional
from urllib import request, error as urllib_error

from agent.tts_provider import TTSProvider

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DEFAULT_MODEL = "qwen3-tts-instruct-flash"
DEFAULT_VOICE = "Maia"
DEFAULT_LANGUAGE = "Chinese"  # 可根据文本语言自动切换

# Endpoint template. {workspace_id} is replaced at runtime.
ENDPOINT_TEMPLATE = (
    "https://{workspace_id}.cn-beijing.maas.aliyuncs.com"
    "/api/v1/services/aigc/multimodal-generation/generation"
)

# ---------------------------------------------------------------------------
# Provider
# ---------------------------------------------------------------------------


class BailianTTSProvider(TTSProvider):
    """TTS backend for Aliyun Bailian (百炼) / DashScope Qwen-TTS API."""

    @property
    def name(self) -> str:
        return "bailian"

    @property
    def display_name(self) -> str:
        return "Bailian (百炼 Qwen-TTS)"

    def is_available(self) -> bool:
        """Check that required env vars are set."""
        api_key = os.environ.get("DASHSCOPE_API_KEY", "").strip()
        ws_id = os.environ.get("BAILIAN_WORKSPACE_ID", "").strip()
        return bool(api_key and ws_id)

    def list_voices(self) -> List[Dict[str, Any]]:
        """Return available Qwen-TTS system voices."""
        return [
            {"id": "Maia", "display": "Maia — 温柔女声", "language": "zh-CN", "gender": "female"},
            {"id": "Cherry", "display": "Cherry — 活力女声", "language": "zh-CN", "gender": "female"},
            {"id": "Stella", "display": "Stella — 沉稳女声", "language": "zh-CN", "gender": "female"},
            {"id": "Harry", "display": "Harry — 儒雅男声", "language": "zh-CN", "gender": "male"},
            {"id": "Liam", "display": "Liam — 阳光男声", "language": "zh-CN", "gender": "male"},
            {"id": "Emma", "display": "Emma — 知性女声 (英文)", "language": "en-US", "gender": "female"},
            {"id": "Henry", "display": "Henry — 磁性男声 (英文)", "language": "en-US", "gender": "male"},
        ]

    def list_models(self) -> List[Dict[str, Any]]:
        """Return available Qwen-TTS models."""
        return [
            {
                "id": "qwen3-tts-instruct-flash",
                "display": "Qwen3-TTS Instruct Flash (指令控制)",
                "max_text_length": 4000,
            },
            {
                "id": "qwen3-tts-flash",
                "display": "Qwen3-TTS Flash",
                "max_text_length": 4000,
            },
        ]

    def default_model(self) -> Optional[str]:
        return DEFAULT_MODEL

    def default_voice(self) -> Optional[str]:
        return DEFAULT_VOICE

    def get_setup_schema(self) -> Dict[str, Any]:
        return {
            "name": self.display_name,
            "badge": "paid",
            "tag": "阿里云百炼 — Qwen-TTS 中文语音合成",
            "env_vars": [
                {
                    "key": "DASHSCOPE_API_KEY",
                    "prompt": "DashScope API Key",
                    "url": "https://bailian.console.aliyun.com/?apiKey=1#/efm/api_key",
                },
                {
                    "key": "BAILIAN_WORKSPACE_ID",
                    "prompt": "百炼业务空间 ID (WorkspaceId)",
                    "url": "https://bailian.console.aliyun.com/",
                },
            ],
        }

    def synthesize(
        self,
        text: str,
        output_path: str,
        *,
        voice: Optional[str] = None,
        model: Optional[str] = None,
        speed: Optional[float] = None,
        format: str = "mp3",
        **extra: Any,
    ) -> str:
        """Synthesize ``text`` via Bailian HTTP API and write audio to ``output_path``."""
        api_key = os.environ.get("DASHSCOPE_API_KEY", "").strip()
        workspace_id = os.environ.get("BAILIAN_WORKSPACE_ID", "").strip()

        if not api_key or not workspace_id:
            raise RuntimeError(
                "Bailian TTS requires DASHSCOPE_API_KEY and BAILIAN_WORKSPACE_ID "
                "environment variables."
            )

        voice = voice or DEFAULT_VOICE
        model = model or DEFAULT_MODEL

        endpoint = ENDPOINT_TEMPLATE.format(workspace_id=workspace_id)

        payload = {
            "model": model,
            "input": {
                "text": text,
                "voice": voice,
                "language_type": DEFAULT_LANGUAGE,
            },
        }

        # Optional: instruction control for instruct-flash models
        if "instruct" in model:
            instructions = extra.get("instructions") or os.environ.get(
                "BAILIAN_TTS_INSTRUCTIONS", ""
            ).strip()
            if instructions:
                payload["input"]["instructions"] = instructions

        logger.info("Bailian TTS: requesting synthesis (model=%s, voice=%s, chars=%d)",
                     model, voice, len(text))

        # ── Step 1: POST synthesis request ──
        req = request.Request(
            endpoint,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )

        try:
            with request.urlopen(req, timeout=30) as resp:
                body = resp.read().decode("utf-8")
        except urllib_error.HTTPError as exc:
            err_body = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(
                f"Bailian TTS API error (HTTP {exc.code}): {err_body[:500]}"
            ) from exc
        except Exception as exc:
            raise RuntimeError(f"Bailian TTS request failed: {exc}") from exc

        result = json.loads(body)

        # Check for API-level errors (code or message fields)
        if result.get("code") or result.get("message"):
            raise RuntimeError(
                f"Bailian TTS API error (code={result.get('code')}, "
                f"message={result.get('message', 'unknown')})"
            )

        audio_url = (result.get("output", {}).get("audio", {}).get("url") or "").strip()
        if not audio_url:
            raise RuntimeError(
                f"Bailian TTS response missing audio URL. Response keys: "
                f"{list(result.get('output', {}).keys())}"
            )

        # ── Step 2: Download the audio file ──
        logger.info("Bailian TTS: downloading audio from %s...", audio_url[:80])
        try:
            with request.urlopen(request.Request(audio_url), timeout=30) as resp:
                audio_data = resp.read()
        except Exception as exc:
            raise RuntimeError(f"Bailian TTS audio download failed: {exc}") from exc

        # ── Step 3: Write audio and convert format if needed ──
        # Bailian API always returns WAV. Write to WAV first, then
        # convert to MP3 if requested (QQ Bot voice messages need MP3).
        import shutil
        import tempfile
        import subprocess

        wav_path = output_path
        if not wav_path.lower().endswith(".wav"):
            wav_path = output_path.rsplit(".", 1)[0] + ".wav"

        with open(wav_path, "wb") as f:
            f.write(audio_data)
        logger.info("Bailian TTS: wrote %d bytes to %s", len(audio_data), wav_path)

        # Convert to MP3 if requested and ffmpeg is available
        want_format = (format or "").lower()
        if want_format in ("mp3",) and wav_path != output_path:
            ffmpeg = shutil.which("ffmpeg")
            if ffmpeg:
                try:
                    subprocess.run(
                        [ffmpeg, "-y", "-i", wav_path,
                         "-codec:a", "libmp3lame", "-b:a", "128k",
                         output_path],
                        capture_output=True, timeout=30, check=True,
                    )
                    os.remove(wav_path)  # clean up intermediate WAV
                    logger.info("Bailian TTS: converted WAV→MP3 (%d bytes)",
                                os.path.getsize(output_path))
                    final_path = output_path
                except Exception as exc:
                    logger.warning("Bailian TTS: ffmpeg conversion failed, falling back to WAV: %s", exc)
                    final_path = wav_path
            else:
                logger.info("Bailian TTS: ffmpeg not found, keeping WAV format")
                final_path = wav_path
        else:
            final_path = wav_path

        # Log usage for monitoring
        usage = result.get("usage", {})
        logger.debug("Bailian TTS usage: %s chars (request_id=%s)",
                     usage.get("characters", "?"),
                     result.get("request_id", "?"))

        return final_path


# ---------------------------------------------------------------------------
# Plugin auto-registration
# ---------------------------------------------------------------------------

def register(plugin_context):
    """Called by the Hermes plugin loader to register this TTS provider."""
    provider = BailianTTSProvider()
    plugin_context.register_tts_provider(provider)
    logger.info("Bailian TTS provider registered (models: %s)", DEFAULT_MODEL)
