#!/bin/bash
#
# 功能：创建并配置shell运行目录（用于AWS EC2环境）
# 用法：./startup.sh
# 说明：
#   - 创建 /run/shell 目录
#   - 将目录所有权设置为 ec2-user:ec2-user
#   - 通常用于系统启动时的初始化脚本
# 注意：
#   - 需要root权限执行
#   - 适用于AWS EC2 Linux环境
#

set -e  # 遇到错误立即退出

echo "🚀 系统启动初始化脚本"
echo ""

# 检查是否以root权限运行
if [ "$EUID" -ne 0 ]; then
    echo "❌ 错误：此脚本需要root权限执行"
    echo "   请使用: sudo $0"
    exit 1
fi

SHELL_DIR="/run/shell"
USER="ec2-user"
GROUP="ec2-user"

echo "📝 配置信息："
echo "   目录路径: $SHELL_DIR"
echo "   所有者:   $USER:$GROUP"
echo ""

# 创建目录（如果不存在）
if [ ! -d "$SHELL_DIR" ]; then
    echo "📁 正在创建目录: $SHELL_DIR"
    mkdir -p "$SHELL_DIR"
    echo "✅ 目录创建成功"
else
    echo "ℹ️  目录已存在: $SHELL_DIR"
fi

# 设置目录所有权
echo "🔒 正在设置目录所有权..."
if chown "$USER:$GROUP" -R "$SHELL_DIR" 2>/dev/null; then
    echo "✅ 所有权设置成功"
else
    echo "⚠️  警告：设置所有权失败，请检查用户 '$USER' 和组 '$GROUP' 是否存在"
    exit 1
fi

# 验证设置
ACTUAL_OWNER=$(stat -c "%U:%G" "$SHELL_DIR" 2>/dev/null || stat -f "%Su:%Sg" "$SHELL_DIR" 2>/dev/null)
echo ""
echo "📊 验证结果："
echo "   目录: $SHELL_DIR"
echo "   所有者: $ACTUAL_OWNER"

if [ "$ACTUAL_OWNER" = "$USER:$GROUP" ]; then
    echo ""
    echo "✅ 初始化完成"
else
    echo ""
    echo "⚠️  警告：所有权设置可能未完全生效"
    exit 1
fi
