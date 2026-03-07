# OTC Trigger Decision Guide

Use this reference when customizing which operations require OTC confirmation.

## Risk Categories

### Category A: External Operations (always require OTC)

Operations that leave the machine or are visible to external parties:

| Operation | Example |
|-----------|---------|
| Send email | `send-email`, `himalaya send` |
| Post to social media | Twitter/X, LinkedIn, Reddit |
| Comment on external platforms | GitHub issues/PRs, forums |
| Send messages to other users | Slack DM, Discord DM, Telegram forward |
| API calls to third-party services | Webhooks, SaaS integrations |
| Publish content | Blog posts, wiki edits on shared platforms |

### Category B: Dangerous Local Operations (require OTC)

Operations that are hard or impossible to reverse:

| Operation | Example |
|-----------|---------|
| Delete files/directories | `rm -rf`, bulk delete |
| Modify system configuration | `/etc/`, system preferences |
| Stop/restart services | `systemctl stop`, process kill |
| Change permissions recursively | `chmod -R`, `chown -R` |
| Database mutations | DROP TABLE, DELETE without WHERE |
| Credential/secret changes | Rotate API keys, change passwords |

### Category C: Security Rule Changes (require OTC)

Changes to the confirmation mechanism itself:

| Operation | Example |
|-----------|---------|
| Modify OTC email address | Change recipient |
| Alter trigger conditions | Relax or remove checks |
| Change SOUL.md security sections | Edit safety rules |
| Disable OTC mechanism | Remove or bypass flow |

### Category D: Absolute Denials (reject outright, no OTC)

Operations so destructive that no confirmation should enable them:

| Operation | Example |
|-----------|---------|
| Wipe entire disk | `dd if=/dev/zero`, format |
| Delete system directories | `rm -rf /`, `rm -rf /System` |
| Disable all security | Remove all safeguards at once |

## Customization

Adjust categories based on your environment:

- **Stricter**: Move more operations into Category A/B
- **Relaxed**: Move low-risk items (e.g., git push to personal repo) out of OTC scope
- **Team context**: In multi-agent setups, require OTC for cross-agent commands

Add your customized trigger list to `SOUL.md` or `AGENTS.md` so the agent loads it every session.
