---
name: bailian-tts-usage
description: "Deploy and tune the Bailian (百炼) Qwen-TTS plugin for Hermes — voice selection, instruction control, platform delivery, and agent behavior."
version: 1.4.0
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
  voice: baiqinglan_v3.1
  model: qwen-audio-3.1-tts-flash
```

[阿里云百炼控制台](https://bailian.console.aliyun.com/) → API-KEY 页面 → 创建 Key。地址栏 `workspaceId=` 即业务空间 ID。

## Voice Catalog

**音色与模型绑定，不可跨系列混用**（旧 qwen3 系列音色已随模型退役移除）。

### qwen-audio-3.1-tts-flash（现行）

| ID | Character |
|------|------|
| `baiqinglan_v3.1` | 白清岚 — 明亮清纯女声（默认） |
| `anxiaolan_v3.1` | 安小岚 — 清甜纯净女声 |
| `yuxiaoyun_v3.1` | 于小云 — 元气亲切女声 |
| `xiaxiaochen_v3.1` | 夏小晨 — 元气明亮女声 |
| `qiaoxiaojiao_v3.1` | 乔小娇 — 俏丽可爱女声 |
| `wenhuaiqing_v3.1` | 温怀清 — 清亮柔和女声 |
| `xieshurou_v3.1` | 谢舒柔 — 柔和知性女声 |
| `xuyuyuan_v3.1` | 许玉远 — 知性成熟女声 |
| `xiaoxingzhi_v3.1` | 萧行之 — 端庄贵气女声 |
| `yeqinghe_v3.1` | 叶清禾 — 亲切温柔女声 |
| `anyuqing_v3.1` | 安语晴 — 甜美女声 |
| `anmingyuan_v3.1` | 安明远 — 清亮自然男声 |
| `huozhuoshi_v3.1` | 霍拙石 — 清亮男声 |
| `xunanchuan_v3.1` | 许南川 — 多方言/多语种男声 |
| `longanhuan_v3.1` | 龙安欢 — 多方言/多语种女声 |
| `Emily_v3.1` / `Ava_v3.1` | 英文（英式 / 美式） |

完整列表：https://docs.bailian.console.aliyun.com/zh/model-studio/qwen-audio-tts-voice-list

### 旧系列（已移除）

`Maia`、`Cherry` 等旧 qwen3 音色已随模型退役一并移除，插件不再支持。

Switch: `hermes config set tts.voice baiqinglan_v3.1 --force`（本机 CLI 对 tts 子键需 `--force`）

## Models

| Model | Instruction Control | Use Case |
|------|:--:|------|
| `qwen-audio-3.1-tts-flash` | ✅ `instruction` | 推荐（默认）。SpeechSynthesizer 端点，原生 mp3/wav，按 Token 计费 |
| `qwen-audio-3.0-tts-flash` | ✅ `instruction` | 上一代，仍可用 |
旧系列 `qwen3-tts-*` 支持已于 2026-09 移除（模型即将停服，插件仅支持 Qwen-Audio 系列）。

## Instruction Control (仅 instruct 模型)

```
"用温柔亲切的语气，语速正常，像是和好朋友聊天一样"
"用激动的播报风格，语速较快"
"用低沉严肃的新闻播音语气"
"以舒缓、放松的方式朗读"
```

Set globally: `BAILIAN_TTS_INSTRUCTIONS` env var, or per-call via `text_to_speech`'s `extra` parameter. 插件映射为 `input.instruction`；Qwen-Audio 系列系统音色支持任意指令。

## Platform Delivery

| Platform | How Audio Arrives | Ready? |
|----------|-------------------|:--:|
| **QQ Bot** | `text_to_speech` → native voice bubble (MP3, 128kbps) | ✅ |
| **Telegram** | `text_to_speech` → Opus voice bubble | ✅ |
| **WebUI** | `text_to_speech` → inline `<audio>` player via `/api/media` | ✅ |
| **CLI** | `/voice tts` framework auto-TTS | ⚠️ Framework-controlled |
| **TUI (SSH)** | No audio device | ❌ |

### QQ Bot Voice Delivery

> ⚠️ 2026-09 起 QQ 服务端 `upload_prepare` 偶发 404「不支持的调用」（~10-15%，重试即成功），媒体投递会偶发失败，详见 Troubleshooting 表。

Gateway auto-handles the 3-step flow:
1. Upload: `POST /v2/users/{id}/files` (base64 for <10MB → 3-step chunked for larger)
2. Send: `POST /v2/users/{id}/messages` with `media: {file_info: "..."}`
3. QQ renders native voice bubble

Manual test script: `scripts/send_voice_qq.py <audio.mp3>`

## Agent Behavior — Make It Speak

By default, the agent won't use `text_to_speech` proactively (Hermes' QQ Bot system prompt doesn't mention voice). Add to `~/.hermes/SOUL.md`:

```markdown
## TTS / Voice on QQ Bot

