#!/bin/bash
# ~/.openclaw/scripts/gateway-watchdog.sh
# OpenClaw 网关进程保活脚本

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OPENCLAW_HOME="${OPENCLAW_HOME:-$HOME/.openclaw}"
LOG_DIR="$OPENCLAW_HOME/logs"
LOG_FILE="$LOG_DIR/watchdog.log"
LOCK_FILE="$LOG_DIR/watchdog.lock"
GATEWAY_PORT="${OPENCLAW_GATEWAY_PORT:-18789}"
CHECK_INTERVAL="${CHECK_INTERVAL:-60}"
MAX_RETRIES=3
RETRY_COOLDOWN=60

mkdir -p "$LOG_DIR"

# 加载核心函数
source "$SCRIPT_DIR/core.sh"

# ==================== 锁文件机制 ====================
acquire_lock() {
    if [ -f "$LOCK_FILE" ]; then
        local lock_pid
        lock_pid=$(cat "$LOCK_FILE" 2>/dev/null)
        if [ -n "$lock_pid" ] && kill -0 "$lock_pid" 2>/dev/null; then
            log_error "另一个实例正在运行 (PID: $lock_pid)，退出"
            exit 0
        else
            log_warn "发现过期锁文件，清理中..."
            rm -f "$LOCK_FILE"
        fi
    fi
    echo $$ > "$LOCK_FILE"
}

release_lock() {
    if [ -f "$LOCK_FILE" ]; then
        local lock_pid
        lock_pid=$(cat "$LOCK_FILE" 2>/dev/null)
        if [ "$lock_pid" = "$$" ]; then
            rm -f "$LOCK_FILE"
        fi
    fi
}

trap release_lock EXIT

# ==================== 网关状态检查 ====================
check_gateway() {
    # 检查端口
    if command -v lsof >/dev/null 2>&1; then
        if lsof -i :$GATEWAY_PORT -sTCP:LISTEN >/dev/null 2>&1; then
            return 0
        fi
    elif command -v netstat >/dev/null 2>&1; then
        if netstat -tlnp 2>/dev/null | grep -q ":$GATEWAY_PORT "; then
            return 0
        fi
    elif command -v ss >/dev/null 2>&1; then
        if ss -tlnp 2>/dev/null | grep -q ":$GATEWAY_PORT "; then
            return 0
        fi
    fi
    
    # 使用 openclaw gateway status 检查（兜底方案）
    if command -v openclaw >/dev/null 2>&1; then
        if openclaw gateway status 2>/dev/null | grep -qi "running\|started"; then
            log_info "openclaw gateway status 命令确认运行中"
            return 0
        fi
    fi

    # 所有检查都失败
    return 1
}

# ==================== 配置验证与修复 ====================
validate_and_fix_config() {
    log_info "验证配置..."
    
    # 验证配置
    if validate_config; then
        log_info "配置验证通过"
        return 0
    fi
    
    log_warn "配置验证失败，尝试修复..."
    
    # 尝试 openclaw doctor 自动修复
    if command -v openclaw >/dev/null 2>&1; then
        if openclaw doctor --non-interactive --fix 2>&1 | tee -a "$LOG_FILE"; then
            log_info "自动修复成功"
            sleep 5
            if validate_config; then
                return 0
            fi
        fi
    fi
    
    log_error "配置修复失败，需要手动处理或回滚"
    return 1
}

# ==================== 清理端口（防止端口冲突） ====================
cleanup_gateway_port() {
    local port="${GATEWAY_PORT:-18789}"
    local pids=""

    # 查找占用端口的进程
    if command -v lsof >/dev/null 2>&1; then
        pids=$(lsof -ti:"$port" 2>/dev/null || true)
    fi

    if [ -n "$pids" ]; then
        log_warn "端口 $port 被占用 (PID: $pids)，清理中..."
        for pid in $pids; do
            kill "$pid" 2>/dev/null || true
        done
        # 等待 5 秒，给进程足够的优雅退出时间
        sleep 5
        # 强制清理残留
        for pid in $pids; do
            kill -9 "$pid" 2>/dev/null || true
        done
        sleep 1
        log_info "端口清理完成"
    fi

    # 清理过期锁文件
    rm -f /tmp/openclaw-gateway.lock 2>/dev/null || true
}

