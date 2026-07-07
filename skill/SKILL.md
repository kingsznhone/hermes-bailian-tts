---
name: bailian-tts-usage
description: "Deploy and tune the Bailian (百炼) Qwen-TTS plugin for Hermes — voice selection, instruction control, platform delivery, and agent behavior."
version: 1.1.0
author: zhn
tags: [tts, bailian, qwen, voice, gateway, webui, qqbot]
platforms: [linux, macos]
---

# Bailian Qwen-TTS Plugin — Usage Guide

Deploy, configure, and tune the `hermes-bailian-tts` plugin for natural Chinese voice synthesis on QQ Bot, Telegram, and WebUI.

## Quick Start

```bash
# Install
hermes plugins install kingsznhone/hermes-bailian-tts
hermes plugins enable tts-bailian

# Credentials (~/.hermes/.env)
DASHSCOPE_API_KEY=sk-xxx
BAILIAN_WORKSPACE_ID=ws-xxx
BAILIAN_TTS_INSTRUCTIONS=用温柔亲切的语气，语速正常

# Config (~/.hermes/config.yaml)
tts:
  provider: bailian
  voice: Maia
  model: qwen3-tts-instruct-flash
```

[阿里云百炼控制台](https://bailian.console.aliyun.com/) → API-KEY 页面 → 创建 Key。地址栏 `workspaceId=` 即业务空间 ID。

## Voice Catalog

| ID | Character | Language |
|------|------|------|
| `Maia` | 温柔女声（默认） | 中文 |
| `Cherry` | 活力女声 | 中文 |
| `Stella` | 沉稳女声 | 中文 |
| `Harry` | 儒雅男声 | 中文 |
| `Liam` | 阳光男声 | 中文 |
| `Emma` | 知性女声 | 英文 |
| `Henry` | 磁性男声 | 英文 |

Switch: `hermes config set tts.voice Cherry`

## Models

| Model | Instruction Control | Use Case |
|------|:--:|------|
| `qwen3-tts-instruct-flash` | ✅ | 推荐。自然语言控制语速/情绪/风格 |
| `qwen3-tts-flash` | ✗ | 基础版，固定风格 |

## Instruction Control (仅 instruct 模型)

```
"用温柔亲切的语气，语速正常，像是和好朋友聊天一样"
"用激动的播报风格，语速较快"
"用低沉严肃的新闻播音语气"
"以舒缓、放松的方式朗读"
```

Set globally: `BAILIAN_TTS_INSTRUCTIONS` env var, or per-call via `text_to_speech`'s `extra` parameter.

## Platform Delivery

| Platform | How Audio Arrives | Ready? |
|----------|-------------------|:--:|
| **QQ Bot** | `text_to_speech` → native voice bubble (MP3, 128kbps) | ✅ |
| **Telegram** | `text_to_speech` → Opus voice bubble | ✅ |
| **WebUI** | `text_to_speech` → inline `<audio>` player via `/api/media` | ✅ |
| **CLI** | `/voice tts` framework auto-TTS | ⚠️ Framework-controlled |
| **TUI (SSH)** | No audio device | ❌ |

### QQ Bot Voice Delivery

Gateway auto-handles the 3-step flow:
1. Upload: `POST /v2/users/{id}/files` (base64 for <10MB → 3-step chunked for larger)
2. Send: `POST /v2/users/{id}/messages` with `media: {file_info: "..."}`
3. QQ renders native voice bubble

Manual test script: `scripts/send_voice_qq.py <audio.mp3>`

## Agent Behavior — Make It Speak

By default, the agent won't use `text_to_speech` proactively (Hermes' QQ Bot system prompt doesn't mention voice). Add to `~/.hermes/SOUL.md`:

```markdown
## TTS / Voice on QQ Bot, Telegram, and WebUI

On QQ Bot, Telegram, and WebUI, `text_to_speech` delivers audible voice.
Follow this decision tree for EVERY reply:

1. **Answer ≤ 30 Chinese chars?**
   → First check: does it contain exact numbers/data the user needs to read precisely?
      - **Yes** → Do NOT call `text_to_speech`. Write as text.
      - **No** → Call `text_to_speech` with that text. NO text output. Done.

2. **Answer > 80 chars?**
   → Call `text_to_speech` with 10–30 char summary, then write full text.

3. **30–80 chars?**
   → Call `text_to_speech` with full text, AND write it.

Task lifecycle:
- Starting: Speak "好的，我来处理"
- Finishing: Speak "搞定了" / "有问题，看消息"

Settings: Voice=Maia, Model=qwen3-tts-instruct-flash,
instructions="用温柔亲切的语气，像是和好朋友聊天一样"
Do NOT speak on CLI or TUI.
```

> 💡 The 30/80 char thresholds are adjustable. Full template: `SOUL_TEMPLATE.md` in the repo.

## Pricing

Billed per input character, output free. Qwen3-TTS-Instruct-Flash ≈ **¥1 / 10,000 characters**.

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| Plugin not listed | `hermes plugins enable tts-bailian` |
| No voice on QQ Bot | Add SOUL.md decision tree (agent doesn't know it can speak) |
| Audio won't play in WebUI | File must be under `$HERMES_HOME` or `/tmp` |
| Voice + text for short replies | SOUL.md uses passive language → use "NO text output. Done." |
| 401 on `/api/media` | Auth enabled — `<audio>` needs session cookie |
| ffmpeg not found | `apt install ffmpeg` — plugin copies WAV to output_path as fallback (bandwidth ~4× MP3) |
| .mp3 file is actually WAV | Shouldn't happen with v1.1.1+. Plugin always writes WAV to a distinct `.wav` path, runs ffmpeg for MP3, and only copy-falls-back on failure. Run `file /path/to/output.mp3` to verify. |
| Plugin code changes not taking effect | Python caches imported modules in memory — the gateway process won't pick up plugin changes until it restarts. Deleting `__pycache__/` is insufficient. Run `hermes gateway restart` from a shell **outside** the gateway (not from inside QQ Bot / agent chat). The gateway blocks self-restart (SIGTERM propagation protection). |

## Reference

- Repo: https://github.com/kingsznhone/hermes-bailian-tts
- Plugin design guide: `/skill hermes-custom-tts-integration` (generic TTS plugin framework)
- Bailian TTS docs: https://help.aliyun.com/zh/model-studio/tts-model/