On QQ Bot, `text_to_speech` delivers audible voice.
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

Settings: Voice=baiqinglan_v3.1, Model=qwen-audio-3.1-tts-flash,
instructions="用温柔亲切的语气，像是和好朋友聊天一样"
Do NOT speak on WebUI, CLI, or TUI.
```

> 💡 The 30/80 char thresholds are adjustable. Full template: `SOUL_TEMPLATE.md` in the repo.

## Pricing

`qwen-audio-3.1-tts-flash`：按 Token 计费（响应 `usage` 含 input/output_tokens，价格见百炼控制台）。

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| Plugin not listed | `hermes plugins enable tts-bailian` |
| No voice on QQ Bot | Add SOUL.md decision tree (agent doesn't know it can speak) |
| QQ 报 "Couldn't deliver the audio attachment" | QQ 服务端 `upload_prepare` 间歇性 404「不支持的调用」(code 11001 / err_code 40011002，实测 ~10-15% 概率，重试即成功)。Hermes 对该接口无重试 → 单次抖动=整条媒体投递失败，重发一次即可。诊断: gateway.log 搜 `Media send failed`。根治: 上游 PR（未合并前不改本地框架 — 用户 2026-09 决策）。 |
| Audio won't play in WebUI | File must be under `$HERMES_HOME` or `/tmp` |
| Voice + text for short replies | SOUL.md uses passive language → use "NO text output. Done." in a numbered decision tree |
| Voice speaking precise numbers | Agent should read them aloud but shouldn't → add Rule 0 (exact data check) to the decision tree before Rule 1 |
| 401 on `/api/media` | Auth enabled — `<audio>` needs session cookie |
| ffmpeg not found | `apt install ffmpeg` — plugin copies WAV to output_path as fallback (bandwidth ~4× MP3) |
| .mp3 file is actually WAV | Shouldn't happen with v1.1.1+. Plugin always writes WAV to a distinct `.wav` path, runs ffmpeg for MP3, and only copy-falls-back on failure. Run `file /path/to/output.mp3` to verify. |
| Plugin code changes not taking effect | Python caches imported modules in memory — the gateway process won't pick up plugin changes until it restarts. Deleting `__pycache__/` is insufficient. Run `hermes gateway restart --system` from a shell **outside** the gateway (not from inside QQ Bot / agent chat). The gateway blocks self-restart (SIGTERM propagation protection). |
| WebUI 里报 `InvalidParameter ... url error`（或一直用旧音色/旧行为） | webui 进程同样是**进程级插件缓存** → `systemctl restart hermes-webui`（页面需刷新）。实测特征：新配置的模型名被发去了旧端点 = 旧代码+新配置共存。 |
| `hermes config set tts.model` 报「not a recognized config key」 | 当前 CLI 的 schema 未收录 tts 子键 → 加 `--force`，会正常写入嵌套结构。 |

## Reference

- Repo: https://github.com/kingsznhone/hermes-bailian-tts
- Plugin design guide: `/skill hermes-custom-tts-integration` (generic TTS plugin framework)
- Bailian TTS docs: https://help.aliyun.com/zh/model-studio/tts-model/
- Qwen-Audio-TTS HTTP API（新系列）: https://docs.bailian.console.aliyun.com/zh/model-studio/qwen-audio-tts-http-api
