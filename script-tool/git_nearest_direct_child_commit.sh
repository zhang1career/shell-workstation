#!/bin/bash
#
# 功能：在Git历史中查找指定参考提交之后最近的直接子提交
# 用法：./git_nearest_direct_child_commit.sh <reference_commit> <candidate_commit1> [candidate_commit2] ...
# 参数：
#   reference_commit  - 必需，参考提交的hash（完整或部分）
#   candidate_commit - 必需，至少一个候选提交的hash（完整或部分）
# 说明：
#   - 从参考提交开始，沿着HEAD方向查找第一个匹配的候选提交
#   - 支持使用提交hash的前缀（部分hash）
#   - 用于查找特定提交之后的下一个相关提交
#

set -e  # 遇到错误立即退出

# 检查参数数量
if [ "$#" -lt 2 ]; then
    echo "❌ 错误：参数不足"
    echo ""
    echo "用法：$0 <reference_commit> <candidate_commit1> [candidate_commit2] ..."
    echo ""
    echo "参数说明："
    echo "  reference_commit  - 参考提交的hash（完整或部分）"
    echo "  candidate_commit - 候选提交的hash（完整或部分），可提供多个"
    echo ""
    echo "示例："
    echo "  $0 abc123 def456 ghi789"
    echo "  $0 abc123 def456"
    exit 1
fi

# 提取参考提交
REF_COMMIT="$1"
shift  # 移除第一个参数，剩余的都是候选提交

# 验证参考提交是否存在
if ! git rev-parse --verify "$REF_COMMIT" >/dev/null 2>&1; then
    echo "❌ 错误：参考提交 '$REF_COMMIT' 不存在或无效"
    exit 1
fi

# 验证候选提交是否存在
INVALID_CANDIDATES=()
for candidate in "$@"; do
    if ! git rev-parse --verify "$candidate" >/dev/null 2>&1; then
        INVALID_CANDIDATES+=("$candidate")
    fi
done

if [ ${#INVALID_CANDIDATES[@]} -gt 0 ]; then
    echo "❌ 错误：以下候选提交不存在或无效："
    printf "   %s\n" "${INVALID_CANDIDATES[@]}"
    exit 1
fi

echo "🔍 正在查找参考提交 '$REF_COMMIT' 之后最近的候选提交..."
echo "📋 候选提交列表："
for candidate in "$@"; do
    echo "   - $candidate"
done
echo ""

# 从参考提交开始，沿着HEAD方向遍历提交历史
# --reverse: 按时间顺序（从旧到新）
# --ancestry-path: 只显示从REF_COMMIT到HEAD路径上的提交
FOUND=false
for commit in $(git rev-list --reverse --ancestry-path HEAD ^"$REF_COMMIT" 2>/dev/null); do
    # 检查当前提交是否匹配任何一个候选提交
    for candidate in "$@"; do
        # 使用前缀匹配（支持部分hash）
        if echo "$commit" | grep -q "^$candidate"; then
            echo "✅ 找到匹配的提交！"
            echo ""
            echo "   参考提交: $REF_COMMIT"
            echo "   找到的提交: $commit"
            echo "   匹配的候选: $candidate"
            echo ""
            # 显示提交信息
            echo "📝 提交信息："
            git log -1 --format="   %h - %s (%an, %ar)" "$commit"
            exit 0
        fi
    done
done

# 如果没有找到匹配的提交
echo "⚠️  未找到匹配的提交"
echo ""
echo "   参考提交: $REF_COMMIT"
echo "   搜索范围: 从 $REF_COMMIT 到 HEAD 的提交历史"
echo "   候选提交: $*"
echo ""
echo "💡 提示："
echo "   - 确认候选提交是否在参考提交之后"
echo "   - 确认提交hash是否正确"
exit 1

