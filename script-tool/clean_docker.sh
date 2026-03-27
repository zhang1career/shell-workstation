#!/usr/bin/env bash
#
# 功能：关闭 Docker 进程并清理脏数据
# 用法：./clean_docker.sh [--clean-data] [--force]
# 参数：
#   --clean-data  - 可选，清理 Docker 构建缓存、未使用镜像/容器/卷等脏数据
#   --force, -f   - 可选，跳过交互确认，直接执行
#   -h, --help    - 显示帮助信息
# 说明：
#   - 需 root 权限执行（或 sudo）
#   - 适用于 macOS，会停止 Docker 的 launchctl 服务
#   - 依次：终止 Docker 进程 → 停止系统服务 → 杀残留进程 → 可选清理数据
# 示例：
#   sudo ./clean_docker.sh
#   sudo ./clean_docker.sh --clean-data
#   sudo ./clean_docker.sh --clean-data --force
#

set -e

# ============================================================
# 参数初始化
# ============================================================
CLEAN_DATA=false
FORCE=false

# ============================================================
# 解析命令行参数
# ============================================================
for arg in "$@"; do
  case "$arg" in
    --clean-data)
      CLEAN_DATA=true
      ;;
    --force|-f)
      FORCE=true
      ;;
    -h|--help)
      echo "用法: $0 [--clean-data] [--force]"
      echo ""
      echo "关闭 Docker 进程并可选清理脏数据（构建缓存、未使用镜像/容器/卷等）。"
      echo ""
      echo "参数说明:"
      echo "  --clean-data   清理 Docker 脏数据（未使用镜像、容器、卷、构建缓存）"
      echo "  --force, -f    跳过交互确认，直接执行"
      echo "  -h, --help     显示此帮助信息"
      echo ""
      echo "注意: 需要 root 权限，建议使用 sudo 执行"
      exit 0
      ;;
  esac
done

# ============================================================
# 权限检查
# ============================================================
if [ "$(id -u)" -ne 0 ]; then
  echo "❌ 错误：本脚本需要 root 权限执行"
  echo "请使用: sudo $0 $*"
  exit 1
fi

# ============================================================
# 交互确认
# ============================================================
if [ "$FORCE" != true ]; then
  echo ""
  echo "⚠️  Docker 进程关闭与清理工具"
  echo ""
  echo "将执行以下操作："
  if [ "$CLEAN_DATA" = true ]; then
    echo "  1. 清理 Docker 脏数据（未使用镜像、容器、卷、构建缓存）"
    echo "  2. 终止所有 Docker 相关进程"
    echo "  3. 停止 Docker 系统服务 (launchctl)"
    echo "  4. 清理残留进程"
    echo ""
    echo "⚠️  --clean-data 将删除未使用的镜像/容器/卷，请确认已备份重要数据"
  else
    echo "  1. 终止所有 Docker 相关进程"
    echo "  2. 停止 Docker 系统服务 (launchctl)"
    echo "  3. 清理残留进程"
  fi
  echo ""
  read -p "是否继续? [y/N]: " confirm
  if [[ ! "$confirm" =~ ^[yY]$ ]]; then
    echo "已取消"
    exit 0
  fi
fi

# ============================================================
# 可选步骤 0：清理 Docker 脏数据（需在终止进程之前，Docker 尚在运行）
# ============================================================
if [ "$CLEAN_DATA" = true ] && command -v docker &>/dev/null; then
  echo ""
  echo "📌 步骤 0：清理 Docker 脏数据..."
  if docker system prune -af --volumes 2>/dev/null; then
    echo "   ✓ 已清理未使用镜像、容器、卷和构建缓存"
  else
    echo "   ⚠ Docker 可能未运行或执行失败，跳过数据清理"
  fi
fi

# ============================================================
# 步骤 1：终止所有 Docker 相关进程
# ============================================================
echo ""
echo "📌 步骤 1/3：终止所有 Docker 相关进程..."
if pkill -9 -i docker 2>/dev/null; then
  echo "   ✓ 已发送 SIGKILL 到 docker 进程"
else
  echo "   ○ 未发现运行中的 docker 进程（或已全部退出）"
fi

# ============================================================
# 步骤 2：停止 system 级 Docker 服务 (macOS launchctl)
# ============================================================
echo ""
echo "📌 步骤 2/3：停止 Docker 系统服务..."
for plist in /Library/LaunchDaemons/com.docker.vmnetd.plist /Library/LaunchDaemons/com.docker.socket.plist; do
  if [ -f "$plist" ]; then
    if launchctl bootout system "$plist" 2>/dev/null; then
      echo "   ✓ 已停止: $(basename "$plist")"
    else
      echo "   ○ $(basename "$plist") 已停止或不存在"
    fi
  fi
done

# ============================================================
# 步骤 3：杀掉残留进程
# ============================================================
echo ""
echo "📌 步骤 3/3：清理残留进程..."
# 使用 grep -v grep 排除 grep 自身，避免误杀
pids=$(ps aux | grep -i docker | grep -v grep | awk '{print $2}' 2>/dev/null || true)
if [ -n "$pids" ]; then
  echo "$pids" | xargs kill -9 2>/dev/null || true
  echo "   ✓ 已清理残留进程"
else
  echo "   ○ 无残留进程"
fi

# 再次确认主进程
killall -9 com.docker.docker 2>/dev/null || true

echo ""
echo "✅ Docker 进程关闭与清理完成"
echo ""
