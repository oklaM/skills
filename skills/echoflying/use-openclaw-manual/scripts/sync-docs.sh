#!/bin/bash
# use-openclaw-manual 技能 - 文档同步脚本
# 同步 OpenClaw 官方文档到本地

set -e

REPO="openclaw/openclaw"
DOCS_PATH="docs/"
TEMP_REPO="/tmp/openclaw-docs-check"

# 技能目录（动态获取）
SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# 可配置路径（支持环境变量覆盖）
LOCAL_DOCS="${OPENCLAW_MANUAL_PATH:-$HOME/.openclaw/workspace/docs/openclaw_manual}"
LAST_COMMIT_FILE="${LAST_COMMIT_FILE:-$LOCAL_DOCS/.last-docs-commit}"
LOG_FILE="${DOC_UPDATE_LOG:-$SKILL_DIR/docs-update.log}"

# 通知渠道（支持环境变量覆盖）
NOTIFY_CHANNEL="${DOC_NOTIFY_CHANNEL:-webchat}"

# 检测当前渠道类型，自动选择通知方式
get_notification_channel() {
  # 优先使用当前会话渠道（webchat/discord/telegram 等）
  # 如果无法获取，默认使用 webchat
  echo "webchat"
}

log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
  echo "$1"
}

# 获取最新 commit (仅 docs 目录)
get_latest_commit() {
  curl -s "https://api.github.com/repos/$REPO/commits?path=$DOCS_PATH&per_page=1" | \
    python3 -c "import sys,json; d=json.load(sys.stdin); print(d[0]['sha'] if d else '')"
}

# 获取变更文件列表
get_changed_files() {
  local old_commit=$1
  local new_commit=$2
  local sync_type=$3
  
  if [ "$sync_type" = "full" ]; then
    # 首次同步：获取所有 docs 文件
    curl -s "https://api.github.com/repos/$REPO/git/trees/$new_commit?recursive=1" | \
      python3 -c "import sys,json; d=json.load(sys.stdin); files=[f['path'] for f in d.get('tree',[]) if f['path'].startswith('docs/') and f['type']=='blob']; print('\n'.join(files))"
  else
    # 增量同步：获取两个 commit 之间的变更文件
    curl -s "https://api.github.com/repos/$REPO/compare/$old_commit...$new_commit" | \
      python3 -c "import sys,json; d=json.load(sys.stdin); files=[f['filename'] for f in d.get('files',[]) if f['filename'].startswith('docs/')]; print('\n'.join(files))"
  fi
}

# 同步文档
sync_docs() {
  local sync_type=$1
  local latest_commit=$2
  local changed_files=$3
  local files_count=$4
  
  log "📥 开始同步 $files_count 个文件 ($sync_type)..."
  
  # 清理临时目录
  rm -rf "$TEMP_REPO"
  mkdir -p "$TEMP_REPO"
  cd "$TEMP_REPO"
  
  # 初始化 git 仓库并配置 sparse-checkout
  git init >/dev/null 2>&1
  git remote add origin https://github.com/$REPO.git >/dev/null 2>&1
  git config core.sparseCheckout true >/dev/null 2>&1
  echo "docs/" > .git/info/sparse-checkout
  
  # 浅克隆 docs 目录
  git pull --depth 1 origin main >/dev/null 2>&1
  
  # 如果是首次同步，清空本地目录
  if [ "$sync_type" = "full" ]; then
    log "🗑️ 清空本地文档目录..."
    rm -rf "$LOCAL_DOCS"
    mkdir -p "$LOCAL_DOCS"
  fi
  
  # 同步到本地
  echo "$changed_files" | while read file; do
    if [ -n "$file" ] && [ -f "$TEMP_REPO/$file" ]; then
      # 提取相对路径 (去掉 docs/ 前缀)
      REL_PATH="${file#docs/}"
      TARGET_DIR="$LOCAL_DOCS/$(dirname "$REL_PATH")"
      
      # 创建目录并复制文件
      mkdir -p "$TARGET_DIR"
      cp "$TEMP_REPO/$file" "$TARGET_DIR/"
    fi
  done
  
  # 清理临时目录
  cd - >/dev/null
  rm -rf "$TEMP_REPO"
  
  log "✅ 同步完成"
}

