# Hermes Bailian TTS Plugin

[English](README_EN.md) | 中文

阿里云百炼 (Bailian / DashScope) Qwen-Audio-TTS 语音合成插件，让 Hermes Agent 通过网关平台（QQ Bot / Telegram 等）用高质量中文语音朗读回答。

## 最佳实践 ⚠️

**这个插件最适合在 Gateway 消息平台上使用。** 并非所有 Hermes 终端都支持音频播放：

| 平台 | TTS 播放支持 | 推荐度 |
|------|:--:|:--:|
| **QQ Bot** | ✅ 网关 `send_voice` → 原生语音气泡 | ⭐⭐⭐ 最佳 |
| **Telegram** | ✅ 网关 `send_voice` → Opus 语音气泡 | ⭐⭐⭐ 最佳 |
| **WebUI** | ✅ 内联 `<audio>` 播放器（通过 `/api/media` 加载） | ⭐⭐⭐ 可用 |
| **Discord / Slack** | ✅ 网关发送音频附件 | ⭐⭐ 可用 |
| **CLI (本地终端)** | ✅ `hermes chat` 内 `/voice tts` 本地播放 | ⭐⭐ 仅本地 |
| **TUI (SSH 远程)** | ❌ 无音频输出设备 | 不可用 |
| **Desktop App** | ❓ 未测试 | 待验证 |

**结论：推荐的平台依次是 QQ Bot / Telegram（原生语音气泡）、WebUI（内联播放器）、CLI（本地播放）。** TUI SSH 远程会话由于没有音频设备，无法使用。

