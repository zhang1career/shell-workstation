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

### 100. `add_swap.sh` - 添加/调整Swap交换空间

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

### 101. `add_user_to_dev_group.sh` - 添加用户到dev组

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

### 102. `startup.sh` - 系统启动初始化脚本

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

### 103. `space-manager.sh` - 大容量文件管理

**功能**：管理大容量目录（如 Xcode DerivedData），支持迁移到外部磁盘或安全清理

**用法**：
```bash
# 迁移目录到外部磁盘
./space-manager.sh migrate <SOURCE> <TARGET>

# 清理目录
./space-manager.sh clean <SOURCE>
```

**参数**：
- `migrate` - 迁移模式，将源目录迁移到目标位置并创建符号链接
- `clean` - 清理模式，安全清理指定目录
- `<SOURCE>` - 源目录路径（支持 `~` 等路径展开）
- `<TARGET>` - 目标目录路径（仅迁移模式需要）

**说明**：
- **迁移功能**：
  - 使用 `rsync` 安全地将目录内容复制到目标位置（保留进度显示）
  - 删除原始目录后创建符号链接，实现透明访问
  - 适用于将大容量目录迁移到外部磁盘或不同分区
  - 迁移后原路径仍可使用，实际数据存储在目标位置

- **清理功能**：
  - 智能检测符号链接：如果是符号链接，会备份目标目录后再清理
  - 安全备份：清理前会自动创建带时间戳的备份目录
  - 原子操作：确保清理过程的安全性
  - 支持普通目录的直接清理

**特性**：
- 使用 `rsync` 而不是 `mv`，确保数据安全
- 避免嵌套符号链接问题
- 支持原子清理操作
- 自动路径展开（支持 `~` 等）
- 详细的执行步骤提示

**依赖**：
- bash
- rsync（用于迁移功能）
- 标准 Unix 工具（rm, ln, mkdir, date 等）

**使用场景**：
- Xcode DerivedData 迁移到外部磁盘
- 大型构建缓存目录管理
- 临时文件目录清理
- 释放系统磁盘空间

**示例**：
```bash
# 迁移 Xcode DerivedData 到外部磁盘
./space-manager.sh migrate \
  ~/Library/Developer/Xcode/DerivedData \
  /Volumes/ExternalDisk/Xcode/DerivedData

# 清理 Xcode DerivedData（如果是符号链接，会备份）
./space-manager.sh clean \
  ~/Library/Developer/Xcode/DerivedData

# 迁移其他大容量目录
./space-manager.sh migrate \
  ~/Downloads/large-files \
  /Volumes/Backup/large-files
```

**注意事项**：
- 迁移操作会删除原始目录，请确保目标位置有足够空间
- 清理操作对于符号链接会创建备份，普通目录会直接删除
- 建议在执行前确认路径正确，避免误操作
- 确保目标位置存在或可访问

---

## 开发工具脚本

### 200. `aws_jenkins_deployee_run_fe.sh` - 部署前端Docker容器

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

### 201. `git_nearest_direct_child_commit.sh` - 查找最近的直接子提交

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

### 202. `git_user_stats.sh` - Git用户统计

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

### 203. `laravel_diagnose.php` - Laravel环境诊断

**功能**：检查Laravel项目的环境变量和数据库配置

**用法**：
```bash
php laravel_diagnose.php
```

**说明**：
- 需要在Laravel项目根目录下运行（需要访问vendor/autoload.php和bootstrap/app.php）
- 检查环境变量：APP_ENV, DB_CONNECTION, DB_HOST, DB_PORT, DB_DATABASE, DB_USERNAME, DB_PASSWORD
- 检查数据库配置（从config/database.php读取）
- 检查.env文件的存在性、大小、权限和可读性
- 检查系统环境变量
- 密码信息会被隐藏显示为`***`

**检查内容**：
1. **环境变量检查**：显示所有数据库相关的环境变量
2. **数据库配置检查**：显示从Laravel配置中读取的数据库连接信息
3. **.env文件检查**：检查.env文件是否存在、大小、权限和可读性，并显示部分DB_配置行（不包含敏感信息）
4. **系统环境变量检查**：检查系统级别的环境变量

**依赖**：
- PHP 7.4+
- Laravel框架（需要vendor/autoload.php和bootstrap/app.php）

**示例**：
```bash
# 在Laravel项目根目录下运行
cd /path/to/laravel-project
php laravel_diagnose.php

# 或者从其他位置运行（需要指定Laravel项目路径）
php /path/to/script-tool/laravel_diagnose.php
```

