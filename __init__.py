"""
Bailian (百炼) TTS Provider — Qwen-Audio-TTS via the DashScope SpeechSynthesizer HTTP API.

Environment variables:
  - DASHSCOPE_API_KEY        : Aliyun Bailian / DashScope API key (required)
  - BAILIAN_WORKSPACE_ID     : Aliyun Bailian workspace / business-space ID (required)
  - BAILIAN_TTS_INSTRUCTIONS : optional natural-language instruction text

Default model: qwen-audio-3.1-tts-flash
Default voice: baiqinglan_v3.1  (白清岚 — bright & pure Mandarin female)

Notes:
  - Qwen-Audio-TTS is served only in the Beijing region on the workspace-scoped
    domain, and returns audio natively (mp3/wav) — no local transcoding needed.
  - The legacy qwen3-tts model family was removed in this version (vendor-retired).
"""

from __future__ import annotations

import json
import logging
import os
import shutil
import subprocess
from typing import Any, Dict, List, Optional
from urllib import request, error as urllib_error

from agent.tts_provider import TTSProvider

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DEFAULT_MODEL = "qwen-audio-3.1-tts-flash"
DEFAULT_VOICE = "baiqinglan_v3.1"

# Endpoint template — {workspace_id} is replaced at runtime.
ENDPOINT = (
    "https://{workspace_id}.cn-beijing.maas.aliyuncs.com"
    "/api/v1/services/audio/tts/SpeechSynthesizer"
)


def _looks_like_mp3(data: bytes) -> bool:
    """Cheap sanity check: ID3 tag or MPEG frame sync at the start."""
    if len(data) < 3:
        return False
    if data[:3] == b"ID3":
        return True
    return data[0] == 0xFF and (data[1] & 0xE0) == 0xE0


