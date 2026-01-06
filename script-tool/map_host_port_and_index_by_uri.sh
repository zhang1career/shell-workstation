#!/bin/bash
#
# 功能：将IP:服务列表格式的数据转换为应用:IP:端口列表格式
# 用法：./map_host_port_and_index_by_uri.sh <input_file>
# 参数：
#   input_file - 必需，输入文件路径（制表符分隔格式）
# 输入格式：
#   IP地址<TAB>应用1:端口1,应用2:端口2,...
# 输出格式：
#   应用名<TAB>IP1:端口1,IP2:端口2,...
# 说明：
#   - 将按IP组织的服务列表重组为按应用组织的IP:端口列表
#   - 用于服务发现和负载均衡配置
# 示例：
#   输入：192.168.1.1<TAB>web:80,db:3306
#   输出：web<TAB>192.168.1.1:80
#        db<TAB>192.168.1.1:3306
#

set -e  # 遇到错误立即退出

# 检查参数
if [ $# -lt 1 ]; then
	echo "❌ 错误：未指定输入文件"
	echo ""
	echo "用法：$0 <input_file>"
	echo ""
	echo "输入格式："
	echo "  IP地址<TAB>应用1:端口1,应用2:端口2,..."
	echo ""
	echo "示例："
	echo "  192.168.1.1<TAB>web:80,db:3306"
	echo "  192.168.1.2<TAB>web:80"
	echo ""
	echo "输出格式："
	echo "  应用名<TAB>IP1:端口1,IP2:端口2,..."
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
echo "ℹ️  转换格式: IP:服务列表 -> 应用:IP:端口列表" >&2
echo "" >&2

# 使用awk处理数据
# -F '\t' 指定制表符为字段分隔符
awk -F '\t' '
{
	# $1: IP地址
	# $2: 服务列表（格式：应用1:端口1,应用2:端口2,...）
	ip = $1;
	
	# 以逗号分割服务列表
	split($2, services, ",");
	
	# 遍历每个服务
	for (i in services) {
		# 以冒号分割应用名和端口
		split(services[i], app_port, ":");
		app = app_port[1];
		port = app_port[2];
		
		# 将IP:端口添加到对应应用的映射中
		if (app_map[app] == "") {
			# 第一个IP:端口对
			app_map[app] = ip ":" port;
		} else {
			# 追加到现有列表
			app_map[app] = app_map[app] "," ip ":" port;
		}
	}
}
END {
	# 输出结果：按应用名排序
	for (app in app_map) {
		print app "\t" app_map[app];
	}
}
' "$INPUT_FILE"
