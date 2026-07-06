# Hermes Bailian TTS Plugin

[中文](README.md) | English

Aliyun Bailian (DashScope) Qwen-TTS voice synthesis plugin for Hermes Agent. Delivers high-quality Chinese text-to-speech via gateway platforms (QQ Bot, Telegram, etc.).

## Best Practices ⚠️

**This plugin works best on Gateway messaging platforms.** Not all Hermes surfaces support audio playback:

| Surface | TTS Playback | Recommendation |
|------|:--:|:--:|
| **QQ Bot** | ✅ Gateway `send_voice` → native voice bubble | ⭐⭐⭐ Best |
| **Telegram** | ✅ Gateway `send_voice` → Opus voice bubble | ⭐⭐⭐ Best |
| **WebUI** | ✅ Inline `<audio>` player (via `/api/media`) | ⭐⭐⭐ Works |
| **Discord / Slack** | ✅ Gateway sends audio attachment | ⭐⭐ OK |
| **CLI (local terminal)** | ✅ `hermes chat` + `/voice tts` local playback | ⭐⭐ Local only |
| **TUI (SSH remote)** | ❌ No audio output device | Not supported |
| **Desktop App** | ❓ Untested | Unknown |

**Bottom line: QQ Bot / Telegram (native voice bubbles), WebUI (inline audio player), and CLI (local playback) all work well.** TUI SSH sessions cannot deliver audio.

