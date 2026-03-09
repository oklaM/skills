---
name: em-intel
description: >
  Engineering Manager Intelligence: track team performance, engineer contributions, and project health across GitLab/GitHub + Jira/GitHub Issues.
  Use when asked for morning briefs, EOD reviews, team reports, quiet engineer alerts, epic health checks, or weekly newsletters.
  Maps engineer contributions to Jira tickets via feature branch analysis. Supports Slack, Telegram, and email delivery.
  Trigger on: /morning-brief, /eod-review, /team-report, "who worked on X", "which tickets are stalled", "send newsletter", "team performance".
license: MIT
metadata:
  author: larry.l.fang@gmail.com
  version: "1.0.0"
  tags: engineering-manager,gitlab,github,jira,team-performance,morning-brief,eod-review,newsletter,dora
---

# em-intel — Engineering Manager Intelligence

Track team performance, engineer contributions, and project health across GitLab/GitHub + Jira/GitHub Issues.

## Quick Start

```bash
# Copy and fill environment variables
cp .env.example .env

# Install dependencies
pip install -r requirements.txt

# Run morning brief
python em_intel.py morning-brief

# Full help
python em_intel.py --help
```

## Commands

| Command | Description |
|---------|-------------|
| `morning-brief` | Merged yesterday, open PRs >3d, quiet engineers, stalled epics |
| `eod-review` | Today's merges/opens, contributor list, cycle time trend |
| `team-report [--days N]` | Full team performance report |
| `contributions [--engineer NAME] [--days N]` | Branch→ticket contribution map |
| `quiet-engineers` | Engineers with no MR activity |
| `epic-health` | Stalled and unassigned epics |
| `newsletter [--week]` | Weekly digest via configured delivery channel |

## Configuration

Set `EM_CODE_PROVIDER` to `gitlab` or `github`, and `EM_TICKET_PROVIDER` to `jira` or `github_issues`.

Delivery channels: `telegram`, `slack`, `email`, or `print` (stdout fallback).

See `.env.example` for all configuration options.

## Architecture

```
em_intel.py          ← CLI entrypoint (argparse)
adapters/            ← Code platform + ticket system adapters
  base.py            ← Abstract base classes & data models
  gitlab_adapter.py  ← GitLab REST API
  github_adapter.py  ← GitHub REST API
  jira_adapter.py    ← Jira REST API
  github_issues_adapter.py ← GitHub Issues as ticket system
core/                ← Business logic
  branch_mapper.py   ← Map branches → tickets → engineers
  team_pulse.py      ← Quiet engineers, MR trends, cycle times
  jira_health.py     ← Stale epics, unassigned tickets, PR age
  newsletter.py      ← Weekly digest generation
  delivery.py        ← Telegram / Slack / Email / Print routing
commands/            ← Command implementations
  morning_brief.py   ← Morning briefing
  eod_review.py      ← End-of-day review
  team_report.py     ← Full team report
  newsletter.py      ← Newsletter generation & delivery
```
