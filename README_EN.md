# Hermes Bailian TTS Plugin

[中文](README.md) | English

Aliyun Bailian (DashScope) Qwen-Audio-TTS voice synthesis plugin for Hermes Agent. Delivers high-quality Chinese text-to-speech via gateway platforms (QQ Bot, Telegram, etc.).

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

- **Qwen-Audio-3.1-TTS-Flash** — HTTP voice synthesis with instruction control (Bailian SpeechSynthesizer endpoint)
- **17 curated system voices** — Chinese (Baiqinglan, Anxiaolan, Yuxiaoyun...), multi-dialect/multi-lingual (Longanhuan, Xunanchuan), English (Emily, Ava)
- **Instruction control** — Natural language control over speed, emotion, style ("speak in a gentle, warm tone")
- **Native MP3 output** — straight from the service, no local transcoding
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
  voice: baiqinglan_v3.1
  model: qwen-audio-3.1-tts-flash

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
| `tts.voice` | `baiqinglan_v3.1` | Voice ID (see voice table) |
| `tts.model` | `qwen-audio-3.1-tts-flash` | Model ID |
| `tts.instructions` | — | Instruction text (mapped to `input.instruction`) |

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

Voices are bound to the model family (current: qwen-audio-3.1-tts-flash). Full list: [official voice docs](https://docs.bailian.console.aliyun.com/zh/model-studio/qwen-audio-tts-voice-list).

| ID | Description |
|------|------|
| `baiqinglan_v3.1` | Baiqinglan — bright & pure female (default) |
| `anxiaolan_v3.1` | Anxiaolan — sweet & clear female |
| `yuxiaoyun_v3.1` | Yuxiaoyun — lively & friendly female |
| `xiaxiaochen_v3.1` | Xiaxiaochen — bright & energetic female |
| `qiaoxiaojiao_v3.1` | Qiaoxiaojiao — playful & cute female |
| `wenhuaiqing_v3.1` | Wenhuaiqing — clear & soft female |
| `xieshurou_v3.1` | Xieshurou — soft & intellectual female |
| `xuyuyuan_v3.1` | Xuyuyuan — mature & sophisticated female |
| `xiaoxingzhi_v3.1` | Xiaoxingzhi — elegant & dignified female |
| `yeqinghe_v3.1` | Yeqinghe — warm & gentle female |
| `anyuqing_v3.1` | Anyuqing — sweet female |
| `anmingyuan_v3.1` | Anmingyuan — clear & natural male |
| `huozhuoshi_v3.1` | Huozhuoshi — clear male |
| `xunanchuan_v3.1` | Xunanchuan — multi-dialect male |
| `longanhuan_v3.1` | Longanhuan — multi-dialect female |
| `Emily_v3.1` | British English female |
| `Ava_v3.1` | American English female |

## Models

| ID | Instruction Control | Description |
|------|:--:|------|
| `qwen-audio-3.1-tts-flash` | ✓ | Recommended (default). SpeechSynthesizer endpoint, native mp3/wav, token-based billing |
| `qwen-audio-3.0-tts-flash` | ✓ | Previous generation, still available |

> Legacy `qwen3-tts-*` support was removed in 2.0.0 (models retired).

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

CLI's `/voice tts` is handled by the framework (auto-TTS with 4000-char truncation). WebUI plays audio inline via `/api/media`.

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
POST https://{workspace_id}.cn-beijing.maas.aliyuncs.com/api/v1/services/audio/tts/SpeechSynthesizer
```

Request body:

```json
{
    "model": "qwen-audio-3.1-tts-flash",
    "input": {
        "text": "Text to synthesize",
        "voice": "baiqinglan_v3.1",
        "format": "mp3",
        "instruction": "Speak in a gentle tone"
    }
}
```

Response:

```json
{
    "request_id": "461e4371-7286-9639-9905-c0bd93b38dd5",
    "output": {
        "finish_reason": "stop",
        "audio": {
            "url": "http://dashscope-result-bj.oss-cn-beijing.aliyuncs.com/....mp3?...",
            "id": "audio_461e4371-7286-9639-9905-c0bd93b38dd5",
            "expires_at": 1790855968
        }
    },
    "usage": {
        "input_tokens": 28,
        "output_tokens": 64,
        "total_tokens": 92
    }
}
```

## Pricing

`qwen-audio-3.1-tts-flash` is billed by **tokens** (input + output; see the `usage` field in responses).

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
- [Qwen-Audio-TTS HTTP API Reference](https://docs.bailian.console.aliyun.com/zh/model-studio/qwen-audio-tts-http-api)
- [QQ Bot API Documentation](https://bot.q.qq.com/wiki/develop/api-v2/)

## License

MIT
