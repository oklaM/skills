# use-openclaw-manual - 基于文档的 OpenClaw 配置技能

## 描述

在配置 OpenClaw 前自动查阅本地官方文档，确保配置操作准确、规范。首次使用时自动同步最新文档到本地。

**通知渠道**: 默认使用 webchat，可通过环境变量 `DOC_NOTIFY_CHANNEL` 覆盖（如：discord、telegram 等）。

## 核心功能

1. **文档同步** - 从 GitHub 同步 OpenClaw 官方文档到本地
2. **文档搜索** - 快速搜索本地文档中的配置相关信息
3. **配置规范** - 强制要求配置前查阅文档
4. **引用来源** - 所有配置方案必须引用文档来源

## 首次安装

### 1. 安装技能

```bash
clawhub skill install use-openclaw-manual
```

### 2. 配置 Agent（重要）

安装后需要在 **AGENTS.md** 中添加使用指南，让 Agent 知道使用此技能：

```markdown
## 工作流程
1. 配置问题 → 使用 `use-openclaw-manual` 技能搜索文档
   - `clawhub skill run use-openclaw-manual --search <关键词>`
   - 配置方案必须引用文档来源
2. 技能操作 → 使用 `clawhub skill` 命令
3. 系统检查 → 使用 `healthcheck` 技能
4. 变更操作 → 必须用户批准
```

**位置**: `~/.openclaw/workspace-sys/AGENTS.md`（或其他 workspace 的 AGENTS.md）

### 3. 初始化文档

首次使用本技能时，会自动执行文档同步：

```bash
# 技能安装后首次使用时自动触发
clawhub skill run use-openclaw-manual --init
```

**同步内容**:
- 从 `github.com/openclaw/openclaw/docs/` 克隆
- 保存到 `~/.openclaw/workspace/docs/openclaw_manual/`
- 约 713 个文件，44 个子目录
- 耗时约 30 秒

### 手动初始化

如需手动触发同步：

```bash
clawhub skill run use-openclaw-manual --init
```

## 使用方法

### 1. 配置前搜索文档

收到配置需求后，先搜索相关文档：

```bash
# 搜索关键词
clawhub skill run use-openclaw-manual --search "binding"

# 或指定主题
clawhub skill run use-openclaw-manual --search "agent workspace"
clawhub skill run use-openclaw-manual --search "cron schedule"
clawhub skill run use-openclaw-manual --search "tools profile"
```

### 2. 查阅特定主题文档

```bash
# 列出相关文档
clawhub skill run use-openclaw-manual --list "agent"

# 查看文档内容
clawhub skill run use-openclaw-manual --read "concepts/agent-workspace.md"
```

### 3. 检查文档更新

```bash
# 检查是否有新文档
clawhub skill run use-openclaw-manual --check

# 手动同步更新
clawhub skill run use-openclaw-manual --sync
```

### 4. 配置操作规范

**标准流程**:

1. **搜索** - `grep -r` 搜索本地文档
2. **阅读** - 理解相关文档内容
3. **设计** - 基于文档设计配置方案
4. **引用** - 在方案中引用文档来源
5. **批准** - 用户确认方案
6. **执行** - 按方案执行配置

**示例**:

```
用户：帮我配置 Discord 通知

助手：
1. 先查阅文档...
   $ clawhub skill run use-openclaw-manual --search "discord notification"
   
2. 找到相关文档:
   - channels/discord.md
   - automation/notifications.md
   
3. 基于文档设计配置方案:
   [方案内容，引用文档来源]
   
4. 用户批准后执行配置
```

## 文档优先级

| 优先级 | 目录 | 说明 | 查阅时机 |
|--------|------|------|---------|
| **P0** | `concepts/` | 核心概念 | 所有配置前必读 |
| **P1** | `cli/` | 命令参考 | 执行命令前查阅 |
| **P2** | `channels/` | 渠道配置 | 配置渠道时查阅 |
| **P3** | `automation/` | 自动化 | 配置定时任务时查阅 |

## 脚本说明

### sync-docs.sh

**位置**: `scripts/sync-docs.sh`（技能目录内）

**功能**: 同步 OpenClaw 官方文档到本地

**参数**:
- `--init` - 首次初始化（完整同步）
- `--sync` - 增量同步（仅更新变更文件）
- `--check` - 仅检查更新，不同步

**环境变量**:
- `OPENCLAW_MANUAL_PATH` - 文档目录路径（默认：`$HOME/.openclaw/workspace/docs/openclaw_manual`）
- `LAST_COMMIT_FILE` - Baseline 文件路径（默认：`$OPENCLAW_MANUAL_PATH/.last-docs-commit`）
- `DOC_UPDATE_LOG` - 日志文件路径（默认：技能目录内 `docs-update.log`）
- `DOC_NOTIFY_CHANNEL` - 通知渠道（默认：`webchat`）