**输出示例**：
```
=== 环境变量检查 ===
APP_ENV: local
DB_CONNECTION: mysql
...

=== 数据库配置检查 ===
...

=== .env文件检查 ===
.env文件存在
...
找到的DB_配置行:
...

=== 系统环境变量检查 ===
...
```

---

### 204. `pip_pkg_size.sh` - Pip包大小统计

**功能**：统计当前 Python 环境中已安装 pip 包的磁盘占用大小，按从大到小排序输出

**用法**：
```bash
./pip_pkg_size.sh
```

**说明**：
- 统计当前 Python 环境中所有已安装的 pip 包的磁盘占用
- 按包大小从大到小排序输出
- 自动转换单位显示（KB、MB、GB）
- 执行过程中显示进度条，方便查看处理进度
- 使用临时文件存储中间结果，处理完成后自动清理

**工作原理**：
1. 通过 `pip list` 获取已安装包列表
2. 通过 `pip show <pkg>` 获取包的安装路径（Location）
3. 假定包目录位于 `site-packages/<package_name>`（通常是小写）
4. 使用 `du` 统计目录大小（单位 KB）
5. 所有结果汇总后按大小排序并格式化输出

**依赖**：
- pip（Python 包管理器）
- du（用于统计目录大小）
- awk / sort / tr / wc（系统自带工具）

**输出格式**：
- 自动根据大小选择合适的单位（KB、MB、GB）
- 格式：`大小 包名`，例如：
  ```
  125.3 MB  numpy
   45.2 MB  pandas
   12.5 MB  scipy
    3.2 MB  requests
  ```

**示例**：
```bash
# 直接运行脚本
./pip_pkg_size.sh

# 输出示例：
# Scanning pip packages (150 total)...
# [########################################] 100% (150/150) numpy
# Sorting results...
# 125.3 MB  numpy
#  45.2 MB  pandas
#  12.5 MB  scipy
#   3.2 MB  requests
# ...
```

**注意事项**：
- 脚本使用 `set -e`，任何命令出错会立即退出
- 只统计实际存在的包目录，避免不存在的目录导致错误
- 进度条会实时更新，显示当前处理的包名

---

### 205. `png_info.py` - PNG图片信息分析

**功能**：分析PNG图片的尺寸信息（宽度和高度），并打印详细信息

**用法**：
```bash
python png_info.py <image.png>
```

**参数**：
- `image.png` - 必需，PNG图片文件路径

**说明**：
- 分析PNG图片的像素尺寸（宽度 x 高度）
- 显示图片格式、文件大小、宽高比等信息
- 支持相对路径和绝对路径
- 提供友好的错误提示和帮助信息

**输出信息**：
- 文件路径
- 图片格式
- 图片尺寸（宽度 x 高度，单位：像素）
- 文件大小（字节和MB）
- 宽高比

**依赖**：
- Python 3.6+
- Pillow (PIL) 库

**安装依赖**：
```bash
pip install Pillow
```

**示例**：
```bash
# 分析当前目录下的PNG图片
python png_info.py example.png

# 分析指定路径的PNG图片
python png_info.py /path/to/image.png

# 查看帮助信息
python png_info.py --help
```

**输出示例**：
```
============================================================
PNG 图片信息
============================================================
文件路径: example.png
图片格式: PNG
图片尺寸: 1920 x 1080 像素
文件大小: 1,245,678 字节 (1.19 MB)
宽高比: 1.78
============================================================
```

**注意事项**：
- 虽然主要针对PNG格式，但脚本会尝试解析其他格式的图片
- 对于非PNG格式的图片，会显示警告信息
- 如果文件不存在或无法读取，会显示相应的错误信息

---

### 206. `ios_screenshot_resize.py` - iOS App Store 截屏尺寸转换

**功能**：将截屏图片转换为 App Store Connect 要求的尺寸，支持单张或批量、预设尺寸或自定义尺寸

**用法**：
```bash
# 单张图，预设 iPhone 6.7" 竖版（1290 x 2796）
python ios_screenshot_resize.py screenshot.png --preset iphone67

# 自定义尺寸
python ios_screenshot_resize.py screenshot.png --size 1290x2796

# 批量转换目录下所有图片
python ios_screenshot_resize.py ./screenshots/ --preset iphone67 --output ./out/
```

**参数**：
- `input` - 必需，输入文件或目录路径
- `--preset` / `-p` - 预设尺寸：iphone69, iphone67, iphone65, iphone63, iphone61, iphone55, iphone47, ipad129, ipad11 等
- `--size` / `-s` - 自定义尺寸，如 `1290x2796`（与 --preset 二选一）
- `--output` / `-o` - 输出目录，默认在输入同目录下创建 `ios_screenshots_out`
- `--mode` / `-m` - 缩放模式：`fit`（留边适配）、`fill`（裁剪填满，默认）、`stretch`（拉伸）
- `--suffix` - 输出文件名后缀，默认 `_ios`

