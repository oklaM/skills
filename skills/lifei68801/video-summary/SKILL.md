---
name: video-summary
version: 1.3.3
description: "AI-powered video summarization for Bilibili, Xiaohongshu, Douyin, and YouTube. Extract insights from video content through automated transcription and intelligent summarization."
metadata:
  openclaw:
    requires:
      bins: ["yt-dlp", "jq", "ffmpeg"]
    install:
      - id: yt-dlp
        kind: pip
        package: yt-dlp
        bins: ["yt-dlp"]
        label: "Install yt-dlp for video/subtitle download"
      - id: jq
        kind: apt
        package: jq
        bins: ["jq"]
        label: "Install jq for JSON processing"
      - id: ffmpeg
        kind: apt
        package: ffmpeg
        bins: ["ffmpeg"]
        label: "Install ffmpeg for audio/video processing"
    setup:
      script: "scripts/setup.sh"
      description: "Conversational setup wizard - OpenClaw guides user through configuration"
      conversational: true
---

# Video Summary Skill

Intelligent video summarization for multi-platform content. Supports Bilibili, Xiaohongshu, Douyin, YouTube, and local video files.

## What It Does

- **Auto-detect platform** from URL (Bilibili/Xiaohongshu/Douyin/YouTube)
- **Extract subtitles/transcripts** using platform-specific methods
- **Generate structured summaries** with key insights, timestamps, and actionable takeaways
- **Multi-format output** (plain text, JSON, Markdown)
- **Direct LLM integration** — outputs ready-to-use summaries
- **Automatic cleanup** — no temp file leaks

---

## Conversational Setup

After installation, OpenClaw will guide you through configuration step by step.

### Configuration Flow

**Step 1: Select AI Provider**
OpenClaw will ask: Which AI service do you want to use?
- 1) Use existing OpenClaw configuration (auto-detected)
- 2) OpenAI
- 3) Zhipu GLM
- 4) DeepSeek
- 5) Moonshot/Kimi
- 6) Custom

**Step 2: Enter API Key**
Based on your selection, OpenClaw will prompt for the API Key.

Get it from:
- OpenAI: https://platform.openai.com/api-keys
- Zhipu: https://open.bigmodel.cn/
- DeepSeek: https://platform.deepseek.com/
- Moonshot: https://platform.moonshot.cn/

**Step 3: Select Whisper Model**
For audio transcription on videos without subtitles:
- tiny - Fastest, quick preview
- base - Balanced, daily use (recommended)
- small - Higher accuracy
- medium - High precision
- large - Highest precision

**Step 4: Configure Cookies (Optional)**
Xiaohongshu and Douyin may need cookies to download videos. You can skip and configure later.

### Manual Trigger

If configuration is incomplete, say:
> "help me configure video-summary"

Or run:
```bash
~/.openclaw/workspace/skills/video-summary/scripts/setup.sh
```

### Configuration Files

- Config file: `~/.config/video-summary/config.sh`
- State file: `~/.config/video-summary/setup-state.json`

### Check Configuration Status

```bash
~/.openclaw/workspace/skills/video-summary/scripts/config-status.sh
```

---

## Conversational Setup Guide

**For OpenClaw Agent: Guide users through configuration step by step.**

### Trigger Conditions

Start conversational setup when:
- User says "help me configure video-summary"
- User says "configure video-summary"
- Or on first use after skill installation

### Configuration Steps

#### Step 1: Check Configuration Status

```bash
~/.openclaw/workspace/skills/video-summary/scripts/config-status.sh
```

If returns `status: "complete"`, configuration is done.
If returns `status: "pending"` or `status: "not_started"`, start conversational setup.

#### Step 2: Select AI Provider

**First, check if OpenClaw has existing LLM config:**

```bash
# Detect OpenClaw's existing LLM configuration
cat ~/.openclaw/agents/main/agent/models.json 2>/dev/null | jq -r '.providers | to_entries[0] | "\(.key) \(.value.apiKey // .value.key)"' 2>/dev/null
```

**OpenClaw should ask:**

> 🎬 video-summary needs an AI service to generate summaries. Which one do you want to use?
> 
> 1. Use existing OpenClaw configuration (detected: {provider})
> 2. OpenAI
> 3. Zhipu GLM
> 4. DeepSeek
> 5. Moonshot/Kimi
> 6. Custom endpoint
> 
> Reply with number or name.

**Process user answer:**