Before enabling, configure `SOUL.md` so the agent acts like a secretary: brief spoken summary + detailed text body. See [Agent Behavior Tuning](#agent-behavior-tuning).

## Features

- **Qwen3-TTS-Instruct-Flash** — HTTP voice synthesis with instruction control
- **7 system voices** — Chinese male/female (Maia, Cherry, Stella, Harry, Liam) + English (Emma, Henry)
- **Instruction control** — Natural language control over speed, emotion, style ("speak in a gentle, warm tone")
- **Zero dependencies** — Pure Python stdlib, uses `urllib` only

## Installation

```bash
# 1. Copy plugin to Hermes plugins directory
cp -r hermes-bailian-tts ~/.hermes/plugins/tts/bailian/

# 2. Enable the plugin
hermes plugins enable bailian

# 3. Set environment variables (~/.hermes/.env)
DASHSCOPE_API_KEY=sk-xxx          # Bailian API Key
BAILIAN_WORKSPACE_ID=ws-xxx       # Workspace ID
BAILIAN_TTS_INSTRUCTIONS=Speak in a gentle, warm tone   # Optional: global instruction

# 4. Configure TTS provider (~/.hermes/config.yaml)
tts:
  provider: bailian
  voice: Maia
  model: qwen3-tts-instruct-flash

# 5. Restart Hermes or /reset
```

## Getting Credentials

1. Open [Aliyun Bailian Console](https://bailian.console.aliyun.com/)
2. Go to **API-KEY** page (top-right), create an API Key (starts with `sk-`)
3. The `workspaceId=` parameter in the address bar is your Workspace ID (starts with `ws-`)

## API Parameters

### Config (config.yaml)

| Parameter | Default | Description |
|------|--------|------|
| `tts.provider` | — | Set to `bailian` |
| `tts.voice` | `Maia` | Voice ID (see voice table) |
| `tts.model` | `qwen3-tts-instruct-flash` | Model ID |
| `tts.instructions` | — | (instruct models only) Instruction text |

### Environment Variables

| Variable | Required | Description |
|------|:--:|------|
| `DASHSCOPE_API_KEY` | ✓ | Bailian API Key |
| `BAILIAN_WORKSPACE_ID` | ✓ | Workspace ID |
| `BAILIAN_TTS_INSTRUCTIONS` | ✗ | Global instruction control |

### Extra Parameters (`text_to_speech` tool `extra`)

| Parameter | Type | Description |
|------|------|------|
| `instructions` | `str` | Per-call instruction (overrides env var) |

## Voices

| ID | Description | Language |
|------|------|------|
| `Maia` | Gentle female | Chinese |
| `Cherry` | Energetic female | Chinese |
| `Stella` | Composed female | Chinese |
| `Harry` | Refined male | Chinese |
| `Liam` | Bright male | Chinese |
| `Emma` | Intellectual female | English |
| `Henry` | Deep male | English |

## Models

| ID | Instruction Control | Description |
|------|:--:|------|
| `qwen3-tts-instruct-flash` | ✓ | Recommended. Natural language style/speed/emotion control |
| `qwen3-tts-flash` | ✗ | Basic, fixed style |

## Instruction Control Examples

```
"Speak in a gentle, warm tone, at a normal pace"
"Use an excited broadcast style, speak faster"
"Use a deep, serious newscaster voice"
"Read in a slow, relaxing manner"
```

## Usage

### QQ Bot / Telegram (Recommended)

On gateway platforms, when the agent calls `text_to_speech`, the gateway automatically delivers the audio as a **native voice bubble**. Configure `SOUL.md` rules and the agent will intelligently decide when to speak.

### CLI / WebUI

CLI's `/voice tts` is handled by the framework (auto-TTS with 4000-char truncation). WebUI does not support inline plugin audio — use the browser's built-in 🔊 button instead.

### Script Utility

`scripts/send_voice_qq.py` — Standalone script to send an MP3 file as a QQ voice message:

```bash
python3 scripts/send_voice_qq.py /path/to/audio.mp3
```

### Companion Skill (Recommended)

This repo includes a Hermes Skill with the full Bailian TTS usage guide and SOUL.md decision tree template:

```bash
hermes skills install \
  https://raw.githubusercontent.com/kingsznhone/hermes-bailian-tts/master/skill/SKILL.md
```

Load in Hermes: `/skill bailian-tts-usage`

> For generic TTS plugin design methodology: `/skill hermes-custom-tts-integration`

## API Endpoint

```
POST https://{workspace_id}.cn-beijing.maas.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation
```

Request body:

```json
{
    "model": "qwen3-tts-instruct-flash",
    "input": {
        "text": "Text to synthesize",
        "voice": "Maia",
        "language_type": "Chinese",
        "instructions": "Speak in a gentle tone"
    }
}
```

Response:

```json
{
    "request_id": "0e6ea46e-1332-9ed3-8f94-0e8de08f72e5",
    "output": {
        "audio": {
            "url": "http://dashscope-xxx.oss-cn-beijing.aliyuncs.com/..."
        }
    },
    "usage": {
        "characters": 22
    }
}
```

## Pricing

Billed per input character, output is free. Qwen3-TTS-Instruct-Flash ≈ **¥1 / 10,000 characters**.

Reference: [Aliyun Bailian Pricing](https://help.aliyun.com/zh/model-studio/billing-for-model-studio)

## Agent Behavior Tuning

On gateway platforms, the agent should act like a secretary — **brief spoken summary + detailed text body** — rather than reading the full response aloud.

Add these rules to `~/.hermes/SOUL.md`:

```markdown
## TTS Behavior on Gateway Platforms (qqbot, telegram, discord, etc.)

When the conversation source is a gateway platform (NOT webui/cli/tui):
- Short replies (≤ 50 Chinese chars): May speak full text.
- Long replies (> 50 Chinese chars): NEVER speak full text. Instead, first call
  text_to_speech with a 10–30 char spoken summary, then deliver full text.
- Task completion: Always end with spoken confirmation.
- Do NOT call text_to_speech on CLI/TUI/WebUI sessions.
```

Full template at `SOUL_TEMPLATE.md`.

## Directory Structure

```
hermes-bailian-tts/
├── plugin.yaml              # Plugin metadata
├── __init__.py              # TTSProvider implementation
├── README.md                # Chinese docs
├── README_EN.md             # English docs
├── SOUL_TEMPLATE.md         # Agent behavior rules template
├── skill/                   # Companion Skill (installable separately)
│   └── SKILL.md             # Skill entry point (framework guide + decision tree)
└── scripts/
    └── send_voice_qq.py     # QQ Bot voice sender utility
```

## Related Resources

- [Hermes Custom TTS Integration Skill](https://github.com/nesquena/hermes-agent) — General TTS framework integration guide
- [Aliyun Bailian TTS Documentation](https://help.aliyun.com/zh/model-studio/tts-model/)
- [QQ Bot API Documentation](https://bot.q.qq.com/wiki/develop/api-v2/)

## License

MIT