**依赖**：
- Python 3.6+
- Pillow (PIL)：`pip install Pillow`

**说明**：输出为 JPEG，适合直接上传到 App Store Connect。尺寸依据 [Apple 截屏规范](https://developer.apple.com/help/app-store-connect/reference/app-information/screenshot-specifications)。

---

## 数据处理脚本

### 300. `filter_row_with_blank_field.sh` - 过滤空白字段行

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

### 301. `map_host_port_and_index_by_uri.sh` - 服务映射转换

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

### 302. `parse_uri_ip_and_write_cache.sh` - 写入Redis缓存

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

### 303. `refresh_api_gateway_token.sh` - 刷新API网关Token

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

### 400. `play_audio.py` - 播放音频文件

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

### 401. `txt2voice.py` - 文本转语音

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

### 402. `voice2txt.py` - 语音转文本

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

### 403. `wav2mp3.py` - WAV 转 MP3 音频格式转换

**功能**：将 WAV 音频文件转换为 MP3 格式，支持单文件或批量转换，可自定义采样率和比特率

**用法**：
```bash
python wav2mp3.py <input_path> <output_path> [options]
```

**参数**：
- `input_path` - 必需，输入文件或目录路径
- `output_path` - 必需，输出目录路径
- `-r`, `--sample-rate` - 可选，采样率 (Hz)，默认：44100
- `-b`, `--bitrate` - 可选，比特率 (kbps)，默认：256

**说明**：
- 支持单文件和批量转换模式
- 目录模式下会递归查找所有 WAV 文件
- 批量转换时保持原有目录结构
- 自动创建输出目录

**依赖**：
- pydub：`pip install pydub`
- ffmpeg（系统安装）

**示例**：
```bash
# 转换单个文件（使用默认参数：44.1kHz, 256kbps）
python wav2mp3.py input.wav ./output/

# 批量转换目录下所有 WAV 文件
python wav2mp3.py ./wav_files/ ./mp3_files/

# 自定义采样率和比特率
python wav2mp3.py input.wav ./output/ -r 48000 -b 320

# 使用较低比特率（节省空间）
python wav2mp3.py ./wav_files/ ./mp3_files/ -b 128

# CD 品质（44.1kHz, 320kbps）
python wav2mp3.py ./recordings/ ./compressed/ -r 44100 -b 320
```

**输出示例**：
```
============================================================
WAV to MP3 Converter
============================================================
输入路径: ./wav_files
输出路径: ./mp3_files
采样率: 44100 Hz
比特率: 256 kbps
文件数量: 5
============================================================
[1/5] 转换: track01.wav -> track01.mp3
  ✓ 成功
[2/5] 转换: track02.wav -> track02.mp3
  ✓ 成功
...
============================================================
转换完成: 成功 5, 失败 0
============================================================
```

**常用参数组合**：
| 用途 | 采样率 | 比特率 | 说明 |
|------|--------|--------|------|
| 高品质 | 48000 | 320 | 接近无损品质 |
| CD 品质 | 44100 | 256 | 默认设置，推荐 |
| 标准品质 | 44100 | 192 | 一般音乐播放 |
| 语音/播客 | 22050 | 128 | 适合人声 |
| 小文件 | 22050 | 64 | 最小文件大小 |

---

### 404. `mix_sound.py` - 双轨音频混音

**功能**：将两个音频文件混音后通过系统扬声器实时播放，支持音量、延迟、淡入淡出、EQ、压缩与限幅

**用法**：
```bash
python mix_sound.py <audio1> <audio2> [options]
```

**参数**：
- `audio1` - 必需，第一个音频文件路径
- `audio2` - 必需，第二个音频文件路径
- `--vol1` - 可选，第一轨音量（数值如 1.0 或分贝如 -6dB），默认：1.0
- `--vol2` - 可选，第二轨音量，默认：1.0
- `--delay2` - 可选，第二轨延迟秒数，默认：0
- `--loop2` - 可选，第二轨循环播放
- `--fadein` - 可选，两轨淡入时长（秒），默认：0
- `--fadeout` - 可选，两轨淡出时长（秒），默认：0
- `--eq1` - 可选，第一轨 FFmpeg EQ/滤镜，如 `highpass=100`
- `--eq2` - 可选，第二轨 FFmpeg EQ/滤镜
- `--compress` - 可选，混音后加压缩（acompressor）
- `--limit` - 可选，混音后加限幅（alimiter），防止削波

**说明**：
- 使用 ffmpeg 做混音与编码，ffplay 从管道播放，不生成中间文件
- 音量支持数值（1.0）或分贝（-6dB）
- 第二轨可设置延迟、循环、淡入淡出
- 可选 EQ 滤镜（如 highpass、equalizer）与后处理（压缩、限幅）

**依赖**：
- Python 3.6+（仅用标准库）
- ffmpeg、ffplay（系统安装，通常随 ffmpeg 一起提供）

**示例**：
```bash
# 基本混音（等音量）
python mix_sound.py voice.wav bgm.mp3

# 人声大、背景小
python mix_sound.py voice.wav bgm.mp3 --vol1 1.0 --vol2 0.3

# 背景音循环 + 淡入淡出
python mix_sound.py voice.wav bgm.mp3 --loop2 --fadein 2 --fadeout 3

# 第二轨延迟 0.5 秒
python mix_sound.py a.wav b.wav --delay2 0.5

# 加限幅防止削波
python mix_sound.py a.wav b.wav --limit

# 查看帮助
python mix_sound.py --help
```

**注意事项**：
- 需已安装 ffmpeg 与 ffplay；若未找到会提示错误并退出
- 按 Ctrl+C 可中断播放

---

### 405. `change_sound_volume.py` - MP3 响度归一化

**功能**：使用 EBU R128 标准对 MP3 进行响度归一化，尽量不损失声音细节

**用法**：
```bash
python change_sound_volume.py <input_mp3> [output_mp3] [options]
```

**参数**：
- `input_mp3` - 必需，输入 MP3 文件路径
- `output_mp3` - 可选，输出 MP3 文件路径（默认：输入名_normalized.mp3）
- `-l`, `--lufs` - 可选，目标响度 LUFS，常用 -16（广播/播客）或 -14（流媒体），默认：-16
- `-t`, `--tp` - 可选，真峰值限制 dB，默认：-1.5
- `-r`, `--lra` - 可选，响度范围 LRA，默认：11.0

**说明**：
- 使用 ffmpeg loudnorm 滤镜实现 EBU R128 响度归一化
- 输出为 LAME V0 高质量 MP3（约 245 kbps VBR）
- 可指定目标响度、真峰值限制和响度范围
- 输出路径默认与输入同目录，文件名加 `_normalized`

**依赖**：
- Python 3.6+（仅用标准库）
- ffmpeg（需包含 loudnorm 滤镜与 libmp3lame 编码器）

**示例**：
```bash
# 使用默认 -16 LUFS，输出为 input_normalized.mp3
python change_sound_volume.py input.mp3

# 指定输出文件和目标响度 -14 LUFS
python change_sound_volume.py input.mp3 output_normalized.mp3 -l -14

# 仅指定目标响度，输出使用默认命名
python change_sound_volume.py input.mp3 -l -14

# 自定义真峰值和响度范围
python change_sound_volume.py input.mp3 out.mp3 -l -16 -t -2.0 -r 11

# 查看帮助
python change_sound_volume.py --help
```

**注意事项**：
- 输出路径不能与输入路径相同，否则会报错
- 若未找到 ffmpeg 或 ffmpeg 执行失败，会提示错误并退出

---

## 网络服务脚本

### 500. `debug_server.py` - HTTP调试服务器

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

### 501. `send_kafka_template.py` - Kafka消息发送

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

### 502. `simple_server.py` - 简单HTTP服务器

**功能**：监听指定端口，接收HTTP请求并返回预定义的JSON响应数据

**用法**：
```bash
python simple_server.py [--port PORT] [--host HOST]
```

**参数**：
- `--port`, `-p` - 可选，监听端口，默认：8080
- `--host`, `-H` - 可选，监听地址，默认：0.0.0.0（监听所有网络接口）

**说明**：
- 启动一个简单的HTTP服务器，用于测试、调试和模拟API服务
- 支持GET、POST、PUT、DELETE请求方法
- 所有请求都返回相同的预定义JSON响应
- POST和PUT请求会打印请求体内容
- 自动处理JSON请求体的解析
- 支持跨域请求（CORS）
- 提供详细的请求日志，包括时间戳、请求方法和路径

**响应格式**：
```json
{
  "code": 0,
  "msg": "ok",
  "data": {
    "name": "simple-server",
    "version": "1.0"
  }
}
```

**依赖**：
- Python 3.6+（使用标准库，无需额外安装包）

**使用场景**：
- API接口测试和调试
- 前端开发时的模拟后端服务
- 网络请求测试
- 负载测试和性能测试

**示例**：
```bash
# 使用默认端口8080
python simple_server.py

# 指定端口
python simple_server.py --port 3000

# 指定端口和监听地址（只监听本地）
python simple_server.py --port 9000 --host 127.0.0.1

# 使用短参数
python simple_server.py -p 5000 -H 0.0.0.0
```

**测试示例**：
```bash
# 启动服务器
python simple_server.py --port 8080

# 在另一个终端测试GET请求
curl http://localhost:8080

# 测试POST请求
curl -X POST http://localhost:8080 \
  -H "Content-Type: application/json" \
  -d '{"test": "data"}'

# 测试PUT请求
curl -X PUT http://localhost:8080 \
  -H "Content-Type: application/json" \
  -d '{"key": "value"}'

# 测试DELETE请求
curl -X DELETE http://localhost:8080
```

---

## 依赖要求

### 系统依赖

- **Bash脚本**：需要bash shell环境（通常Linux/macOS自带）
- **Python脚本**：需要Python 3.6+

### Python包依赖

安装所有Python依赖：
```bash
pip install pydub edge-tts tqdm openai-whisper kafka-python Pillow
```

### 系统工具依赖

- **ffmpeg / ffplay**：用于音频处理（play_audio.py, txt2voice.py, voice2txt.py, mix_sound.py, change_sound_volume.py）
- **redis-cli**：用于Redis操作（parse_uri_ip_and_write_cache.sh, refresh_api_gateway_token.sh）
- **curl**：用于HTTP请求（refresh_api_gateway_token.sh）
- **jq**：用于JSON解析（refresh_api_gateway_token.sh）
- **docker**：用于容器管理（aws_jenkins_deployee_run_fe.sh）
- **gawk**：用于高级文本处理（git_user_stats.sh）
- **rsync**：用于文件同步（space-manager.sh）

### 安装系统工具（Ubuntu/Debian）

```bash
sudo apt-get update
sudo apt-get install -y ffmpeg redis-tools curl jq docker.io gawk rsync
```

### 安装系统工具（macOS）

```bash
brew install ffmpeg redis curl jq docker gawk rsync
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
| 系统管理 | add_swap.sh, add_user_to_dev_group.sh, space-manager.sh, startup.sh |
| 容器部署 | aws_jenkins_deployee_run_fe.sh |
| Git工具 | git_nearest_direct_child_commit.sh, git_user_stats.sh |
| Laravel工具 | laravel_diagnose.php |
| Python工具 | pip_pkg_size.sh, png_info.py, ios_screenshot_resize.py |
| 数据处理 | filter_row_with_blank_field.sh, map_host_port_and_index_by_uri.sh, parse_uri_ip_and_write_cache.sh |
| API管理 | refresh_api_gateway_token.sh |
| 音视频 | play_audio.py, txt2voice.py, voice2txt.py, wav2mp3.py, mix_sound.py, change_sound_volume.py |
| 网络服务 | debug_server.py, send_kafka_template.py, simple_server.py |

### 按语言分类

| 语言 | 脚本数量 | 脚本列表 |
|-----|---------|---------|
| Bash | 12 | add_swap.sh, add_user_to_dev_group.sh, aws_jenkins_deployee_run_fe.sh, filter_row_with_blank_field.sh, git_nearest_direct_child_commit.sh, git_user_stats.sh, map_host_port_and_index_by_uri.sh, parse_uri_ip_and_write_cache.sh, pip_pkg_size.sh, refresh_api_gateway_token.sh, space-manager.sh, startup.sh |
| Python | 11 | change_sound_volume.py, debug_server.py, ios_screenshot_resize.py, mix_sound.py, play_audio.py, png_info.py, send_kafka_template.py, simple_server.py, txt2voice.py, voice2txt.py, wav2mp3.py |
| PHP | 1 | laravel_diagnose.php |

---

## 更新日志

- **2026** - 初始版本，包含16个实用脚本工具
- **2026** - 新增 pip 包大小统计脚本（pip_pkg_size.sh）
- **2026** - 新增 PNG 图片信息分析脚本（png_info.py）
- **2026** - 新增 WAV 转 MP3 音频转换脚本（wav2mp3.py）
- **2026** - 新增双轨音频混音脚本（mix_sound.py），并补充使用说明与注释
- **2026** - 新增 MP3 响度归一化脚本（change_sound_volume.py）
- 所有脚本已添加详细注释和用户友好的交互提示

---

## 贡献

如有问题或建议，请直接修改脚本或联系维护者。

---

## 许可证

本脚本工具集为内部使用工具，请根据实际需求使用。