```bash
# If user selects option 1 (use existing OpenClaw config):
~/.openclaw/workspace/skills/video-summary/scripts/config-update.sh use_openclaw_config "true"

# Otherwise:
~/.openclaw/workspace/skills/video-summary/scripts/config-update.sh api_provider "openai"
# or "zhipu" / "deepseek" / "moonshot" / custom URL
```

#### Step 3: Enter API Key

**OpenClaw should ask:**

> 🔑 Please enter your API Key.
> 
> Get it from:
> - OpenAI: https://platform.openai.com/api-keys
> - Zhipu: https://open.bigmodel.cn/
> - DeepSeek: https://platform.deepseek.com/
> - Moonshot: https://platform.moonshot.cn/

**Process user answer:**

```bash
~/.openclaw/workspace/skills/video-summary/scripts/config-update.sh api_key "sk-xxx..."
```

#### Step 4: Select Whisper Model

**OpenClaw should ask:**

> 🎤 Videos without subtitles need Whisper for transcription. Select model:
> 
> 1. tiny - Fastest (quick preview)
> 2. base - Balanced (recommended)
> 3. small - Higher accuracy
> 4. medium - High precision
> 5. large - Highest precision
> 
> Reply with number. Default is base.

**Process user answer:**

```bash
~/.openclaw/workspace/skills/video-summary/scripts/config-update.sh whisper_model "base"
```

#### Step 5: Configure Cookies (Optional)

**OpenClaw should ask:**

> 🍪 Xiaohongshu and Douyin may need cookies to download videos. Configure now?
> 
> - Reply "skip" to skip for now
> - Reply "configure" to set up

**If user says skip:**

```bash
~/.openclaw/workspace/skills/video-summary/scripts/config-update.sh cookies_skip "true"
```

**If user wants to configure:**

Ask for each platform's cookies (Xiaohongshu, Douyin, Bilibili), then save:

```bash
~/.openclaw/workspace/skills/video-summary/scripts/config-update.sh cookies '{"xiaohongshu": "...", "douyin": "..."}'
```

#### Step 6: Configuration Complete

When all steps are done, OpenClaw should say:

> ✅ video-summary is now configured!
> 
> You can use it now:
> - "Summarize this video: [URL]"
> - "Analyze this Bilibili video: [URL]"

### Auto-detect Existing OpenClaw Configuration

If user has already configured an API in OpenClaw (e.g., Zhipu), auto-detect and use it:

```bash
# Detect OpenClaw configuration
cat ~/.openclaw/agents/main/agent/models.json | jq '.providers | to_entries[0]'
```

If detected, ask user:

> Detected existing OpenClaw configuration for Zhipu API. Use this? (confirm/no)

If user confirms, use detected config to complete setup.

---

## Quick Start

### Check Dependencies

```bash
# Check all required tools
yt-dlp --version && jq --version && ffmpeg -version

# If missing, install
pip install yt-dlp
apt install jq ffmpeg  # or: brew install jq ffmpeg
```

### Basic Usage

```bash
# Standard summary
video-summary "https://www.bilibili.com/video/BV1xx411c7mu"

# With chapter segmentation
video-summary "https://www.youtube.com/watch?v=xxxxx" --chapter

# JSON output for programmatic use
video-summary "https://www.xiaohongshu.com/explore/xxxxx" --json

# Subtitle only (no AI summary)
video-summary "https://v.douyin.com/xxxxx" --subtitle

# Save to file
video-summary "https://www.bilibili.com/video/BV1xx" --output summary.md

# Use cookies for restricted content
video-summary "https://www.xiaohongshu.com/explore/xxxxx" --cookies cookies.txt
```

### In OpenClaw Agent

Just say:
> "Summarize this video: [URL]"

The agent will automatically:
1. Detect the platform
2. Extract video content
3. Generate a structured summary

---

## Commands Reference

| Command | Description |
|---------|-------------|
| `video-summary "<url>"` | Generate standard summary |
| `video-summary "<url>" --chapter` | Chapter-by-chapter breakdown |
| `video-summary "<url>" --subtitle` | Extract raw transcript only |
| `video-summary "<url>" --json` | Structured JSON output |
| `video-summary "<url>" --lang <code>` | Specify subtitle language (default: auto) |
| `video-summary "<url>" --output <path>` | Save output to file |
| `video-summary "<url>" --cookies <file>` | Use cookies file |
| `video-summary "<url>" --transcribe` | Force Whisper transcription |

---

## How It Works

### Platform Support Matrix