# ==================== 重启网关 ====================
restart_gateway() {
    log_info "尝试重启网关..."

    # 步骤 1: 先用官方 stop 优雅关闭
    if command -v openclaw >/dev/null 2>&1; then
        openclaw gateway stop 2>/dev/null || true
        sleep 5
    fi

    # 步骤 2: 清理端口（兜底处理残留进程）
    cleanup_gateway_port

    # 检测平台并使用正确的重启方式
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS 使用 launchctl
        local plist="$HOME/Library/LaunchAgents/ai.openclaw.gateway.plist"
        if [ -f "$plist" ]; then
            launchctl unload "$plist" 2>/dev/null || true
            sleep 1
            launchctl load "$plist" 2>/dev/null || true
            launchctl kickstart -k "ai.openclaw.gateway" 2>/dev/null || true
        fi
    elif command -v systemctl >/dev/null 2>&1; then
        # Linux 使用 systemd
        systemctl --user restart openclaw-gateway 2>/dev/null || \
        systemctl restart openclaw-gateway 2>/dev/null || true
    fi

    # 备用: 直接启动
    if command -v openclaw >/dev/null 2>&1; then
        openclaw gateway start 2>/dev/null || true
    fi

    sleep 15

    if check_gateway; then
        log_info "网关重启成功"
        return 0
    else
        log_error "网关重启失败"
        return 1
    fi
}

# ==================== 读取重启计数 ====================
get_restart_count() {
    local count_file="$LOG_DIR/restart_count"
    if [ -f "$count_file" ]; then
        cat "$count_file" 2>/dev/null || echo "0"
    else
        echo "0"
    fi
}

save_restart_count() {
    local count="$1"
    echo "$count" > "$LOG_DIR/restart_count"
}

# ==================== 记录最后重启时间 ====================
get_last_restart_time() {
    local time_file="$LOG_DIR/last_restart_time"
    if [ -f "$time_file" ]; then
        cat "$time_file" 2>/dev/null || echo "0"
    else
        echo "0"
    fi
}

save_last_restart_time() {
    echo "$(date +%s)" > "$LOG_DIR/last_restart_time"
}

# ==================== 主函数 ====================
main() {
    acquire_lock
    
    load_notify_config
    
    log_info "========== Watchdog 检查开始 =========="
    
    local current_time
    current_time=$(date +%s)
    local last_restart_time
    last_restart_time=$(get_last_restart_time)
    local time_since_restart=$((current_time - last_restart_time))
    
    local restart_count
    restart_count=$(get_restart_count)
    
    # 检查网关状态
    if check_gateway; then
        log_info "网关运行正常"
        # 重置计数
        save_restart_count 0
        save_last_restart_time "$current_time"
        exit 0
    fi
    
    log_warn "网关异常，准备修复..."
    
    # 冷却期检查
    if [ "$time_since_restart" -lt "$RETRY_COOLDOWN" ]; then
        log_warn "冷却期内 (${time_since_restart}/${RETRY_COOLDOWN}秒)，跳过重启"
        exit 0
    fi
    
    # 检查重启次数
    if [ "$restart_count" -ge "$MAX_RETRIES" ]; then
        log_error "连续重启次数达到上限 ($MAX_RETRIES)，触发告警"
        
        # 发送告警
        notify "ERROR" "Gateway 连续重启 $restart_count 次失败，需要人工干预!"
        
        # 触发应急脚本（如果存在）
        if [ -x "$SCRIPT_DIR/config-rollback.sh" ]; then
            log_warn "触发配置回滚..."
            bash "$SCRIPT_DIR/config-rollback.sh"
        fi
        
        exit 1
    fi
    
    # 验证配置
    if ! validate_and_fix_config; then
        log_error "配置验证/修复失败"
        ((restart_count++))
        save_restart_count "$restart_count"
        save_last_restart_time "$current_time"
        
        notify "WARNING" "配置验证失败，重启次数: $restart_count/$MAX_RETRIES"
        
        exit 1
    fi
    
    # 尝试重启
    if restart_gateway; then
        log_info "重启成功"
        save_restart_count 0
        save_last_restart_time "$current_time"
        
        # 重启后恢复检查
        if [ -x "$SCRIPT_DIR/safe-config-modify.sh" ]; then
            log_info "执行重启后恢复检查..."
            bash "$SCRIPT_DIR/safe-config-modify.sh" recovery 2>&1 | tee -a "$LOG_FILE" || true
        else
            notify "INFO" "Gateway 已恢复正常运行"
        fi
    else
        log_error "重启失败"
        ((restart_count++))
        save_restart_count "$restart_count"
        save_last_restart_time "$current_time"
        
        notify "WARNING" "Gateway 重启失败，次数: $restart_count/$MAX_RETRIES"
        
        exit 1
    fi
    
    log_info "========== Watchdog 检查结束 =========="
}

# 支持单次运行或守护进程模式
if [ "${1:-}" = "--daemon" ]; then
    while true; do
        main
        sleep "$CHECK_INTERVAL"
    done
else
    main "$@"
fi
