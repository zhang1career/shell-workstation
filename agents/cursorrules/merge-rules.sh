#!/usr/bin/env bash
# 将 common 与指定规则文件合并输出，供 Cursor 只配置一个规则文件时使用。
# 用法: ./merge-rules.sh <输入文件名> [输出文件路径]
#   - 第1个参数：输入文件名（必需），在 raw-rules 下查找
#   - 第2个参数：输出文件路径（可选），不传则输出到 output-rules/<输入文件名>
set -e
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMMON="$DIR/common"
OPENSKILLS="$DIR/../openskills/AGENTS.md"
RAW_DIR="$DIR/raw-rules"
OUTPUT_DIR="$DIR/output-rules"

if [[ ! -f "$OPENSKILLS" ]]; then
  echo "错误: 未找到 openskills AGENTS.md: $OPENSKILLS" >&2
  exit 1
fi

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

# 将 common 中的 {{OPENSKILLS}} 替换为 openskills/AGENTS.md 全文（不修改原始 common 模版）
expand_common_with_openskills() {
  perl -0777 -e '
    my ($openskills_path, $common_path) = @ARGV;
    open my $f, "<", $openskills_path or die "$openskills_path: $!\n";
    local $/;
    my $skills = <$f>;
    close $f;
    open $f, "<", $common_path or die "$common_path: $!\n";
    my $out = <$f>;
    close $f;
    my $ph = "{{OPENSKILLS}}";
    my $len = length($ph);
    while ((my $i = index($out, $ph)) >= 0) {
      substr($out, $i, $len) = $skills;
    }
    print $out;
  ' "$OPENSKILLS" "$COMMON"
}

{
  echo "--- common"
  expand_common_with_openskills
  echo ""
  echo "--- $INPUT_FILENAME"
  cat "$INPUT_FILE"
} > "$OUTFILE"

echo "已合并输出到: $OUTFILE"
