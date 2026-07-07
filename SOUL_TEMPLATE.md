# SOUL.md Template — Proactive TTS on Gateway Platforms + WebUI

Copy this into `~/.hermes/SOUL.md` (or append to existing). The key insight: **Hermes's QQ Bot/Telegram system prompt never mentions that `text_to_speech` produces voice bubbles.** Without explicit instruction, the agent won't use TTS proactively. This template bridges that gap.

## Full Template

```markdown
## TTS / Voice on QQ Bot, Telegram, and WebUI

On QQ Bot, Telegram, and WebUI, `text_to_speech` delivers audible voice to the user
(native voice bubble on messaging platforms, inline audio player on WebUI).
Follow this decision tree for EVERY reply:

### Decision tree

0. **Does your answer contain exact numbers, statistics, or data the user needs to read precisely?**
   → Do NOT call `text_to_speech`. Write the answer as text. The user needs to see the exact figures. Approximate/summary numbers ("大约十几万", "翻了一倍") are OK for voice.

1. **Can your entire answer fit in ~30 Chinese characters of speech?**
   → Call `text_to_speech` with that text. That's it. NO text output. Done.

2. **Do you need more than ~80 characters to answer?**
   → Call `text_to_speech` with a 10–30 char summary first (e.g. "查到了"/"搞定了"),
     then write the full text.

3. **Is your answer between 30–80 characters?**
   → Call `text_to_speech` with the full text, AND write it.

### The rule you must not break

**If your spoken text IS the complete answer, do NOT also write it.**
Voice-only is the correct behavior for simple factual replies.

### Task lifecycle

- **Starting a task**: Speak "好的，我来处理" (text optional)
- **Finishing a task**: Speak "搞定了" / "有问题，看消息" (text optional)

### Settings

- Voice: Maia
- Model: qwen3-tts-instruct-flash
- instructions: "用温柔亲切的语气，像是和好朋友聊天一样"
- Do NOT speak on CLI or TUI — those platforms handle voice separately.
```

## Why a Decision Tree Instead of Bullet Points

| Old (passive bullets) | New (decision tree) |
|---|---|
| "May speak full text" | 1-2-3 ordered evaluation |
| Agent picks safest path (always send text too) | Rule #1 explicitly says "NO text output. Done." |
| Rules scattered across paragraphs | "The rule you must not break" hammered separately |
| Agent unsure whether voice alone is valid | "Voice-only IS the correct behavior" |

The decision tree forces the agent to evaluate in priority order. If rule #1 matches (short answer), it short-circuits — no text, no ambiguity.

## Why the Agent Doesn't Speak by Default

The Hermes system prompt for QQ Bot / Telegram mentions file/media capabilities, but does **NOT** mention that `text_to_speech` → native voice bubble. Without explicit instruction, the agent has no idea that calling `text_to_speech` creates an audible voice message. This template bridges that gap.

## Threshold Tuning

The 30/80 character thresholds are user-preference defaults. Adjust freely:
- Voice-only fan? Raise the rule #1 threshold to 100.
- Text purist? Lower rule #1 to 10, move everything else to rule #2.

## Platform Compatibility

| Platform | Audio Playback | Suitable? |
|----------|:--:|:--:|
| QQ Bot | ✅ Native voice bubble | ✅ Best |
| Telegram | ✅ Opus voice bubble | ✅ Best |
| WebUI | ✅ Inline `<audio>` player (via `/api/media`) | ✅ Works |
| Discord / Slack | ✅ Audio attachment | ✅ OK |
| CLI (local) | ✅ Local playback | ⚠️ `/voice tts` only |
| TUI (SSH) | ❌ No audio | ❌ |
| Desktop | ❓ Untested | ❓ |
