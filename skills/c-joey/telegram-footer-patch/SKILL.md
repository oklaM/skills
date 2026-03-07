---
name: telegram-footer-patch
description: Patch OpenClaw gateway reply pipeline to auto-append a single-line Telegram footer (`🧠 Model + 📊 Context`) in private chats, with backup, rollback, and post-restart verification. Use when user asks to make reply footer persistent at platform layer instead of prompt-only output.
---

# Telegram Footer Patch

实现 Telegram 私聊自动尾注（平台层注入，不依赖模型记忆）。

## 执行步骤

1. 预检查（仅预览）

```bash
python3 scripts/patch_reply_footer.py --dry-run
```

2. 应用补丁（自动备份）

```bash
python3 scripts/patch_reply_footer.py
```

3. 重启网关（高风险动作，先确认）

```bash
openclaw gateway restart
```

4. 最小测试
- 给 bot 发：`测试`
- 确认尾注存在且为单行：
  - `🧠 Model: ... 📊 Context: ...`

## 回滚

```bash
python3 scripts/revert_reply_footer.py
openclaw gateway restart
```

## 说明

- 仅对 `dist/reply-*.js` 进行补丁；脚本会写入 marker，避免重复注入。
- 升级 OpenClaw 后补丁可能被覆盖；升级后重新执行 `patch_reply_footer.py`。
- 若 `Context` 显示异常（如 `--/--`），说明数据链路未完全可用，不代表注入失败。
