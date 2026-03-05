#!/bin/bash
# use-openclaw-manual 技能 - 文档搜索脚本
# 搜索本地 OpenClaw 官方文档

set -e

# 技能目录（动态获取）
SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# 可配置路径（支持环境变量覆盖）
LOCAL_DOCS="${OPENCLAW_MANUAL_PATH:-$HOME/.openclaw/workspace/docs/openclaw_manual}"
LOG_FILE="${DOC_UPDATE_LOG:-$SKILL_DIR/docs-update.log}"

log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

# 检查文档是否已同步
check_initialized() {
  if [ ! -d "$LOCAL_DOCS" ] || [ -z "$(ls -A $LOCAL_DOCS 2>/dev/null)" ]; then
    echo "❌ 文档未同步"
    echo ""
    echo "请先运行以下命令初始化文档："
    echo "  clawhub skill run use-openclaw-manual --init"
    echo ""
    exit 1
  fi
}

# 搜索文档内容
search_content() {
  local keyword=$1
  local limit=${2:-10}
  
  echo "🔍 搜索内容：'$keyword'"
  echo "📁 搜索路径：$LOCAL_DOCS"
  echo ""
  
  grep -rn "$keyword" "$LOCAL_DOCS" --include="*.md" | head -$limit | while read line; do
    file=$(echo "$line" | cut -d: -f1 | sed "s|$LOCAL_DOCS/||")
    lineno=$(echo "$line" | cut -d: -f2)
    content=$(echo "$line" | cut -d: -f3-)
    
    echo "📄 $file:$lineno"
    echo "   $content"
    echo ""
  done
  
  local count=$(grep -r "$keyword" "$LOCAL_DOCS" --include="*.md" | wc -l)
  echo "---"
  echo "共找到 $count 个匹配项（显示前 $limit 个）"
}

# 搜索文件名
search_filename() {
  local keyword=$1
  local limit=${2:-20}
  
  echo "🔍 搜索文件名：'$keyword'"
  echo "📁 搜索路径：$LOCAL_DOCS"
  echo ""
  
  find "$LOCAL_DOCS" -name "*$keyword*.md" | head -$limit | while read file; do
    echo "📄 ${file#$LOCAL_DOCS/}"
  done
  
  local count=$(find "$LOCAL_DOCS" -name "*$keyword*.md" | wc -l)
  echo ""
  echo "---"
  echo "共找到 $count 个匹配文件（显示前 $limit 个）"
}

# 搜索标题
search_title() {
  local keyword=$1
  local limit=${2:-20}
  
  echo "🔍 搜索标题：'$keyword'"
  echo "📁 搜索路径：$LOCAL_DOCS"
  echo ""
  
  grep -rn "^#" "$LOCAL_DOCS" --include="*.md" | grep -i "$keyword" | head -$limit | while read line; do
    file=$(echo "$line" | cut -d: -f1 | sed "s|$LOCAL_DOCS/||")
    lineno=$(echo "$line" | cut -d: -f2)
    title=$(echo "$line" | cut -d: -f3-)
    
    echo "📄 $file:$lineno"
    echo "   $title"
    echo ""
  done
  
  local count=$(grep -r "^#" "$LOCAL_DOCS" --include="*.md" | grep -i "$keyword" | wc -l)
  echo "---"
  echo "共找到 $count 个匹配标题（显示前 $limit 个）"
}

# 列出目录内容
list_directory() {
  local dir=$1
  
  if [ -d "$LOCAL_DOCS/$dir" ]; then
    echo "📁 目录：$dir"
    echo ""
    ls -1 "$LOCAL_DOCS/$dir" | head -20
  else
    echo "❌ 目录不存在：$dir"
    echo ""
    echo "可用目录:"
    ls -1 "$LOCAL_DOCS" | head -20
  fi
}