# 发送通知（支持环境变量指定渠道）
send_notification() {
  local files_count=$1
  local sync_type=$2
  
  local NOTIFY_MSG="📚 OpenClaw 文档更新：**$files_count** 个文件"
  
  # 发送到指定渠道（默认 webchat，可通过 DOC_NOTIFY_CHANNEL 覆盖）
  # 如果失败，记录日志但不中断流程
  openclaw message send -t "$NOTIFY_CHANNEL" -m "$NOTIFY_MSG" 2>/dev/null || {
    log "⚠️ 通知发送失败（渠道：$NOTIFY_CHANNEL）"
  }
  
  log "📢 已通知：$files_count 个文件 ($sync_type)"
}

# 更新 baseline
update_baseline() {
  local commit=$1
  echo "$commit" > "$LAST_COMMIT_FILE"
  log "✅ Baseline 已更新：${commit:0:7}"
}

# 主函数
main() {
  local mode=${1:-"--check"}
  
  case "$mode" in
    --init|--sync)
      log "🔄 开始文档同步..."
      
      # 获取最新 commit
      LATEST_COMMIT=$(get_latest_commit)
      if [ -z "$LATEST_COMMIT" ]; then
        log "❌ 获取 commit 失败"
        exit 1
      fi
      
      # 读取上次记录的 commit
      LAST_COMMIT=$(cat "$LAST_COMMIT_FILE" 2>/dev/null || echo "")
      
      # 判断同步类型
      if [ -z "$LAST_COMMIT" ] || [ "$mode" = "--init" ]; then
        SYNC_TYPE="full"
        log "📝 首次检查，执行完整同步..."
      elif [ "$LATEST_COMMIT" = "$LAST_COMMIT" ]; then
        log "✅ 无更新"
        exit 0
      else
        SYNC_TYPE="incremental"
        log "🔄 发现更新..."
      fi
      
      # 获取变更文件列表
      CHANGED_FILES=$(get_changed_files "$LAST_COMMIT" "$LATEST_COMMIT" "$SYNC_TYPE")
      FILES_COUNT=$(echo "$CHANGED_FILES" | grep -c . || echo 0)
      
      if [ "$FILES_COUNT" -eq 0 ]; then
        log "⚠️ 无 docs 文件"
        update_baseline "$LATEST_COMMIT"
        exit 0
      fi
      
      # 同步文档
      sync_docs "$SYNC_TYPE" "$LATEST_COMMIT" "$CHANGED_FILES" "$FILES_COUNT"
      
      # 发送通知
      send_notification "$FILES_COUNT" "$SYNC_TYPE"
      
      # 更新 baseline
      update_baseline "$LATEST_COMMIT"
      
      # 创建初始化标记
      touch "$SKILL_DIR/.initialized"
      
      log "✅ 同步完成"
      ;;
    
    --check)
      log "🔍 检查文档更新..."
      
      LATEST_COMMIT=$(get_latest_commit)
      LAST_COMMIT=$(cat "$LAST_COMMIT_FILE" 2>/dev/null || echo "")
      
      if [ -z "$LAST_COMMIT" ]; then
        log "⚠️ 未初始化，请运行：clawhub skill run use-openclaw-manual --init"
        exit 1
      elif [ "$LATEST_COMMIT" = "$LAST_COMMIT" ]; then
        log "✅ 文档已是最新"
      else
        log "🔄 发现更新！运行以下命令同步："
        log "   clawhub skill run use-openclaw-manual --sync"
      fi
      ;;
    
    --help)
      echo "用法：sync-docs.sh [选项]"
      echo ""
      echo "选项:"
      echo "  --init     首次初始化（完整同步）"
      echo "  --sync     增量同步（仅更新变更文件）"
      echo "  --check    仅检查更新，不同步"
      echo "  --help     显示帮助"
      echo ""
      ;;
    
    *)
      echo "错误：未知选项 '$mode'"
      echo "运行 'sync-docs.sh --help' 查看帮助"
      exit 1
      ;;
  esac
}

main "$@"
