#!/bin/bash
#
# 功能：刷新API网关的访问令牌
# 用法：./refresh_api_gateway_token.sh <app> <redis_host> <redis_port>
# 参数：
#   app         - 必需，应用名称（用于构建Redis键）
#   redis_host  - 必需，Redis服务器地址
#   redis_port  - 必需，Redis服务器端口
# 说明：
#   - 从Redis读取refresh token和API网关地址
#   - 调用API网关的刷新接口获取新token
#   - 将新token和refresh token保存回Redis，TTL为30天
#   - 需要jq命令来解析JSON响应
# 依赖：
#   - redis-cli
#   - curl
#   - jq
# 示例：
#   ./refresh_api_gateway_token.sh myapp localhost 6379
#

set -e  # 遇到错误立即退出

# 检查参数数量
if [ "$#" -ne 3 ]; then
  echo "❌ 错误：参数数量不正确"
  echo ""
  echo "用法：$0 <app> <redis_host> <redis_port>"
  echo ""
  echo "参数说明："
  echo "  app         - 应用名称（用于构建Redis键）"
  echo "  redis_host  - Redis服务器地址"
  echo "  redis_port  - Redis服务器端口"
  echo ""
  echo "示例："
  echo "  $0 myapp localhost 6379"
  exit 1
fi

# 参数赋值
APP="$1"
REDIS_HOST="$2"
REDIS_PORT="$3"
TOKEN_KEY="${APP}:apigw:token"
REFRESH_KEY="${APP}:apigw:refresh"

# 验证端口是否为数字
if ! [[ "$REDIS_PORT" =~ ^[0-9]+$ ]] || [ "$REDIS_PORT" -le 0 ] || [ "$REDIS_PORT" -gt 65535 ]; then
  echo "❌ 错误：Redis端口必须是1-65535之间的数字"
  exit 1
fi

# 检查必要命令是否存在
for cmd in redis-cli curl jq; do
  if ! command -v "$cmd" &> /dev/null; then
    echo "❌ 错误：未找到命令 '$cmd'，请先安装"
    exit 1
  fi
done

echo "🔄 API网关令牌刷新工具"
echo ""
echo "📋 配置信息："
echo "   应用名称:  $APP"
echo "   Redis地址: $REDIS_HOST:$REDIS_PORT"
echo "   Token键:   $TOKEN_KEY"
echo "   Refresh键: $REFRESH_KEY"
echo ""

# 测试Redis连接
echo "🔗 正在测试Redis连接..."
if ! redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" PING > /dev/null 2>&1; then
  echo "❌ 错误：无法连接到Redis服务器 $REDIS_HOST:$REDIS_PORT"
  exit 1
fi
echo "✅ Redis连接成功"
echo ""

# 从Redis获取API网关基础URL
echo "📥 正在从Redis获取API网关地址..."
API_GATEWAY_BASE=$(redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" GET "reg:serv:api-gateway" 2>/dev/null)
if [ -z "$API_GATEWAY_BASE" ]; then
  echo "❌ 错误：无法从Redis获取 'reg:serv:api-gateway'"
  echo "   请确认该键存在于Redis中"
  exit 1
fi
echo "✅ API网关地址: $API_GATEWAY_BASE"

# 构建完整的API URL
API_GATEWAY_URL="${API_GATEWAY_BASE}/consumer/login"
echo "   完整URL: $API_GATEWAY_URL"
echo ""

# 从Redis获取refresh token
echo "📥 正在从Redis获取refresh token..."
REFRESH_TOKEN=$(redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" GET "$REFRESH_KEY" 2>/dev/null)
if [ -z "$REFRESH_TOKEN" ]; then
  echo "❌ 错误：无法从Redis获取refresh token"
  echo "   Redis键: $REFRESH_KEY"
  echo "   请确认该键存在于Redis中"
  exit 1
fi
echo "✅ Refresh token获取成功"
echo ""

# 调用API刷新token
echo "🌐 正在调用API网关刷新接口..."
RESPONSE=$(curl -s -w "\n%{http_code}" -X PUT "$API_GATEWAY_URL" \
  -H "Content-Type: application/json" \
  -d "{\"refresh_token\": \"$REFRESH_TOKEN\"}" 2>/dev/null)

# 分离HTTP状态码和响应体
HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
RESPONSE_BODY=$(echo "$RESPONSE" | sed '$d')

if [ "$HTTP_CODE" != "200" ]; then
  echo "❌ 错误：API请求失败"
  echo "   HTTP状态码: $HTTP_CODE"
  echo "   响应内容: $RESPONSE_BODY"
  exit 1
fi

# 解析JSON响应
NEW_TOKEN=$(echo "$RESPONSE_BODY" | jq -r '.token' 2>/dev/null)
NEW_REFRESH_TOKEN=$(echo "$RESPONSE_BODY" | jq -r '.refresh_token' 2>/dev/null)

# 验证响应数据
if [ "$NEW_TOKEN" == "null" ] || [ -z "$NEW_TOKEN" ] || \
   [ "$NEW_REFRESH_TOKEN" == "null" ] || [ -z "$NEW_REFRESH_TOKEN" ]; then
  echo "❌ 错误：API响应无效"
  echo "   响应内容: $RESPONSE_BODY"
  exit 1
fi

echo "✅ Token刷新成功"
echo ""

# 保存新token到Redis
TTL_SECONDS=2592000  # 30天（秒）
echo "💾 正在保存新token到Redis（TTL: ${TTL_SECONDS}秒 = 30天）..."

if redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" SET "$TOKEN_KEY" "$NEW_TOKEN" EX $TTL_SECONDS > /dev/null 2>&1; then
  echo "✅ Token已保存: $TOKEN_KEY"
else
  echo "❌ 错误：保存token失败"
  exit 1
fi

if redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" SET "$REFRESH_KEY" "$NEW_REFRESH_TOKEN" EX $TTL_SECONDS > /dev/null 2>&1; then
  echo "✅ Refresh token已保存: $REFRESH_KEY"
else
  echo "❌ 错误：保存refresh token失败"
  exit 1
fi

echo ""
echo "🎉 完成！应用 '$APP' 的token已成功刷新"