| Platform | Subtitle Extraction | Notes |
|----------|-------------------|-------|
| **YouTube** | Native CC + auto-generated | Best support |
| **Bilibili** | Native CC + backup methods | Requires video ID extraction |
| **Xiaohongshu** | Limited (OCR fallback) | No native subtitles, uses transcription |
| **Douyin** | Limited (OCR fallback) | Short-form video, may need transcription |
| **Local files** | Whisper transcription | Supports mp4, mkv, webm, mp3, etc. |

### Supported URL Formats

**YouTube:**
- `https://www.youtube.com/watch?v=xxxxx`
- `https://youtu.be/xxxxx`

**Bilibili:**
- `https://www.bilibili.com/video/BV1xx411c7mu`
- `https://www.bilibili.com/video/av123456`

**Xiaohongshu:**
- `https://www.xiaohongshu.com/explore/xxxxx`
- `https://xhslink.com/xxxxx` (short link)

**Douyin:**
- `https://www.douyin.com/video/xxxxx`
- `https://v.douyin.com/xxxxx` (short link)

### Processing Pipeline

```
URL Input
    ↓
Platform Detection
    ↓
Subtitle Extraction (yt-dlp / Whisper)
    ↓
Content Chunking (if long)
    ↓
LLM Summarization (OpenAI API / Agent)
    ↓
Structured Output
    ↓
Auto Cleanup
```

---

## Performance Estimation

### Whisper Transcription Time

| Video Duration | tiny | base | small | medium |
|---------------|------|------|-------|--------|
| 5 min | ~30s | ~1m | ~2m | ~4m |
| 15 min | ~1.5m | ~3m | ~6m | ~12m |
| 30 min | ~3m | ~6m | ~15m | ~30m |
| 60 min | ~6m | ~12m | ~30m | ~60m |

**Notes:**
- GPU significantly faster (3-10x)
- `base` model recommended for balance
- First run downloads model (~150MB for base)

### Subtitle Extraction Time

| Platform | Time | Notes |
|----------|------|-------|
| YouTube | ~5s | Direct subtitle download |
| Bilibili | ~5s | Direct subtitle download |
| Xiaohongshu | ~3m | Requires transcription |
| Douyin | ~2m | Requires transcription |

---

## Advanced Configuration

### Whisper for Transcription

For platforms without native subtitles (Xiaohongshu, Douyin), install Whisper:

```bash
pip install openai-whisper
```

Then configure:
```bash
export VIDEO_SUMMARY_WHISPER_MODEL=base  # tiny, base, small, medium, large
```

### OpenAI API for Summarization

For direct LLM-powered summaries, configure OpenAI API:

```bash
# Required for direct summarization
export OPENAI_API_KEY=sk-xxx

# Optional: Custom API endpoint
export OPENAI_BASE_URL=https://api.openai.com/v1

# Optional: Model selection
export OPENAI_MODEL=gpt-4o-mini
```

**Without API key:** Script outputs structured request for agent to process.

### Cookie Configuration for Restricted Content

Some platforms require authentication for certain content:

```bash
# Method 1: Command line
video-summary "https://www.xiaohongshu.com/explore/xxxxx" --cookies cookies.txt

# Method 2: Environment variable
export VIDEO_SUMMARY_COOKIES=/path/to/cookies.txt
```

**How to get cookies:**

1. Install browser extension: "Get cookies.txt LOCALLY"
2. Login to the platform
3. Export cookies to file

### Custom Summary Prompt

Create `~/.video-summary/prompt.txt`:

```markdown
You are a professional video content analyst. Generate a structured summary:

## Key Insights
- List 3-5 core arguments

## Key Information
- Data, cases, quotes

## Action Items
- Specific actions viewers can take

## Timestamp Navigation
- Key moments with timestamps and descriptions
```

---

## Output Formats

### Standard Output (default)

```markdown
# Video Title

**Duration**: 12:34
**Platform**: Bilibili
**Author**: Tech Creator

## Core Content
This video explains...

## Key Points
1. Point one
2. Point two
3. Point three

## Timestamps
- 00:00 Introduction
- 02:15 Core concept
- 08:30 Case study
- 11:45 Summary
```

### JSON Output (`--json`)

```json
{
  "title": "Video Title",
  "platform": "bilibili",
  "duration": 754,
  "author": "Creator Name",
  "summary": "Core content summary...",
  "keyPoints": ["Point 1", "Point 2", "Point 3"],
  "chapters": [
    {"time": 0, "title": "Intro", "summary": "..."},
    {"time": 135, "title": "Core Concept", "summary": "..."}
  ],
  "transcript": "Full transcript text..."
}
```