# 显示文档内容
read_document() {
  local doc=$1
  local lines=${2:-50}
  
  local file="$LOCAL_DOCS/$doc"
  
  if [ -f "$file" ]; then
    echo "📄 文档：$doc"
    echo ""
    head -$lines "$file"
    echo ""
    echo "---"
    echo "显示前 $lines 行"
  else
    echo "❌ 文档不存在：$doc"
    echo ""
    echo "提示：使用 --search 搜索相关文档"
  fi
}

# 显示统计信息
show_stats() {
  echo "📊 文档统计"
  echo ""
  echo "文档路径：$LOCAL_DOCS"
  echo ""
  
  local file_count=$(find "$LOCAL_DOCS" -type f ! -name ".last-docs-commit" | wc -l)
  local md_count=$(find "$LOCAL_DOCS" -name "*.md" | wc -l)
  local dir_count=$(find "$LOCAL_DOCS" -type d | wc -l)
  local total_lines=$(find "$LOCAL_DOCS" -name "*.md" -exec cat {} \; | wc -l)
  local total_words=$(find "$LOCAL_DOCS" -name "*.md" -exec cat {} \; | wc -w)
  
  echo "总文件数：$file_count 个"
  echo "Markdown 文件：$md_count 个"
  echo "子目录：$dir_count 个"
  echo "总行数：$total_lines 行"
  echo "总词数：$total_words 词"
  echo ""
  
  echo "主要目录:"
  ls -1 "$LOCAL_DOCS" | head -10 | while read dir; do
    if [ -d "$LOCAL_DOCS/$dir" ]; then
      count=$(find "$LOCAL_DOCS/$dir" -type f | wc -l)
      echo "  📁 $dir/ ($count 个文件)"
    fi
  done
}

# 主函数
main() {
  check_initialized
  
  local mode=${1:-"--help"}
  shift || true
  
  case "$mode" in
    --search|-s)
      local keyword=$1
      local type=${2:-"content"}
      local limit=${3:-10}
      
      if [ -z "$keyword" ]; then
        echo "错误：请提供搜索关键词"
        echo "用法：search-docs.sh --search <关键词> [类型] [数量]"
        exit 1
      fi
      
      case "$type" in
        content|-c)
          search_content "$keyword" "$limit"
          ;;
        filename|-f)
          search_filename "$keyword" "$limit"
          ;;
        title|-t)
          search_title "$keyword" "$limit"
          ;;
        *)
          echo "错误：未知类型 '$type'"
          echo "可用类型：content, filename, title"
          exit 1
          ;;
      esac
      
      log "搜索：$keyword (类型：$type)"
      ;;
    
    --list|-l)
      local dir=$1
      list_directory "$dir"
      ;;
    
    --read|-r)
      local doc=$1
      local lines=${2:-50}
      read_document "$doc" "$lines"
      ;;
    
    --stats)
      show_stats
      ;;
    
    --help|-h)
      echo "用法：search-docs.sh [选项] [参数]"
      echo ""
      echo "选项:"
      echo "  --search, -s <关键词> [类型] [数量]  搜索文档"
      echo "      类型：content(内容), filename(文件名), title(标题)"
      echo "      默认：content, 数量：10"
      echo ""
      echo "  --list, -l <目录>                   列出目录内容"
      echo "  --read, -r <文档> [行数]            阅读文档内容"
      echo "  --stats                             显示文档统计"
      echo "  --help, -h                          显示帮助"
      echo ""
      echo "示例:"
      echo "  search-docs.sh --search binding"
      echo "  search-docs.sh --search agent filename"
      echo "  search-docs.sh --search cron title"
      echo "  search-docs.sh --list concepts"
      echo "  search-docs.sh --read concepts/agent.md"
      echo "  search-docs.sh --stats"
      echo ""
      ;;
    
    *)
      echo "错误：未知选项 '$mode'"
      echo "运行 'search-docs.sh --help' 查看帮助"
      exit 1
      ;;
  esac
}

main "$@"
