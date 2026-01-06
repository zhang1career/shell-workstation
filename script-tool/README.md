# 脚本工具集目录

本目录包含一系列实用的脚本工具，涵盖系统管理、开发工具、数据处理、音视频处理等功能。

## 📋 目录

- [系统管理脚本](#系统管理脚本)
- [开发工具脚本](#开发工具脚本)
- [数据处理脚本](#数据处理脚本)
- [音视频处理脚本](#音视频处理脚本)
- [网络服务脚本](#网络服务脚本)
- [依赖要求](#依赖要求)

---

## 系统管理脚本

### 1. `add_swap.sh` - 添加/调整Swap交换空间

**功能**：为Linux系统添加或调整swap交换空间

**用法**：
```bash
./add_swap.sh [swap_size_gb]
```

**参数**：
- `swap_size_gb` - 可选，swap大小（单位：GB），默认为2GB

**说明**：
- 需要root权限执行
- 会关闭现有swap，创建新的swap文件，并配置为开机自动挂载
- swap文件位置：`/swapfile`

**示例**：
```bash
sudo ./add_swap.sh          # 使用默认2GB
sudo ./add_swap.sh 4        # 创建4GB swap
```

---

### 2. `add_user_to_dev_group.sh` - 添加用户到dev组

**功能**：将指定用户添加到dev用户组

**用法**：
```bash
./add_user_to_dev_group.sh <username>
```

**参数**：
- `username` - 必需，要添加到dev组的用户名

**说明**：
- 需要root权限执行
- 如果dev组不存在，会自动创建
- 用户需要重新登录才能使组权限生效

**示例**：
```bash
sudo ./add_user_to_dev_group.sh john
```

---

### 3. `startup.sh` - 系统启动初始化脚本

**功能**：创建并配置shell运行目录（用于AWS EC2环境）

**用法**：
```bash
sudo ./startup.sh
```

**说明**：
- 需要root权限执行
- 创建 `/run/shell` 目录
- 将目录所有权设置为 `ec2-user:ec2-user`
- 适用于AWS EC2 Linux环境

---

## 开发工具脚本

### 4. `aws_jenkins_deployee_run_fe.sh` - 部署前端Docker容器

**功能**：部署前端Docker容器（用于AWS Jenkins环境）

**用法**：
```bash
./aws_jenkins_deployee_run_fe.sh [server-port container-port docker-account image version]
```

**参数**（全部可选，未提供时会交互式询问）：
- `server-port` - 服务器端口，默认：13001
- `container-port` - 容器端口，默认：3000
- `docker-account` - Docker账户名，默认：zhang1career
- `image` - 镜像名称，默认：data-analyzer-fe
- `version` - 镜像版本，默认：latest

**说明**：
- 会停止并删除同名旧容器和镜像
- 从 `/download/` 目录加载tar格式的镜像文件
- 容器配置为自动重启（unless-stopped）

**示例**：
```bash
./aws_jenkins_deployee_run_fe.sh
./aws_jenkins_deployee_run_fe.sh 13001 3000 zhang1career data-analyzer-fe latest
```

---

### 5. `git_nearest_direct_child_commit.sh` - 查找最近的直接子提交

**功能**：在Git历史中查找指定参考提交之后最近的直接子提交

**用法**：
```bash
./git_nearest_direct_child_commit.sh <reference_commit> <candidate_commit1> [candidate_commit2] ...
```

**参数**：
- `reference_commit` - 必需，参考提交的hash（完整或部分）
- `candidate_commit` - 必需，至少一个候选提交的hash（完整或部分）

**说明**：
- 从参考提交开始，沿着HEAD方向查找第一个匹配的候选提交
- 支持使用提交hash的前缀（部分hash）

**示例**：
```bash
./git_nearest_direct_child_commit.sh abc123 def456 ghi789
```

---

### 6. `git_user_stats.sh` - Git用户统计

**功能**：显示Git仓库中用户的统计信息

**用法**：
```bash
./git_user_stats.sh [git_log_options]
```

**参数**：
- `git_log_options` - 可选，传递给git log的选项

**说明**：
- 统计每个用户的提交数、修改文件数、新增行数、删除行数和总修改行数
- 按总修改行数降序排列
- 支持使用git log的所有选项来过滤提交范围

**示例**：
```bash
./git_user_stats.sh
./git_user_stats.sh --since="2024-01-01"
./git_user_stats.sh --author="john@example.com"
./git_user_stats.sh --since="2024-01-01" --until="2024-12-31"
```

---

## 数据处理脚本

### 7. `filter_row_with_blank_field.sh` - 过滤空白字段行

**功能**：过滤掉包含空白字段的数据行（制表符分隔）

**用法**：
```bash
./filter_row_with_blank_field.sh <input_file>
```

**参数**：
- `input_file` - 必需，输入文件路径（制表符分隔格式）

**说明**：
- 过滤掉第2列为"None"或空字符串的行
- 保留第2列有有效值的行
- 输出到标准输出

**示例**：
```bash
./filter_row_with_blank_field.sh data.txt > filtered_data.txt
```

---

### 8. `map_host_port_and_index_by_uri.sh` - 服务映射转换

**功能**：将IP:服务列表格式的数据转换为应用:IP:端口列表格式

**用法**：
```bash
./map_host_port_and_index_by_uri.sh <input_file>
```

**参数**：
- `input_file` - 必需，输入文件路径（制表符分隔格式）

**输入格式**：
```
IP地址<TAB>应用1:端口1,应用2:端口2,...
```

**输出格式**：
```
应用名<TAB>IP1:端口1,IP2:端口2,...
```

**示例**：
```bash
# 输入：192.168.1.1<TAB>web:80,db:3306
# 输出：
# web<TAB>192.168.1.1:80
# db<TAB>192.168.1.1:3306
./map_host_port_and_index_by_uri.sh services.txt
```

---

### 9. `parse_uri_ip_and_write_cache.sh` - 写入Redis缓存

**功能**：从文件中读取键值对并写入Redis缓存

**用法**：
```bash
./parse_uri_ip_and_write_cache.sh <file_path> <redis_host> <redis_port> <prefix> <ttl>
```

**参数**：
- `file_path` - 必需，输入文件路径（制表符分隔的键值对）
- `redis_host` - 必需，Redis服务器地址
- `redis_port` - 必需，Redis服务器端口
- `prefix` - 必需，Redis键的前缀
- `ttl` - 必需，键的过期时间（秒）

**说明**：
- 从文件中读取制表符分隔的键值对
- 将数据写入Redis，键格式为：`prefix + key`
- 所有键都设置相同的TTL（过期时间）
- 跳过空键或空值的行

**示例**：
```bash
./parse_uri_ip_and_write_cache.sh data.txt localhost 6379 "cache:" 3600
```

---

### 10. `refresh_api_gateway_token.sh` - 刷新API网关Token

**功能**：刷新API网关的访问令牌

**用法**：
```bash
./refresh_api_gateway_token.sh <app> <redis_host> <redis_port>
```

**参数**：
- `app` - 必需，应用名称（用于构建Redis键）
- `redis_host` - 必需，Redis服务器地址
- `redis_port` - 必需，Redis服务器端口

**说明**：
- 从Redis读取refresh token和API网关地址
- 调用API网关的刷新接口获取新token
- 将新token和refresh token保存回Redis，TTL为30天
- 需要 `jq` 命令来解析JSON响应

**依赖**：
- redis-cli
- curl
- jq

**示例**：
```bash
./refresh_api_gateway_token.sh myapp localhost 6379
```

---

## 音视频处理脚本

### 11. `play_audio.py` - 播放音频文件

**功能**：播放音频文件，支持指定播放区间和播放速度

**用法**：
```bash
python play_audio.py <audio_file> [--start SECONDS] [--end SECONDS] [--speed SPEED]
```

**参数**：
- `audio_file` - 必需，音频文件路径（支持mp3, m4a, wav等格式）
- `--start` - 可选，开始播放时间（秒），默认：0
- `--end` - 可选，结束播放时间（秒），默认：播放到文件末尾
- `--speed` - 可选，播放速度倍数，默认：1.0（正常速度）

**依赖**：
- pydub
- 系统需要安装ffmpeg或相应的音频解码器

**示例**：
```bash
python play_audio.py music.mp3
python play_audio.py music.mp3 --start 10 --end 60
python play_audio.py music.mp3 --speed 1.5
python play_audio.py music.mp3 --start 30 --end 90 --speed 0.8
```

---

### 12. `txt2voice.py` - 文本转语音

**功能**：将文本文件转换为语音（使用Microsoft Edge TTS）

**用法**：
```bash
python txt2voice.py <input_file> [output_file] [voice]
```

**参数**：
- `input_file` - 必需，输入文本文件路径
- `output_file` - 可选，输出音频文件路径，默认：output.mp3
- `voice` - 可选，语音模型，默认：en-US-JennyNeural

**依赖**：
- edge-tts
- pydub
- tqdm

**常用语音模型**：
- `zh-CN-XiaoxiaoNeural` - 中文，女声
- `zh-CN-YunxiNeural` - 中文，男声
- `en-US-JennyNeural` - 英文，女声
- `en-US-GuyNeural` - 英文，男声

**示例**：
```bash
python txt2voice.py text.txt
python txt2voice.py text.txt output.mp3
python txt2voice.py text.txt output.mp3 zh-CN-XiaoxiaoNeural
```

---

### 13. `voice2txt.py` - 语音转文本

**功能**：将音频文件转换为文本（使用OpenAI Whisper）

**用法**：
```bash
python voice2txt.py <audio_file> [--model MODEL] [--language LANGUAGE] [--output OUTPUT]
```

**参数**：
- `audio_file` - 必需，音频文件路径（支持mp3, wav, m4a等格式）
- `--model` - 可选，Whisper模型名称，默认：base
- `--language` - 可选，指定语言代码（如zh, en），默认：自动检测
- `--output` - 可选，输出文本文件路径，默认：输出到控制台

**依赖**：
- openai-whisper
- ffmpeg（用于音频处理）

**模型说明**：
- `tiny` - 最快，准确度较低，适合快速测试
- `base` - 平衡速度和准确度（推荐）
- `small` - 更准确，速度较慢
- `medium` - 高准确度，速度慢
- `large` - 最高准确度，速度最慢

**示例**：
```bash
python voice2txt.py audio.mp3
python voice2txt.py audio.mp3 --model small
python voice2txt.py audio.mp3 --language zh
python voice2txt.py audio.mp3 --output transcript.txt
```

---

## 网络服务脚本

### 14. `debug_server.py` - HTTP调试服务器

**功能**：HTTP调试服务器，用于查看和分析HTTP请求详情

**用法**：
```bash
python debug_server.py [--host HOST] [--port PORT] [--path PATH]
```

**参数**：
- `--host` - 可选，监听地址，默认：0.0.0.0
- `--port` - 可选，监听端口，默认：7788
- `--path` - 可选，调试路径前缀，默认：/debug

**说明**：
- 启动一个HTTP服务器，接收所有请求
- 当请求路径以指定前缀开头时，打印详细的请求信息
- 支持GET、POST、PUT、DELETE请求
- 用于调试HTTP客户端、API调用等场景

**示例**：
```bash
python debug_server.py
python debug_server.py --port 8080
python debug_server.py --host 127.0.0.1 --port 9000 --path /api
```

---

### 15. `send_kafka_template.py` - Kafka消息发送

**功能**：基于JSON模板生成并发送Kafka消息

**用法**：
```bash
python send_kafka_template.py --topic TOPIC --template_file FILE [--bootstrap SERVER] [--interval SECONDS]
```

**参数**：
- `--topic` - 必需，Kafka主题名称
- `--template_file` - 必需，JSON模板文件路径
- `--bootstrap` - 可选，Kafka服务器地址，默认：localhost:9092
- `--interval` - 可选，发送消息的间隔（秒），默认：1

**模板规则**：
- `random_int_MIN_MAX` - 生成MIN到MAX之间的随机整数
- `random_choice_A_B_C` - 从A、B、C中随机选择一个
- `now_ts` - 当前时间戳（精确到毫秒）
- 普通字符串/数字/布尔值 - 直接使用该值

**依赖**：
- kafka-python

**模板文件示例** (`template.json`):
```json
{
  "user_id": "random_int_1000_9999",
  "action": "random_choice_click_login_logout",
  "timestamp": "now_ts",
  "status": "active"
}
```

**示例**：
```bash
python send_kafka_template.py --topic test-topic --template_file template.json
python send_kafka_template.py --topic test-topic --template_file template.json --bootstrap kafka:9092 --interval 2
```

---

## 依赖要求

### 系统依赖

- **Bash脚本**：需要bash shell环境（通常Linux/macOS自带）
- **Python脚本**：需要Python 3.6+

### Python包依赖

安装所有Python依赖：
```bash
pip install pydub edge-tts tqdm openai-whisper kafka-python
```

### 系统工具依赖

- **ffmpeg**：用于音频处理（play_audio.py, txt2voice.py, voice2txt.py）
- **redis-cli**：用于Redis操作（parse_uri_ip_and_write_cache.sh, refresh_api_gateway_token.sh）
- **curl**：用于HTTP请求（refresh_api_gateway_token.sh）
- **jq**：用于JSON解析（refresh_api_gateway_token.sh）
- **docker**：用于容器管理（aws_jenkins_deployee_run_fe.sh）
- **gawk**：用于高级文本处理（git_user_stats.sh）

### 安装系统工具（Ubuntu/Debian）

```bash
sudo apt-get update
sudo apt-get install -y ffmpeg redis-tools curl jq docker.io gawk
```

### 安装系统工具（macOS）

```bash
brew install ffmpeg redis curl jq docker gawk
```

---

## 使用说明

### 权限要求

部分脚本需要root权限：
- `add_swap.sh` - 需要root权限
- `add_user_to_dev_group.sh` - 需要root权限
- `startup.sh` - 需要root权限

使用方式：
```bash
sudo ./add_swap.sh
```

### 脚本执行权限

首次使用前，需要为脚本添加执行权限：
```bash
chmod +x *.sh
chmod +x *.py
```

### 帮助信息

大多数脚本都支持查看帮助信息：
- Bash脚本：查看文件头部注释或直接运行（会显示用法）
- Python脚本：使用 `--help` 参数
  ```bash
  python script.py --help
  ```

---

## 脚本分类索引

### 按功能分类

| 功能类别 | 脚本列表 |
|---------|---------|
| 系统管理 | add_swap.sh, add_user_to_dev_group.sh, startup.sh |
| 容器部署 | aws_jenkins_deployee_run_fe.sh |
| Git工具 | git_nearest_direct_child_commit.sh, git_user_stats.sh |
| 数据处理 | filter_row_with_blank_field.sh, map_host_port_and_index_by_uri.sh, parse_uri_ip_and_write_cache.sh |
| API管理 | refresh_api_gateway_token.sh |
| 音视频 | play_audio.py, txt2voice.py, voice2txt.py |
| 网络服务 | debug_server.py, send_kafka_template.py |

### 按语言分类

| 语言 | 脚本数量 | 脚本列表 |
|-----|---------|---------|
| Bash | 10 | add_swap.sh, add_user_to_dev_group.sh, aws_jenkins_deployee_run_fe.sh, filter_row_with_blank_field.sh, git_nearest_direct_child_commit.sh, git_user_stats.sh, map_host_port_and_index_by_uri.sh, parse_uri_ip_and_write_cache.sh, refresh_api_gateway_token.sh, startup.sh |
| Python | 5 | debug_server.py, play_audio.py, send_kafka_template.py, txt2voice.py, voice2txt.py |

---

## 更新日志

- **2026** - 初始版本，包含15个实用脚本工具
- 所有脚本已添加详细注释和用户友好的交互提示

---

## 贡献

如有问题或建议，请直接修改脚本或联系维护者。

---

## 许可证

本脚本工具集为内部使用工具，请根据实际需求使用。

