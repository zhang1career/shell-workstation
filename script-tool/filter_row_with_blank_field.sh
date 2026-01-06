#!/bin/bash
#
# 功能：过滤掉包含空白字段的数据行（制表符分隔）
# 用法：./filter_row_with_blank_field.sh <input_file>
# 参数：
#   input_file - 必需，输入文件路径（制表符分隔格式）
# 说明：
#   - 过滤掉第2列为"None"或空字符串的行
#   - 保留第2列有有效值的行
#   - 输出到标准输出
#

set -e  # 遇到错误立即退出

# 检查参数
if [ $# -lt 1 ]; then
	echo "❌ 错误：未指定输入文件"
	echo ""
	echo "用法：$0 <input_file>"
	echo "示例：$0 data.txt"
	exit 1
fi

INPUT_FILE=$1

# 检查文件是否存在
if [ ! -f "$INPUT_FILE" ]; then
	echo "❌ 错误：文件不存在: $INPUT_FILE"
	exit 1
fi

# 检查文件是否可读
if [ ! -r "$INPUT_FILE" ]; then
	echo "❌ 错误：文件不可读: $INPUT_FILE"
	exit 1
fi

echo "ℹ️  正在处理文件: $INPUT_FILE" >&2
echo "ℹ️  过滤规则: 保留第2列不为'None'且不为空的行" >&2
echo "" >&2

# 使用awk过滤数据
# -F '\t' 指定制表符为字段分隔符
awk -F '\t' '{
    # 如果第2列不是"None"且不为空，则输出该行
    if ($2 != "None" && $2 != "") {
        print $0
    }
}' "$INPUT_FILE"
