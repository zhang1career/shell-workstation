#!/bin/bash

# =============================================================================
# gen_patch.sh - Git 差异补丁生成工具
# =============================================================================
#
# 功能：将指定 Git 仓库中相对于 HEAD 的所有修改（未暂存 + 已暂存）导出为 patch 文件
#
# 用法：./gen_patch.sh <target_dir> <output_patch_file>
#
# 参数：
#   target_dir     - 必需，目标 Git 仓库的目录路径
#   output_patch_file - 必需，输出的 patch 文件路径（如 my_changes.patch）
#
# 说明：
#   - 生成的 patch 包含工作区与暂存区相对于 HEAD 的所有修改
#   - 可用于备份修改、跨仓库迁移代码、代码审查等场景
#   - 应用时使用：git apply <patch_file> 或 git am <patch_file>
#
# 示例：
#   ./gen_patch.sh /path/to/my_project ./my_changes.patch
#   ./gen_patch.sh . ../backup.patch
#
# =============================================================================

set -e

TARGET_DIR="$1"
OUTPUT_FILE="$2"

# 检查必需参数
if [ -z "$TARGET_DIR" ] || [ -z "$OUTPUT_FILE" ]; then
  echo "用法: $0 <target_dir> <output_patch_file>"
  echo ""
  echo "参数说明："
  echo "  target_dir        - 目标 Git 仓库目录"
  echo "  output_patch_file - 输出的 patch 文件路径"
  echo ""
  echo "示例："
  echo "  $0 /path/to/project changes.patch"
  exit 1
fi

# 检查目标目录是否存在
if [ ! -d "$TARGET_DIR" ]; then
  echo "错误：目标目录不存在: $TARGET_DIR"
  exit 1
fi

cd "$TARGET_DIR"

# 确保目标目录是 Git 仓库
if ! git rev-parse --is-inside-work-tree > /dev/null 2>&1; then
  echo "错误：目标目录不是 Git 仓库: $TARGET_DIR"
  exit 1
fi

# 生成 patch（包含未暂存 + 已暂存的所有修改）
git diff HEAD > "$OUTPUT_FILE"

echo "✓ 补丁已生成: $OUTPUT_FILE"
echo ""
echo "应用补丁示例："
echo "  cd <目标项目目录>"
echo "  git apply $OUTPUT_FILE"
echo ""
echo "提示：若补丁应用失败，可尝试 git apply --3way $OUTPUT_FILE 进行三方合并"
