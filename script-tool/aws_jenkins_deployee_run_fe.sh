#!/bin/bash
#
# 功能：部署前端Docker容器（用于AWS Jenkins环境）
# 用法：./aws_jenkins_deployee_run_fe.sh [server-port container-port docker-account image version]
# 参数（全部可选，未提供时会交互式询问）：
#   server-port      - 服务器端口，默认：13001
#   container-port   - 容器端口，默认：3000
#   docker-account   - Docker账户名，默认：zhang1career
#   image            - 镜像名称，默认：data-analyzer-fe
#   version          - 镜像版本，默认：latest
# 说明：
#   - 脚本会停止并删除同名旧容器和镜像
#   - 从 /download/ 目录加载tar格式的镜像文件
#   - 容器配置为自动重启（unless-stopped）
#

set -e  # 遇到错误立即退出

echo "🚀 前端Docker容器部署工具"
echo ""

# 参数处理：如果没有提供5个参数，则交互式询问
if [ $# -eq 5 ]; then
	# 使用命令行参数
	SERVER_PORT=$1
	CONTAINER_PORT=$2
	DOCKER_ACCOUNT=$3
	IMAGE=$4
	VERSION=$5
	echo "✅ 使用命令行参数"
else
	# 交互式输入参数
	echo "📝 请提供以下参数（直接回车使用默认值）："
	echo ""
	
	read -rp "服务器端口 (默认: 13001): " SERVER_PORT
	SERVER_PORT="${SERVER_PORT:-13001}"
	
	read -rp "容器端口 (默认: 3000): " CONTAINER_PORT
	CONTAINER_PORT="${CONTAINER_PORT:-3000}"
	
	read -rp "Docker账户名 (默认: zhang1career): " DOCKER_ACCOUNT
	DOCKER_ACCOUNT="${DOCKER_ACCOUNT:-zhang1career}"
	
	read -rp "镜像名称 (默认: data-analyzer-fe): " IMAGE
	IMAGE="${IMAGE:-data-analyzer-fe}"
	
	read -rp "镜像版本 (默认: latest): " VERSION
	VERSION="${VERSION:-latest}"
fi

# 验证端口是否为数字
if ! [[ "$SERVER_PORT" =~ ^[0-9]+$ ]] || [ "$SERVER_PORT" -le 0 ] || [ "$SERVER_PORT" -gt 65535 ]; then
	echo "❌ 错误：服务器端口必须是1-65535之间的数字"
	exit 1
fi

if ! [[ "$CONTAINER_PORT" =~ ^[0-9]+$ ]] || [ "$CONTAINER_PORT" -le 0 ] || [ "$CONTAINER_PORT" -gt 65535 ]; then
	echo "❌ 错误：容器端口必须是1-65535之间的数字"
	exit 1
fi

# 构建变量
DOCKER_REPO="$DOCKER_ACCOUNT/$IMAGE"
CONTAINER_NAME="${IMAGE}_${VERSION}"
IMAGE_FILE="/download/${CONTAINER_NAME}.tar"

echo ""
echo "📋 部署配置："
echo "   服务器端口:     ${SERVER_PORT}"
echo "   容器端口:       ${CONTAINER_PORT}"
echo "   Docker账户:     ${DOCKER_ACCOUNT}"
echo "   镜像名称:       ${IMAGE}"
echo "   镜像版本:       ${VERSION}"
echo "   Docker仓库:     ${DOCKER_REPO}"
echo "   容器名称:       ${CONTAINER_NAME}"
echo "   镜像文件:       ${IMAGE_FILE}"
echo ""

# 检查镜像文件是否存在
if [ ! -f "$IMAGE_FILE" ]; then
	echo "❌ 错误：镜像文件不存在: $IMAGE_FILE"
	exit 1
fi

# 停止并删除旧容器（如果存在）
echo "🛑 正在停止并删除旧容器..."
if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
	echo "   发现旧容器: ${CONTAINER_NAME}"
	docker stop "$CONTAINER_NAME" 2>/dev/null || true
	docker rm "$CONTAINER_NAME" 2>/dev/null || true
	echo "✅ 旧容器已删除"
else
	echo "   ℹ️  未发现旧容器"
fi

# 删除旧镜像（如果存在）
if docker images --format '{{.Repository}}:{{.Tag}}' | grep -q "^${DOCKER_REPO}:${VERSION}$"; then
	echo "   发现旧镜像: ${DOCKER_REPO}:${VERSION}"
	docker image rm "$DOCKER_REPO:$VERSION" 2>/dev/null || true
	echo "✅ 旧镜像已删除"
else
	echo "   ℹ️  未发现旧镜像"
fi

echo ""

# 加载镜像
echo "📦 正在加载镜像..."
if docker load -i "$IMAGE_FILE"; then
	echo "✅ 镜像加载成功"
else
	echo "❌ 镜像加载失败"
	exit 1
fi

echo ""

# 运行容器
echo "🚀 正在启动容器..."
if docker run --restart unless-stopped \
	--name "$CONTAINER_NAME" \
	-p "${SERVER_PORT}:${CONTAINER_PORT}" \
	-d "$DOCKER_REPO:$VERSION"; then
	echo "✅ 容器启动成功"
else
	echo "❌ 容器启动失败"
	exit 1
fi

echo ""
echo "📊 容器状态："
docker ps --filter "name=${CONTAINER_NAME}" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo ""
echo "🎉 部署完成！"
echo "   访问地址: http://localhost:${SERVER_PORT}"
