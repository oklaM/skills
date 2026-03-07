# Seede Skill for Open Claw

> **The Ultimate AI Design Skill for Open Claw & Agents.**
> Generate professional UI, social media graphics, posters, and more directly via Open Claw.

This repository contains the **Seede Skill**, enabling [Open Claw](https://github.com/openclaw/openclaw) (and other compatible agents) to generate high-quality designs using [Seede AI](https://seede.ai).

## Why Seede Skill?

- 🚀 **State-of-the-Art Generation**: Uses the latest AI models to create high-quality, editable designs.
- 🤖 **Agent-First**: Designed specifically for autonomous agents to control design parameters.
- 🎨 **Brand Consistency**: Supports brand colors and asset injection.
- 🛠️ **Full Control**: Precise control over resolution, format, and scene types.

## Installation

### For Open Claw

Add this repository to your Open Claw configuration or skill list.

### Standalone CLI

You can also use the underlying CLI tool directly:

```bash
npm install -g seede-cli
```

## Usage

### As an Open Claw Skill

Once the skill is enabled, you can ask Open Claw to perform design tasks:

> "Design a modern tech conference poster with neon accents."
> "Create a social media banner for a coffee shop."

The agent will use the `seede-design` skill to fulfill these requests.

### Configuration

The skill requires the `SEEDE_API_TOKEN` environment variable to be set.

```bash
export SEEDE_API_TOKEN="your_api_token"
```

## Features

- **Text to Design**: Generate complex designs from natural language.
- **Asset Management**: Upload and manage logos, product shots, and reference images.
- **Design Management**: List, search, and retrieve design URLs.

## Manual Usage (CLI)

If you want to use the tool manually:

**Interactive Mode:**

```bash
seede create
```

**Command Line (Agent Mode):**

```bash
seede create --no-interactive \
  --prompt "Modern tech conference poster with neon accents" \
  --scene "poster" \
  --format "png"
```

## Skill Metadata

This repository includes a `SKILL.md` file that defines the skill capabilities and metadata for the agent system.