启用前建议配置 `SOUL.md` 让 Agent 像秘书一样工作：短语音摘要 + 长文字正文。详见 [Agent 行为调优](#agent-行为调优)。

## 特性

- **Qwen-Audio-3.1-TTS-Flash** — 支持指令控制的 HTTP 语音合成（百炼 SpeechSynthesizer 端点）
- **17 种常用音色** — 中文（白清岚、安小岚、于小云…）、多方言/多语种（龙安欢、许南川）、英文（Emily、Ava）
- **指令控制** — 用自然语言控制语速、情绪、风格（"用温柔的语气，语速稍慢"）
- **原生 MP3 输出** — 服务端直出，无需本地转码
- **纯 Python stdlib** — 零外部依赖，只用 `urllib`

## 安装

```bash
# 1. 复制插件到 Hermes 插件目录
cp -r hermes-bailian-tts ~/.hermes/plugins/tts/bailian/

# 2. 启用插件
hermes plugins enable bailian

# 3. 配置环境变量 (~/.hermes/.env)
DASHSCOPE_API_KEY=sk-xxx          # 百炼 API Key
BAILIAN_WORKSPACE_ID=ws-xxx       # 业务空间 ID
BAILIAN_TTS_INSTRUCTIONS=用温柔亲切的语气，语速正常   # 可选：全局指令

# 4. 配置 TTS provider (~/.hermes/config.yaml)
tts:
  provider: bailian
  voice: baiqinglan_v3.1
  model: qwen-audio-3.1-tts-flash

# 5. 重启 Hermes 或 /reset
```

## 获取凭证

1. 打开 [阿里云百炼控制台](https://bailian.console.aliyun.com/)
2. 右上角进入 **API-KEY** 页面，创建 API Key (`sk-` 开头)
3. 地址栏中的 `workspaceId=` 参数即为业务空间 ID (`ws-` 开头)

## API 参数

### 配置 (config.yaml)

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `tts.provider` | — | 设为 `bailian` |
| `tts.voice` | `baiqinglan_v3.1` | 音色 ID（见下方音色表） |
| `tts.model` | `qwen-audio-3.1-tts-flash` | 模型 ID |
| `tts.instructions` | — | 指令文本（映射为 `input.instruction`） |

### 环境变量

| 变量 | 必填 | 说明 |
|------|:--:|------|
| `DASHSCOPE_API_KEY` | ✓ | 百炼 API Key |
| `BAILIAN_WORKSPACE_ID` | ✓ | 业务空间 ID |
| `BAILIAN_TTS_INSTRUCTIONS` | ✗ | 全局指令控制 |

### 扩展参数 (`text_to_speech` 工具 `extra`)

| 参数 | 类型 | 说明 |
|------|------|------|
| `instructions` | `str` | 单次调用的指令（覆盖环境变量） |

## 音色

音色与模型绑定（当前系列：qwen-audio-3.1-tts-flash）。完整列表见 [官方音色文档](https://docs.bailian.console.aliyun.com/zh/model-studio/qwen-audio-tts-voice-list)。

| ID | 描述 |
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
| `Emily_v3.1` | 英式女声（英文） |
| `Ava_v3.1` | 美式女声（英文） |

## 模型

| ID | 指令控制 | 说明 |
|------|:--:|------|
| `qwen-audio-3.1-tts-flash` | ✓ | 推荐（默认）。SpeechSynthesizer 端点，原生 mp3/wav，按 Token 计费 |
| `qwen-audio-3.0-tts-flash` | ✓ | 上一代，仍可用 |

> 旧系列 `qwen3-tts-*` 支持已于 2.0.0 移除（模型退役）。

## 指令控制示例

```
"用温柔亲切的语气，语速正常，像是和好朋友聊天一样"
"用激动的播报风格，语速较快"
"用低沉严肃的新闻播音语气"
"以舒缓、放松的方式朗读"
```

## 使用方式

### QQ Bot / Telegram（推荐）

在网关平台和 Hermes 对话时，Agent 调用 `text_to_speech` 后，网关自动将音频以**语音气泡**发送。配置 `SOUL.md` 规则后 Agent 会智能判断何时朗读。

### CLI / WebUI

CLI 下 `/voice tts` 由框架层自动处理（全文截断 4000 字朗读）。WebUI 通过 `/api/media` 内联播放。

### 脚本工具

`scripts/send_voice_qq.py` — 独立脚本，直接将 MP3 文件发送为 QQ 语音消息：

```bash
python3 scripts/send_voice_qq.py /path/to/audio.mp3
```

### 配套 Skill（推荐安装）

本仓库附带一个 Hermes Skill，包含完整的百炼 TTS 使用指南和 SOUL.md 决策树模板：

```bash
hermes skills install \
  https://raw.githubusercontent.com/kingsznhone/hermes-bailian-tts/master/skill/SKILL.md
```

安装后在 Hermes 对话中加载：`/skill bailian-tts-usage`

> 通用 TTS 插件设计方法论请加载：`/skill hermes-custom-tts-integration`

## API 端点

```
POST https://{workspace_id}.cn-beijing.maas.aliyuncs.com/api/v1/services/audio/tts/SpeechSynthesizer
```

请求体：

```json
{
    "model": "qwen-audio-3.1-tts-flash",
    "input": {
        "text": "待合成文本",
        "voice": "baiqinglan_v3.1",
        "format": "mp3",
        "instruction": "用温柔的语气"
    }
}
```

响应：

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

## 计费

`qwen-audio-3.1-tts-flash` 按 **Token** 计费（输入 + 输出 Token，见响应 `usage` 字段）。

参考：[阿里云百炼计费文档](https://help.aliyun.com/zh/model-studio/billing-for-model-studio)

## Agent 行为调优

在 Gateway 平台上，建议让 Agent 像一个秘书——**短语音摘要 + 长文字详情**，而非全文朗读。

将以下规则写入 `~/.hermes/SOUL.md`：

```markdown
## TTS Behavior on Gateway Platforms (qqbot, telegram, discord, etc.)

When the conversation source is a gateway platform (NOT webui/cli/tui):
- Short replies (≤ 50 Chinese chars): May speak full text.
- Long replies (> 50 Chinese chars): NEVER speak full text. Instead, first call
  text_to_speech with a 10–30 char spoken summary, then deliver full text.
- Task completion: Always end with spoken confirmation.
- Do NOT call text_to_speech on CLI/TUI/WebUI sessions.
```

完整模板见 `SOUL_TEMPLATE.md`。

## 目录结构

```
hermes-bailian-tts/
├── plugin.yaml              # 插件元数据
├── __init__.py              # TTSProvider 实现
├── README.md                # 中文文档
├── README_EN.md             # English docs
├── SOUL_TEMPLATE.md         # Agent 行为规则模板
├── skill/                   # 配套 Skill（可独立安装）
│   └── SKILL.md             # Skill 主文件（含完整框架指南 + 决策树模板）
└── scripts/
    └── send_voice_qq.py     # QQ Bot 语音发送工具
```

## 相关资源

- [Hermes 自定义 TTS 集成 Skill](https://github.com/nesquena/hermes-agent) — 通用 TTS 接入框架指南
- [阿里云百炼语音合成文档](https://help.aliyun.com/zh/model-studio/tts-model/)
- [Qwen-Audio-TTS HTTP API 参考](https://docs.bailian.console.aliyun.com/zh/model-studio/qwen-audio-tts-http-api)
- [QQ Bot API 文档](https://bot.q.qq.com/wiki/develop/api-v2/)

## 许可

MIT
