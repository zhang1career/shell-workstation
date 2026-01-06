#!/bin/bash
#
# 功能：从文件中读取键值对并写入Redis缓存
# 用法：./parse_uri_ip_and_write_cache.sh <file_path> <redis_host> <redis_port> <prefix> <ttl>
# 参数：
#   file_path   - 必需，输入文件路径（制表符分隔的键值对）
#   redis_host  - 必需，Redis服务器地址
#   redis_port  - 必需，Redis服务器端口
#   prefix      - 必需，Redis键的前缀
#   ttl         - 必需，键的过期时间（秒）
# 输入格式：
#   键<TAB>值
# 说明：
#   - 从文件中读取制表符分隔的键值对
#   - 将数据写入Redis，键格式为：prefix + key
#   - 所有键都设置相同的TTL（过期时间）
#   - 跳过空键或空值的行
# 示例：
#   ./parse_uri_ip_and_write_cache.sh data.txt localhost 6379 "cache:" 3600
#

set -e  # 遇到错误立即退出

# 检查参数数量
if [ $# -lt 5 ]; then
    echo "❌ 错误：参数不足"
    echo ""
    echo "用法：$0 <file_path> <redis_host> <redis_port> <prefix> <ttl>"
    echo ""
    echo "参数说明："
    echo "  file_path   - 输入文件路径（制表符分隔的键值对）"
    echo "  redis_host  - Redis服务器地址"
    echo "  redis_port  - Redis服务器端口"
    echo "  prefix      - Redis键的前缀"
    echo "  ttl         - 键的过期时间（秒）"
    echo ""
    echo "示例："
    echo "  $0 data.txt localhost 6379 \"cache:\" 3600"
    exit 1
fi

file=$1
redis_host=$2
redis_port=$3
prefix=$4
ttl=$5

# 检查文件是否存在
if [ ! -f "$file" ]; then
    echo "❌ 错误：文件不存在: $file"
    exit 1
fi

# 检查文件是否可读
if [ ! -r "$file" ]; then
    echo "❌ 错误：文件不可读: $file"
    exit 1
fi

# 验证端口是否为数字
if ! [[ "$redis_port" =~ ^[0-9]+$ ]] || [ "$redis_port" -le 0 ] || [ "$redis_port" -gt 65535 ]; then
    echo "❌ 错误：Redis端口必须是1-65535之间的数字"
    exit 1
fi

# 验证TTL是否为数字
if ! [[ "$ttl" =~ ^[0-9]+$ ]] || [ "$ttl" -le 0 ]; then
    echo "❌ 错误：TTL必须是正整数（秒）"
    exit 1
fi

# 检查redis-cli是否可用
if ! command -v redis-cli &> /dev/null; then
    echo "❌ 错误：未找到redis-cli命令，请先安装Redis客户端"
    exit 1
fi

# 测试Redis连接
echo "🔗 正在测试Redis连接..."
if ! redis-cli -h "$redis_host" -p "$redis_port" PING > /dev/null 2>&1; then
    echo "❌ 错误：无法连接到Redis服务器 $redis_host:$redis_port"
    echo "   请检查："
    echo "   - Redis服务器是否运行"
    echo "   - 主机地址和端口是否正确"
    echo "   - 网络连接是否正常"
    exit 1
fi
echo "✅ Redis连接成功"
echo ""

echo "📝 配置信息："
echo "   文件路径:  $file"
echo "   Redis地址: $redis_host:$redis_port"
echo "   键前缀:    $prefix"
echo "   TTL:       ${ttl}秒"
echo ""

# 统计变量
total_lines=0
success_count=0
skip_count=0
error_count=0

# 读取文件并写入Redis
echo "🔄 正在写入数据到Redis..."
while IFS=$'\t' read -r key value || [ -n "$key" ]; do
    total_lines=$((total_lines + 1))
    
    # 跳过空键或空值的行
    if [[ -z "$key" || -z "$value" ]]; then
        skip_count=$((skip_count + 1))
        continue
    fi
    
    # 构建完整的Redis键
    redis_key="${prefix}${key}"
    
    # 写入Redis
    if redis-cli -h "$redis_host" -p "$redis_port" SET "$redis_key" "$value" EX "$ttl" > /dev/null 2>&1; then
        success_count=$((success_count + 1))
    else
        error_count=$((error_count + 1))
        echo "⚠️  警告：写入失败 - 键: $redis_key" >&2
    fi
done < "$file"

echo ""
echo "📊 处理结果："
echo "   总行数:    $total_lines"
echo "   成功:      $success_count"
echo "   跳过:      $skip_count"
echo "   失败:      $error_count"

if [ $error_count -gt 0 ]; then
    echo ""
    echo "⚠️  有部分数据写入失败，请检查Redis连接和权限"
    exit 1
else
    echo ""
    echo "✅ 所有数据已成功写入Redis"
fi
