#!/usr/bin/env bash
#
# 功能：
#   统计当前 Python 环境中已安装 pip 包的磁盘占用大小，
#   按从大到小排序输出，并在执行过程中显示进度条。
#
# 依赖：
#   - pip
#   - du
#   - awk / sort / tr / wc（系统自带）
#
# 原理：
#   1. 通过 `pip list` 获取已安装包列表
#   2. 通过 `pip show <pkg>` 获取包的安装路径（Location）
#   3. 假定包目录位于 site-packages/<package_name>
#   4. 使用 du 统计目录大小（单位 KB）
#   5. 所有结果汇总后再排序并格式化输出
#

set -e
# set -e：脚本中任何命令出错即退出，避免产生不完整结果

# 创建临时文件，用于存放 “size package_name”
TMP_FILE=$(mktemp)

# 获取 pip 包总数，用于计算进度条
TOTAL=$(pip list --format freeze | wc -l)

# 当前已处理的包数量
COUNT=0

echo "Scanning pip packages ($TOTAL total)..."
echo

# 逐个读取 pip 包名
pip list --format freeze | cut -d= -f1 | while read -r P; do
    # 已处理数量 +1
    COUNT=$((COUNT + 1))

    # ======================
    # 进度条计算
    # ======================
    PERCENT=$((COUNT * 100 / TOTAL))   # 百分比
    BAR_WIDTH=40                       # 进度条宽度
    FILLED=$((PERCENT * BAR_WIDTH / 100))
    EMPTY=$((BAR_WIDTH - FILLED))

    # \r：回到行首，实现“原地刷新”
    printf "\r[%s%s] %3d%% (%d/%d) %s" \
        "$(printf '%0.s#' $(seq 1 $FILLED))" \
        "$(printf '%0.s-' $(seq 1 $EMPTY))" \
        "$PERCENT" "$COUNT" "$TOTAL" "$P"

    # ======================
    # 获取包安装路径
    # ======================
    LOCATION=$(pip show "$P" 2>/dev/null | awk '/Location/{print $2}')

    # pip 包目录通常是小写
    PKG_DIR=$(echo "$P" | tr 'A-Z' 'a-z')

    # ======================
    # 统计包大小
    # ======================
    # 仅当目录存在时才统计，避免报错
    if [[ -d "$LOCATION/$PKG_DIR" ]]; then
        # du -s：只输出总大小（单位 KB）
        SIZE=$(du -s "$LOCATION/$PKG_DIR" | awk '{print $1}')

        # 保存为：<size_in_kb> <package_name>
        echo "$SIZE $P" >> "$TMP_FILE"
    fi
done

echo
echo "Sorting results..."
echo

# ======================
# 排序并格式化输出
# ======================
# -nr：按数值倒序排序（从大到小）
sort -nr "$TMP_FILE" | awk '
{
    size=$1
    pkg=$2

    # 按大小自动转换单位
    if (size > 1024*1024)
        printf "%6.1f GB  %s\n", size/1024/1024, pkg
    else if (size > 1024)
        printf "%6.1f MB  %s\n", size/1024, pkg
    else
        printf "%6.1f KB  %s\n", size, pkg
}
'

# 清理临时文件
rm -f "$TMP_FILE"

