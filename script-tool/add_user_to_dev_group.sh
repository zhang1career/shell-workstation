#!/bin/bash
#
# 功能：将指定用户添加到dev用户组
# 用法：./add_user_to_dev_group.sh <username>
# 参数：
#   username - 必需，要添加到dev组的用户名
# 说明：
#   - 如果dev组不存在，会自动创建
#   - 需要root权限执行
#   - 用户需要重新登录才能生效
#

set -e  # 遇到错误立即退出

# 检查参数
if [ $# -lt 1 ]; then
	echo "❌ 错误：未指定用户名"
	echo ""
	echo "用法：$0 <username>"
	echo "示例：$0 john"
	exit 1
fi

USER_GROUP="dev"
USER=$1

# 验证用户是否存在
if ! id "$USER" &>/dev/null; then
	echo "❌ 错误：用户 '$USER' 不存在"
	exit 1
fi

echo "ℹ️  目标用户：$USER"
echo "ℹ️  目标组：$USER_GROUP"
echo ""

# 检查组是否存在，不存在则创建
if sudo getent group "$USER_GROUP" &>/dev/null; then
	echo "✅ 组 '$USER_GROUP' 已存在"
else
	echo "📝 组 '$USER_GROUP' 不存在，正在创建..."
	sudo groupadd "$USER_GROUP"
	echo "✅ 组 '$USER_GROUP' 创建成功"
fi

# 检查用户是否已在组中
if id -nG "$USER" | grep -qw "$USER_GROUP"; then
	echo "ℹ️  用户 '$USER' 已在组 '$USER_GROUP' 中"
	echo "✅ 操作完成（无需更改）"
else
	# 将用户添加到组
	echo "🔄 正在将用户 '$USER' 添加到组 '$USER_GROUP'..."
	sudo usermod -a -G "$USER_GROUP" "$USER"
	
	# 验证操作结果
	if id -nG "$USER" | grep -qw "$USER_GROUP"; then
		echo "✅ 用户 '$USER' 已成功添加到组 '$USER_GROUP'"
		echo ""
		echo "📋 用户当前所属组："
		id -nG "$USER" | tr ' ' '\n' | sed 's/^/   - /'
		echo ""
		echo "⚠️  注意：用户需要重新登录才能使组权限生效"
	else
		echo "❌ 错误：添加用户到组失败"
		exit 1
	fi
fi
