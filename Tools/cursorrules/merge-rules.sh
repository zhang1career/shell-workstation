#!/usr/bin/env bash
# 将 common 与指定规则文件合并输出，供 Cursor 只配置一个规则文件时使用。
# 用法: ./merge-rules.sh <输入文件名> [输出文件路径]
#   - 第1个参数：输入文件名（必需），在 raw-rules 下查找
#   - 第2个参数：输出文件路径（可选），不传则输出到 output-rules/<输入文件名>
set -e
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMMON="$DIR/common"
RAW_DIR="$DIR/raw-rules"
OUTPUT_DIR="$DIR/output-rules"

INPUT_FILENAME="$1"
OUTPUT_PATH="$2"

if [[ -z "$INPUT_FILENAME" ]]; then
  echo "用法: $0 <输入文件名> [输出文件路径]" >&2
  echo "  输入文件在 raw-rules 下查找；输出路径不传则写入 output-rules/<输入文件名>" >&2
  echo "例:   $0 fe-rules" >&2
  echo "例:   $0 fe-rules /path/to/merged-rules" >&2
  exit 1
fi

INPUT_FILE="$RAW_DIR/$INPUT_FILENAME"
if [[ ! -f "$INPUT_FILE" ]]; then
  echo "错误: 在 $RAW_DIR 下未找到文件: $INPUT_FILENAME" >&2
  exit 1
fi

if [[ -n "$OUTPUT_PATH" ]]; then
  OUTFILE="$OUTPUT_PATH"
else
  OUTFILE="$OUTPUT_DIR/$INPUT_FILENAME"
fi

{
  echo "--- common"
  cat "$COMMON"
  echo ""
  echo "--- $INPUT_FILENAME"
  cat "$INPUT_FILE"
} > "$OUTFILE"

echo "已合并输出到: $OUTFILE"