**输出**:
- 同步文件数量
- 变更文件列表
- 通知（通过指定渠道发送）

### search-docs.sh

**位置**: `scripts/search-docs.sh`（技能目录内）

**功能**: 搜索本地文档

**参数**:
- `--keyword <词>` - 搜索关键词
- `--type <content|filename|title>` - 搜索类型（内容/文件名/标题）
- `--limit <数>` - 结果数量限制

**环境变量**:
- `OPENCLAW_MANUAL_PATH` - 文档目录路径
- `DOC_UPDATE_LOG` - 日志文件路径

## 文件结构

```
use-openclaw-manual/
├── SKILL.md                          # 技能说明
├── run.sh                            # 入口脚本
├── scripts/
│   ├── sync-docs.sh                  # 文档同步脚本
│   └── search-docs.sh                # 文档搜索脚本
└── .initialized                      # 初始化标记文件（自动创建）
```

## 相关文件

| 文件 | 路径 | 用途 |
|------|------|------|
| 本地文档 | `~/.openclaw/workspace/docs/openclaw_manual/` | 官方文档（约 713 个文件） |
| Baseline | `$OPENCLAW_MANUAL_PATH/.last-docs-commit` | 记录同步的 commit hash |
| 日志 | `$DOC_UPDATE_LOG` | 同步日志（默认技能目录内） |

## 自动同步

技能支持定时同步功能，用户可自行配置 crontab：

```bash
# 示例：每天 4:44 AM (Asia/Shanghai) 检查更新
44 4 * * * clawhub skill run use-openclaw-manual --sync
```

### 通知渠道

通过环境变量 `DOC_NOTIFY_CHANNEL` 指定通知渠道：

| 渠道 | 说明 | 配置 |
|------|------|------|
| **webchat** | Web 界面通知 | 默认 |
| **discord** | Discord DM | `DOC_NOTIFY_CHANNEL=discord` |
| **telegram** | Telegram 消息 | `DOC_NOTIFY_CHANNEL=telegram` |
| **其他** | 其他支持的渠道 | 按需设置 |

## 配置规范

### ✅ 必须做

- 配置前必须搜索本地文档
- 配置方案必须引用文档来源
- 文档与经验冲突时，以文档为准
- 定期同步确保文档最新

### ❌ 禁止做

- 未查文档直接配置
- 凭经验或猜测操作
- 忽略文档中的警告
- 跳过用户批准步骤

## 示例场景

### 场景 1: 配置 Agent

```
用户：帮我配置一个新的 agent

助手：
1. 运行：clawhub skill run use-openclaw-manual --search "agent configuration"
2. 查阅：concepts/agent.md, cli/agents.md
3. 设计方案（引用文档）
4. 用户批准
5. 执行配置
```

### 场景 2: 配置定时任务

```
用户：设置一个每天运行的任务

助手：
1. 运行：clawhub skill run use-openclaw-manual --search "cron schedule"
2. 查阅：automation/cron.md, cli/cron.md
3. 设计方案（引用文档）
4. 用户批准
5. 执行配置
```

### 场景 3: 配置通知

```
用户：配置 Discord 通知

助手：
1. 运行：clawhub skill run use-openclaw-manual --search "discord notification"
2. 查阅：channels/discord.md, automation/notifications.md
3. 设计方案（引用文档）
4. 用户批准
5. 执行配置
```

## 故障排除

### 问题：文档目录为空

**原因**: 首次同步未执行或失败

**解决**:
```bash
clawhub skill run use-openclaw-manual --init
```

### 问题：搜索无结果

**原因**: 关键词不匹配或文档未同步

**解决**:
1. 尝试不同关键词
2. 检查文档是否已同步：`ls ~/.openclaw/workspace/docs/openclaw_manual/`
3. 重新同步：`clawhub skill run use-openclaw-manual --sync`

### 问题：同步失败

**原因**: 网络问题或 GitHub API 限流

**解决**:
1. 检查网络连接
2. 等待几分钟后重试
3. 查看日志：`cat ~/.openclaw/workspace-sys/docs-update.log`

## 版本历史

### v1.0.0 (2026-03-05)

- 首次发布
- 文档自动同步
- 文档搜索功能
- 配置操作规范
- 定时更新任务

## 相关技能

- **healthcheck** - 系统健康检查
- **clawhub** - 技能管理
- **skill-creator** - 技能创建

## 许可证

与 OpenClaw 相同

## 支持

- 文档：`~/.openclaw/workspace/docs/openclaw_manual/`
- 社区：https://discord.com/invite/clawd
- 技能市场：https://clawhub.com