---

## Technical Details

### Dependencies

| Tool | Required | Purpose |
|------|----------|---------|
| **yt-dlp** | Yes | Video/subtitle downloader |
| **jq** | Yes | JSON processing |
| **ffmpeg** | Yes | Audio/video processing |
| **whisper** | Optional | Local transcription |

### File Structure

```
~/.openclaw/workspace/skills/video-summary/
├── SKILL.md              # This file
├── scripts/
│   ├── video-summary.sh  # Main CLI script
│   ├── setup.sh          # Setup wizard
│   ├── config-status.sh  # Check config status
│   └── config-update.sh  # Update config
└── references/
    └── platform-support.md  # Detailed platform notes
```

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | auto-detect | OpenAI API key (auto-detects OpenClaw config) |
| `OPENAI_BASE_URL` | auto-detect | Custom API endpoint (auto-detects OpenClaw config) |
| `OPENAI_MODEL` | `gpt-4o-mini` | Model for summarization |
| `VIDEO_SUMMARY_WHISPER_MODEL` | `base` | Whisper model size |
| `VIDEO_SUMMARY_COOKIES` | - | Path to cookies file |

**API Configuration Priority:**
1. Environment variables `OPENAI_API_KEY` / `OPENAI_BASE_URL`
2. OpenClaw config file `~/.openclaw/agents/main/agent/models.json`
3. Manual configuration (setup.sh or config.sh)

---

## Troubleshooting

### "No subtitles found"

- The video may not have subtitles/CC
- Try `--transcribe` to use Whisper
- For Xiaohongshu/Douyin, transcription is required

### "yt-dlp: command not found"

```bash
pip install yt-dlp
# or
brew install yt-dlp
```

### "Missing required dependencies"

```bash
# Install all dependencies
pip install yt-dlp
apt install jq ffmpeg  # Ubuntu/Debian
# or
brew install jq ffmpeg  # macOS
```

### "Video too long"

Long videos (>1h) are automatically chunked:
- Split into 10-minute segments
- Summarize each segment
- Merge into final summary

### "Failed to fetch video info"

- Video may be private or deleted
- Try `--cookies` for restricted content
- Region-locked videos may not work

### "Rate limited"

- Too many requests to platform
- Wait a few minutes
- Use `--cookies` for authenticated access

---

## Comparison

| Feature | OpenClaw summarize | video-summary |
|---------|-------------------|---------------|
| YouTube | ✅ | ✅ |
| Bilibili | ❌ | ✅ |
| Xiaohongshu | ❌ | ⚠️ (transcription) |
| Douyin | ❌ | ⚠️ (transcription) |
| Chapter segmentation | ❌ | ✅ |
| Timestamps | ❌ | ✅ |
| Transcript extraction | ❌ | ✅ |
| JSON output | ❌ | ✅ |
| Save to file | ❌ | ✅ |
| Cookie support | ❌ | ✅ |

---

## References

- [Platform Support Details](references/platform-support.md)
- [yt-dlp Documentation](https://github.com/yt-dlp/yt-dlp)
- [OpenAI Whisper](https://github.com/openai/whisper)

---

## Contributing

Found a bug or want to add platform support?
- Open an issue on ClawHub
- Submit a PR with your improvements

---

## Changelog

### v1.3.0 (2026-03-08)
- Conversational setup: OpenClaw guides user through configuration after installation
- Added config-status.sh to query configuration status
- Added config-update.sh to handle configuration updates
- setup.sh is now non-interactive, creates config state then hands off to OpenClaw
- SKILL.md includes detailed conversational setup guide

### v1.2.2 (2026-03-08)
- Redesigned setup wizard with question-driven flow
- Simplified English-only interface
- Clearer step-by-step guidance

### v1.2.1 (2026-03-08)
- Auto-detect OpenClaw API config
- Setup wizard uses detected config by default
- Simplified setup flow

### v1.2.0 (2026-03-08)
- Added interactive setup wizard
- Added detailed configuration guide
- Added API key acquisition guide
- Added cookie extraction guide
- Added Whisper model selection guide

### v1.1.0 (2026-03-08)
- Added direct LLM integration
- Added `--output` parameter
- Added `--cookies` parameter
- Added automatic temp file cleanup
- Added progress estimation
- Added dependency checking
- Added URL format documentation
- Added performance estimation table
- Fixed metadata dependencies

### v1.0.0
- Initial release

---

*Make video content accessible. Let AI watch, so you can learn.*