class BailianTTSProvider(TTSProvider):
    """TTS backend for Aliyun Bailian (百炼) / DashScope Qwen-Audio-TTS."""

    @property
    def name(self) -> str:
        return "bailian"

    @property
    def display_name(self) -> str:
        return "Bailian (百炼 Qwen-Audio-TTS)"

    def is_available(self) -> bool:
        """Check that required env vars are set."""
        api_key = os.environ.get("DASHSCOPE_API_KEY", "").strip()
        ws_id = os.environ.get("BAILIAN_WORKSPACE_ID", "").strip()
        return bool(api_key and ws_id)

    def list_voices(self) -> List[Dict[str, Any]]:
        """Curated qwen-audio-3.1-tts-flash system voices (full list:
        https://docs.bailian.console.aliyun.com/zh/model-studio/qwen-audio-tts-voice-list)."""
        return [
            {"id": "baiqinglan_v3.1", "display": "白清岚 — 明亮清纯女声 (默认)", "language": "zh-CN", "gender": "female"},
            {"id": "anxiaolan_v3.1", "display": "安小岚 — 清甜纯净女声", "language": "zh-CN", "gender": "female"},
            {"id": "yuxiaoyun_v3.1", "display": "于小云 — 元气亲切女声", "language": "zh-CN", "gender": "female"},
            {"id": "xiaxiaochen_v3.1", "display": "夏小晨 — 元气明亮女声", "language": "zh-CN", "gender": "female"},
            {"id": "qiaoxiaojiao_v3.1", "display": "乔小娇 — 俏丽可爱女声", "language": "zh-CN", "gender": "female"},
            {"id": "wenhuaiqing_v3.1", "display": "温怀清 — 清亮柔和女声", "language": "zh-CN", "gender": "female"},
            {"id": "xieshurou_v3.1", "display": "谢舒柔 — 柔和知性女声", "language": "zh-CN", "gender": "female"},
            {"id": "xuyuyuan_v3.1", "display": "许玉远 — 知性成熟女声", "language": "zh-CN", "gender": "female"},
            {"id": "xiaoxingzhi_v3.1", "display": "萧行之 — 端庄贵气女声", "language": "zh-CN", "gender": "female"},
            {"id": "yeqinghe_v3.1", "display": "叶清禾 — 亲切温柔女声", "language": "zh-CN", "gender": "female"},
            {"id": "anyuqing_v3.1", "display": "安语晴 — 甜美女声", "language": "zh-CN", "gender": "female"},
            {"id": "anmingyuan_v3.1", "display": "安明远 — 清亮自然男声", "language": "zh-CN", "gender": "male"},
            {"id": "huozhuoshi_v3.1", "display": "霍拙石 — 清亮男声", "language": "zh-CN", "gender": "male"},
            {"id": "xunanchuan_v3.1", "display": "许南川 — 多方言/多语种男声", "language": "zh-CN", "gender": "male"},
            {"id": "longanhuan_v3.1", "display": "龙安欢 — 多方言/多语种女声", "language": "zh-CN", "gender": "female"},
            {"id": "Emily_v3.1", "display": "Emily — 英式女声 (英文)", "language": "en-GB", "gender": "female"},
            {"id": "Ava_v3.1", "display": "Ava — 美式女声 (英文)", "language": "en-US", "gender": "female"},
        ]

    def list_models(self) -> List[Dict[str, Any]]:
        """Return available models (Qwen-Audio-TTS family only)."""
        return [
            {
                "id": "qwen-audio-3.1-tts-flash",
                "display": "Qwen-Audio-3.1-TTS Flash (指令控制, 推荐)",
                "max_text_length": 4000,
            },
            {
                "id": "qwen-audio-3.0-tts-flash",
                "display": "Qwen-Audio-3.0-TTS Flash (指令控制)",
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
            "tag": "阿里云百炼 — Qwen-Audio-TTS 中文语音合成",
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

        want_format = (format or "mp3").lower()
        if want_format not in ("mp3", "wav"):
            want_format = "mp3"

        instructions = (
            extra.get("instructions")
            or os.environ.get("BAILIAN_TTS_INSTRUCTIONS", "").strip()
        )

        endpoint = ENDPOINT.format(workspace_id=workspace_id)

        input_params: Dict[str, Any] = {
            "text": text,
            "voice": voice,
            "format": want_format,
        }
        if instructions:
            input_params["instruction"] = instructions
        if speed is not None:
            try:
                rate = float(speed)
            except (TypeError, ValueError):
                rate = 1.0
            if 0.5 <= rate <= 2.0 and rate != 1.0:
                input_params["rate"] = rate

        payload = {"model": model, "input": input_params}

        logger.info(
            "Bailian TTS: requesting synthesis (model=%s, voice=%s, format=%s, chars=%d)",
            model, voice, want_format, len(text),
        )

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
            with request.urlopen(req, timeout=60) as resp:
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
            with request.urlopen(request.Request(audio_url), timeout=60) as resp:
                audio_data = resp.read()
        except Exception as exc:
            raise RuntimeError(f"Bailian TTS audio download failed: {exc}") from exc

        if not audio_data:
            raise RuntimeError("Bailian TTS audio download returned 0 bytes")

        # ── Step 3: Write audio (native format; ffmpeg only as a safety net) ──
        tmp_path = f"{output_path}.{want_format}"

        with open(tmp_path, "wb") as f:
            f.write(audio_data)
        logger.info("Bailian TTS: received %d bytes (%s)", len(audio_data), want_format)

        needs_convert = want_format == "mp3" and not _looks_like_mp3(audio_data)
        if not needs_convert:
            os.replace(tmp_path, output_path)
            logger.info(
                "Bailian TTS: wrote %s (%d bytes)",
                output_path, os.path.getsize(output_path),
            )
        else:
            logger.warning(
                "Bailian TTS: response does not look like MP3 (first bytes: %r), "
                "attempting ffmpeg conversion", audio_data[:4],
            )
            converted = False
            ffmpeg = shutil.which("ffmpeg")
            if ffmpeg:
                try:
                    subprocess.run(
                        [ffmpeg, "-y", "-i", tmp_path,
                         "-ac", "1",                    # mono for voice
                         "-codec:a", "libmp3lame",
                         "-q:a", "5",                   # VBR ~80kbps avg
                         output_path],
                        capture_output=True, timeout=30, check=True,
                    )
                    logger.info(
                        "Bailian TTS: ffmpeg conversion done (%d bytes -> %d bytes)",
                        len(audio_data), os.path.getsize(output_path),
                    )
                    converted = True
                except Exception as exc:
                    logger.warning("Bailian TTS: ffmpeg conversion failed: %s", exc)
            else:
                logger.warning("Bailian TTS: ffmpeg not found, cannot convert to MP3")

            if not converted:
                # Fallback: copy raw audio to output_path so the file always
                # exists at the expected location.
                shutil.copy2(tmp_path, output_path)
                logger.info(
                    "Bailian TTS: raw-format fallback -> %s (%d bytes)",
                    output_path, os.path.getsize(output_path),
                )

            try:
                os.remove(tmp_path)
            except OSError:
                pass

        # Log usage for monitoring (token-based billing)
        usage = result.get("usage", {}) or {}
        logger.debug(
            "Bailian TTS: usage=%s request_id=%s",
            usage or "?", result.get("request_id", "?"),
        )

        return output_path


# ---------------------------------------------------------------------------
# Plugin auto-registration
# ---------------------------------------------------------------------------


def register(plugin_context):
    """Called by the Hermes plugin loader to register this TTS provider."""
    provider = BailianTTSProvider()
    plugin_context.register_tts_provider(provider)
    logger.info(
        "Bailian TTS provider registered (default: %s / %s)",
        DEFAULT_MODEL, DEFAULT_VOICE,
    )
