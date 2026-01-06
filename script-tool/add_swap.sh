#!/bin/bash
#
# 功能：为Linux系统添加或调整swap交换空间
# 用法：./add_swap.sh [swap_size_gb]
# 参数：
#   swap_size_gb - 可选，swap大小（单位：GB），默认为2GB
# 说明：
#   - 此脚本会关闭现有swap，创建新的swap文件，并配置为开机自动挂载
#   - 需要root权限执行
#   - swap文件位置：/swapfile
#

set -e  # 遇到错误立即退出

# 设置swap大小，默认为2GB
if [ $# -lt 1 ]; then
	SWAP_SIZE=2
	echo "ℹ️  未指定swap大小，使用默认值：${SWAP_SIZE}GB"
else
	SWAP_SIZE=$1
	# 验证输入是否为数字
	if ! [[ "$SWAP_SIZE" =~ ^[0-9]+$ ]] || [ "$SWAP_SIZE" -le 0 ]; then
		echo "❌ 错误：swap大小必须是正整数（单位：GB）"
		echo "用法：$0 [swap_size_gb]"
		exit 1
	fi
	echo "ℹ️  设置swap大小为：${SWAP_SIZE}GB"
fi

# 计算swap文件块数：每个块128MB，1GB = 8个块
SWAP_COUNT=$((SWAP_SIZE * 8))
echo "📊 将创建 ${SWAP_COUNT} 个128MB块（总计 ${SWAP_SIZE}GB）"

# 关闭所有swap进程
echo "🔄 正在关闭现有swap..."
if sudo swapoff -a 2>/dev/null; then
	echo "✅ swap已关闭"
else
	echo "⚠️  未检测到活动的swap，继续执行..."
fi

# 检查swap文件是否已存在
if [ -f /swapfile ]; then
	echo "⚠️  检测到已存在的swap文件 /swapfile"
	read -p "是否删除并重新创建？(y/N): " -n 1 -r
	echo
	if [[ $REPLY =~ ^[Yy]$ ]]; then
		sudo rm -f /swapfile
		echo "✅ 已删除旧swap文件"
	else
		echo "❌ 操作已取消"
		exit 1
	fi
fi

# 创建swap文件
echo "📝 正在创建swap文件（这可能需要几分钟）..."
sudo dd if=/dev/zero of=/swapfile bs=128M count=$SWAP_COUNT status=progress
if [ $? -eq 0 ]; then
	echo "✅ swap文件创建成功"
else
	echo "❌ swap文件创建失败"
	exit 1
fi

# 设置文件权限（仅root可读写）
echo "🔒 正在设置文件权限..."
sudo chmod 600 /swapfile
echo "✅ 权限设置完成"

# 格式化为swap分区
echo "🔧 正在格式化swap分区..."
sudo mkswap /swapfile
if [ $? -eq 0 ]; then
	echo "✅ swap分区格式化成功"
else
	echo "❌ swap分区格式化失败"
	exit 1
fi

# 启用swap
echo "🚀 正在启用swap..."
sudo swapon /swapfile
if [ $? -eq 0 ]; then
	echo "✅ swap已启用"
else
	echo "❌ swap启用失败"
	exit 1
fi

# 验证swap状态
echo ""
echo "📊 当前swap状态："
sudo swapon -s
echo ""

# 配置开机自动挂载
if grep -q "/swapfile swap swap defaults 0 0" /etc/fstab 2>/dev/null; then
	echo "ℹ️  /etc/fstab中已存在swap配置，跳过添加"
else
	echo "💾 正在配置开机自动挂载..."
	echo "/swapfile swap swap defaults 0 0" | sudo tee -a /etc/fstab
	echo "✅ 已添加到/etc/fstab"
fi

echo ""
echo "🎉 swap配置完成！"
echo "   大小：${SWAP_SIZE}GB"
echo "   文件：/swapfile"
echo "   状态：已启用并配置为开机自动挂载"

