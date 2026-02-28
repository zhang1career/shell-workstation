#!/usr/bin/env bash
#
# 功能：交互式清理 Git Worktree，逐个询问是否删除
# 用法：./clear-worktree-interactive.sh [--dry-run]
# 参数：
#   --dry-run  - 可选，仅模拟执行，不实际删除（用于预览将要执行的操作）
# 说明：
#   - 脚本会列出当前仓库的所有 worktree，逐个询问是否删除
#   - 删除完成后会自动执行 git worktree prune 清理失效引用
#   - 使用 --dry-run 可安全预览操作，不会实际修改任何内容
# 示例：
#   ./clear-worktree-interactive.sh
#   ./clear-worktree-interactive.sh --dry-run
#
# 注意：
#   - 删除 worktree 会同时删除其工作目录，请确保没有未提交的更改
#   - 主 worktree（bare 仓库的主目录）通常不应被删除
#   - 当前分支和主分支（main/master）会自动跳过，不允许删除
#

set -e  # 遇到错误立即退出

# ============================================================
# 参数初始化
# ============================================================
DRY_RUN=false  # 是否为模拟运行模式

# ============================================================
# 解析命令行参数
# ============================================================
for arg in "$@"; do
  case "$arg" in
    --dry-run)
      DRY_RUN=true
      ;;
    -h|--help)
      echo "用法: $0 [--dry-run]"
      echo ""
      echo "交互式清理 Git Worktree，逐个询问是否删除。"
      echo ""
      echo "参数说明:"
      echo "  --dry-run    模拟运行，仅显示将要执行的操作"
      echo "  -h, --help   显示此帮助信息"
      echo ""
      echo "示例:"
      echo "  $0"
      echo "  $0 --dry-run"
      exit 0
      ;;
  esac
done

# ============================================================
# 环境检查
# ============================================================
# 检查是否在 Git 仓库中
if ! git rev-parse --git-dir > /dev/null 2>&1; then
  echo "❌ 错误：当前目录不是 Git 仓库"
  exit 1
fi

# 获取当前工作目录的绝对路径，用于标记当前所在的 worktree
CURRENT_DIR=$(pwd -P)

# 获取当前分支名称（用于保护当前分支）
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "")

# 定义主分支名称列表（这些分支将被保护，不允许删除）
MAIN_BRANCHES=("main" "master")

# ============================================================
# 显示运行模式提示
# ============================================================
echo ""
echo "🔧 Git Worktree 交互式清理工具"
echo ""

if [ "$DRY_RUN" = true ]; then
  echo "🔍 模拟运行模式（不会实际删除任何内容）"
  echo ""
fi

# ============================================================
# 获取所有 worktree 列表
# ============================================================
# git worktree list --porcelain 输出格式：
#   worktree /path/to/worktree
#   HEAD <commit-hash>
#   branch refs/heads/<branch-name>
#   (空行分隔)
ALL_WORKTREES=$(git worktree list --porcelain | grep "^worktree " | awk '{print $2}')

# 检查是否有 worktree
if [ -z "$ALL_WORKTREES" ]; then
  echo "ℹ️  未找到任何 worktree"
  exit 0
fi

# 统计 worktree 数量
TOTAL_COUNT=$(echo "$ALL_WORKTREES" | wc -l | tr -d ' ')
echo "📋 发现 $TOTAL_COUNT 个 worktree"
echo ""

# 统计变量
DELETED_COUNT=0
SKIPPED_COUNT=0
PROTECTED_COUNT=0
INDEX=0

# ============================================================
# 遍历并处理每个 worktree
# ============================================================
for WT in $ALL_WORKTREES; do
  ((INDEX++)) || true

  # 将 worktree 路径转换为绝对路径
  WT_REAL=$(realpath "$WT" 2>/dev/null || echo "$WT")

  # 获取该 worktree 的分支信息（格式如 [branch-name]）
  BRANCH_INFO=$(git worktree list | grep "^$WT " | awk '{print $3}' || echo "")

  # 提取纯分支名（去掉方括号）
  BRANCH_NAME=$(echo "$BRANCH_INFO" | tr -d '[]')

  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo "[$INDEX/$TOTAL_COUNT] 📁 $WT_REAL"

  # 显示分支信息
  if [ -n "$BRANCH_INFO" ]; then
    echo "        🌿 $BRANCH_INFO"
  fi

  # ============================================================
  # 保护逻辑：检查是否为受保护的分支
  # ============================================================

  # 检查是否为当前分支
  if [ -n "$BRANCH_NAME" ] && [ "$BRANCH_NAME" = "$CURRENT_BRANCH" ]; then
    echo "        🔒 当前分支，已保护（自动跳过）"
    ((PROTECTED_COUNT++)) || true
    continue
  fi

  # 检查是否为主分支
  IS_MAIN_BRANCH=false
  for MAIN in "${MAIN_BRANCHES[@]}"; do
    if [ "$BRANCH_NAME" = "$MAIN" ]; then
      IS_MAIN_BRANCH=true
      break
    fi
  done

  if [ "$IS_MAIN_BRANCH" = true ]; then
    echo "        🔒 主分支，已保护（自动跳过）"
    ((PROTECTED_COUNT++)) || true
    continue
  fi

  # 检查是否为当前工作目录
  IS_CURRENT=false
  if [ "$WT_REAL" = "$CURRENT_DIR" ] || [[ "$CURRENT_DIR" == "$WT_REAL"* ]]; then
    IS_CURRENT=true
    echo "        ⚠️  这是当前工作目录所在的 worktree"
  fi

  # 交互式询问用户
  if [ "$IS_CURRENT" = true ]; then
    read -p "        是否删除此 worktree? (当前目录，谨慎!) [y/N]: " ANSWER
  else
    read -p "        是否删除此 worktree? [y/N]: " ANSWER
  fi

  # 处理用户响应
  if [[ "$ANSWER" =~ ^[Yy]$ ]]; then
    if [ "$DRY_RUN" = true ]; then
      echo "        🔸 (模拟) 将删除: $WT_REAL"
    else
      echo "        🗑️  正在删除..."
      if git worktree remove --force "$WT_REAL" 2>/dev/null; then
        echo "        ✅ 已删除"
      else
        echo "        ❌ 删除失败（可能是主 worktree 或有未提交更改）"
        ((SKIPPED_COUNT++)) || true
        continue
      fi
    fi
    ((DELETED_COUNT++)) || true
  else
    echo "        ⏭️  已跳过"
    ((SKIPPED_COUNT++)) || true
  fi
done

# ============================================================
# 清理失效的 worktree 引用
# ============================================================
if [ "$DRY_RUN" = false ] && [ "$DELETED_COUNT" -gt 0 ]; then
  echo ""
  echo "🧹 正在清理失效的 worktree 引用..."
  git worktree prune
fi

# ============================================================
# 显示操作摘要
# ============================================================
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ "$DRY_RUN" = true ]; then
  echo "📊 模拟运行完成"
  echo "   将删除: $DELETED_COUNT 个 worktree"
  echo "   已保护: $PROTECTED_COUNT 个 worktree"
  echo "   已跳过: $SKIPPED_COUNT 个 worktree"
else
  echo "✅ 操作完成"
  echo "   已删除: $DELETED_COUNT 个 worktree"
  echo "   已保护: $PROTECTED_COUNT 个 worktree"
  echo "   已跳过: $SKIPPED_COUNT 个 worktree"
fi
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
