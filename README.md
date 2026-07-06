# Hermes Bailian TTS Plugin

[English](README_EN.md) | 中文

阿里云百炼 (Bailian / DashScope) Qwen-TTS 语音合成插件，让 Hermes Agent 通过网关平台（QQ Bot / Telegram 等）用高质量中文语音朗读回答。

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

- **Qwen3-TTS-Instruct-Flash** — 支持指令控制的 HTTP 语音合成
- **7 种系统音色** — 中文男/女声 (Maia, Cherry, Stella, Harry, Liam) + 英文 (Emma, Henry)
- **指令控制** — 用自然语言控制语速、情绪、风格（"用温柔的语气，语速稍慢"）
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
  voice: Maia
  model: qwen3-tts-instruct-flash

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
| `tts.voice` | `Maia` | 音色 ID（见下方音色表） |
| `tts.model` | `qwen3-tts-instruct-flash` | 模型 ID |
| `tts.instructions` | — | (仅 instruct 模型) 指令文本 |

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

| ID | 描述 | 语言 |
|------|------|------|
| `Maia` | 温柔女声 | 中文 |
| `Cherry` | 活力女声 | 中文 |
| `Stella` | 沉稳女声 | 中文 |
| `Harry` | 儒雅男声 | 中文 |
| `Liam` | 阳光男声 | 中文 |
| `Emma` | 知性女声 | 英文 |
| `Henry` | 磁性男声 | 英文 |

## 模型

| ID | 指令控制 | 说明 |
|------|:--:|------|
| `qwen3-tts-instruct-flash` | ✓ | 推荐。支持自然语言调语速/情绪/风格 |
| `qwen3-tts-flash` | ✗ | 基础版，固定风格 |

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

CLI 下 `/voice tts` 由框架层自动处理（全文截断 4000 字朗读）。WebUI 不支持插件音频内联播放，请使用浏览器自带的 🔊 按钮。

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
POST https://{workspace_id}.cn-beijing.maas.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation
```

请求体：

```json
{
    "model": "qwen3-tts-instruct-flash",
    "input": {
        "text": "待合成文本",
        "voice": "Maia",
        "language_type": "Chinese",
        "instructions": "用温柔的语气"
    }
}
```

响应：

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

## 计费

按输入字符计费，输出不计费。Qwen3-TTS-Instruct-Flash 约 **1 元/万字符**。

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
- [QQ Bot API 文档](https://bot.q.qq.com/wiki/develop/api-v2/)

## 许可

MIT
