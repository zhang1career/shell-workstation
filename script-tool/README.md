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

### 104. `clean_docker.sh` - 关闭 Docker 进程并清理脏数据

**功能**：关闭 Docker 相关进程并可选清理未使用的镜像、容器、卷和构建缓存

**用法**：
```bash
sudo ./clean_docker.sh [--clean-data] [--force]
```

**参数**：
- `--clean-data` - 可选，清理 Docker 脏数据（未使用镜像、容器、卷、构建缓存）
- `--force`, `-f` - 可选，跳过交互确认，直接执行
- `-h`, `--help` - 显示帮助信息

**说明**：
- **需要 root 权限**，建议使用 `sudo` 执行
- 适用于 **macOS**，会停止 Docker 的 launchctl 服务（vmnetd、socket）
- 执行顺序：
  1. 若指定 `--clean-data`，先清理脏数据（需 Docker 尚在运行）
  2. 终止所有 Docker 相关进程
  3. 停止 system 级 Docker 服务
  4. 清理残留进程
- `--clean-data` 会执行 `docker system prune -af --volumes`，将删除未使用的镜像、容器和卷，请确认已备份重要数据

**依赖**：
- bash
- docker（仅在使用 `--clean-data` 时需要）

**示例**：
```bash
# 仅关闭 Docker 进程
sudo ./clean_docker.sh

# 关闭进程并清理脏数据
sudo ./clean_docker.sh --clean-data

# 非交互模式（适用于脚本调用）
sudo ./clean_docker.sh --clean-data --force
```

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

### 207. `font_preview.py` - 字体 PDF 预览

**功能**：根据 TTF/OTF 字体文件生成一页 PDF 预览，包含英文与中文示例句，并可选择用系统默认程序打开

**用法**：
```bash
python font_preview.py <字体路径> [--no-open] [-o 输出路径]
```

**参数**：
- `字体路径` - 必需，字体文件路径（.ttf 或 .otf）
- `--no-open` - 可选，生成 PDF 后不自动打开
- `-o`, `--output` - 可选，输出 PDF 路径（默认使用临时文件）

**说明**：
- 支持 TTF、OTF（含 CFF 轮廓）格式
- 预览页使用 36pt 字号，展示 "The quick brown fox" 与 "中文字体测试"
- 未指定 `-o` 时使用系统临时目录，脚本结束后由系统清理
- 若字体缺少部分字形（如西文字体无中文），fpdf2 可能输出缺失字形提示，不影响 PDF 生成

**依赖**：
- Python 3.6+
- fpdf2：`pip install fpdf2`

**示例**：
```bash
# 生成预览并自动打开
python font_preview.py /path/to/GenRyuMin2TW-M.otf

# 仅生成到指定文件，不打开
python font_preview.py ./MyFont.ttf --no-open -o preview.pdf

# 使用模块方式运行
python -m font_preview ./MyFont.otf --no-open
```

---

### 208. `gen_patch.sh` - Git 差异补丁生成

**功能**：将指定 Git 仓库中相对于 HEAD 的所有修改（未暂存 + 已暂存）导出为 patch 文件

**用法**：
```bash
./gen_patch.sh <target_dir> <output_patch_file>
```

**参数**：
- `target_dir` - 必需，目标 Git 仓库的目录路径
- `output_patch_file` - 必需，输出的 patch 文件路径（如 `my_changes.patch`）

**说明**：
- 生成的 patch 包含工作区与暂存区相对于 HEAD 的所有修改
- 可用于备份修改、跨仓库迁移代码、代码审查等场景
- 应用 patch 时使用 `git apply <patch_file>` 或 `git am <patch_file>`

**依赖**：
- bash
- git

**示例**：
```bash
# 将当前项目的修改导出为 patch
./gen_patch.sh . ./my_changes.patch

# 指定其他项目目录
./gen_patch.sh /path/to/my_project ../backup.patch

# 在目标项目中应用补丁
cd /path/to/old_project
git apply /path/to/my_changes.patch

# 若应用失败可尝试三方合并
git apply --3way /path/to/my_changes.patch
```

---

### 209. `png_cutout.py` - PNG 棋盘格转透明

**功能**：将输入 PNG 中“棋盘格”颜色（灰白格）的像素改为透明并保存为新 PNG。常见导出错误会把透明区域变成 #fff / #c0c0c0 等灰白格，本脚本将这些像素的 alpha 置为 0。

**用法**：
```bash
python png_cutout.py <input.png> [-o output.png]
```

**参数**：
- `input` - 必需，输入 PNG 文件路径
- `-o`, `--output` - 可选，输出 PNG 路径，默认：输入同目录下「输入名.transparent.png」

**说明**：
- 判定为棋盘格的条件：像素接近灰色（R≈G≈B，通道差 ≤ 15）且偏亮（平均亮度 ≥ 170）
- 输出路径未指定时自动生成为「输入名.transparent.png」；不允许输出与输入相同路径，以免覆盖原图
- 运行后会提示已保存路径及「设为透明的像素数 / 总像素数」

**依赖**：
- Python 3.6+
- Pillow (PIL)：`pip install Pillow`

**示例**：
```bash
# 默认输出为 input.transparent.png
python png_cutout.py image.png

# 指定输出文件
python png_cutout.py image.png -o image_transparent.png
python png_cutout.py image.png --output image_clean.png
```

---

### 210. `png2jpg.py` - PNG 转 JPG 图片格式转换

**功能**：将 PNG 图片转换为 JPG 格式。若 PNG 有透明通道，会先以白色填充后再导出。

**用法**：
```bash
python png2jpg.py <input.png> [output.jpg] [-q N]
```

**参数**：
- `input` - 必需，输入 PNG 文件路径
- `output` - 可选，输出 JPG 路径，默认：与输入同目录、同主名的 .jpg
- `-q`, `--quality` - 可选，JPEG 质量 1–100（默认 95）

**说明**：
- JPG 不支持透明通道，若 PNG 含透明区域，会以白色填充后再导出
- 输出路径未指定时，自动生成为「输入名.jpg」

**依赖**：
- Python 3.6+
- Pillow (PIL)：`pip install Pillow`

**示例**：
```bash
# 默认输出为 logo.jpg
python png2jpg.py logo.png

# 指定输出文件
python png2jpg.py logo.png logo.jpg

# 指定 JPEG 质量
python png2jpg.py logo.png --quality 90
python png2jpg.py logo.png -q 80
```

---

### 210a. `jpg2png.py` - JPG 转 PNG 图片格式转换

**功能**：将 JPG/JPEG 图片转换为 PNG 格式。PNG 为无损格式，适合需要保留图片质量或后续编辑的场景。

**用法**：
```bash
python jpg2png.py <input.jpg> [output.png] [-c N]
```

**参数**：
- `input` - 必需，输入 JPG/JPEG 文件路径
- `output` - 可选，输出 PNG 路径，默认：与输入同目录、同主名的 .png
- `-c`, `--compression` - 可选，PNG 压缩级别 0–9，0 无压缩最快，9 最小文件（默认 6）

**说明**：
- PNG 为无损格式，转换后不会丢失 JPG 已有的细节
- 支持 CMYK 等模式的 JPG，会自动转换为 RGB
- 输出路径未指定时，自动生成为「输入名.png」

**依赖**：
- Python 3.6+
- Pillow (PIL)：`pip install Pillow`

**示例**：
```bash
# 默认输出为 photo.png
python jpg2png.py photo.jpg

# 指定输出文件
python jpg2png.py photo.jpg photo.png

# 指定 PNG 压缩级别（9 为最小文件）
python jpg2png.py photo.jpg --compression 9
python jpg2png.py photo.jpg -c 0
```

---

### 210b. `md2pdf.py` - Markdown 转 PDF

**功能**：将 Markdown 文件转换为 PDF，优先使用 Playwright + Chromium（中文支持更好）。

**用法**：
```bash
python md2pdf.py <input.md> [output.pdf]
```

**参数**：
- `input.md` - 必需，输入 Markdown 文件路径
- `output.pdf` - 可选，输出 PDF 路径（默认与输入同目录同名 `.pdf`）

**说明**：
- 先将 Markdown 渲染为 HTML（支持表格、围栏代码块、目录）
- 优先使用 Playwright 的 Chromium 生成 PDF；若未安装则尝试 `pdfkit`
- 推荐方式（中文显示更稳定）：
  - `pip install markdown playwright`
  - `playwright install chromium`

**示例**：
```bash
# 输出为 README.pdf
python md2pdf.py README.md

# 指定输出路径
python md2pdf.py README.md ./output/resume.pdf
```

---

### 212. `clean_worktree_interactive.sh` - Git Worktree 交互式清理

**功能**：交互式清理 Git Worktree 及其关联分支，逐个询问是否删除

**用法**：
```bash
./clean_worktree_interactive.sh [--dry-run]
```

**参数**：
- `--dry-run` - 可选，仅模拟执行，不实际删除（用于预览将要执行的操作）

**说明**：
- 脚本会列出当前仓库的所有 worktree，逐个询问是否删除
- 显示每个 worktree 的路径和分支信息
- **删除 worktree 时会同时删除其关联的本地分支**
- **保护机制**：当前分支和主分支（main/master）会自动跳过，不允许删除
- 当前工作目录所在的 worktree 会特别标记提示
- 删除完成后会自动执行 `git worktree prune` 清理失效引用
- 使用 `--dry-run` 可安全预览操作，不会实际修改任何内容

**依赖**：
- bash
- git

**示例**：
```bash
# 交互式清理 worktree
./clean_worktree_interactive.sh

# 模拟运行，仅预览将要执行的操作
./clean_worktree_interactive.sh --dry-run
```

**输出示例**：
```
🔧 Git Worktree 交互式清理工具

📋 发现 4 个 worktree

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[1/4] 📁 /path/to/main
        🌿 [main]
        🔒 主分支，已保护（自动跳过）
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[2/4] 📁 /path/to/develop
        🌿 [develop]
        🔒 当前分支，已保护（自动跳过）
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[3/4] 📁 /path/to/feature-branch
        🌿 [feature-branch]
        ⚠️  删除将同时移除 worktree 和分支 [feature-branch]
        是否删除? [y/N]: y
        🗑️  正在删除 worktree...
        ✅ worktree 已删除
        🗑️  正在删除分支 [feature-branch]...
        ✅ 分支已删除
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[4/4] 📁 /path/to/bugfix
        🌿 [bugfix]
        ⚠️  删除将同时移除 worktree 和分支 [bugfix]
        是否删除? [y/N]: n
        ⏭️  已跳过
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ 操作完成
   已删除 worktree: 1 个
   已删除分支: 1 个
   已保护: 2 个
   已跳过: 1 个
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**注意事项**：
- 删除 worktree 会同时删除其工作目录**和关联分支**，请确保没有未提交的更改
- 当前分支和主分支（main/master）会自动保护，无法删除
- 建议先使用 `--dry-run` 预览操作

---

### 213. `list_git_modifying_branches` - 列出文件曾被修改过的分支

**功能**：列出指定文件在本地分支中曾被修改过的所有分支，并显示各分支上最近的修改提交

**用法**：
```bash
./list_git_modifying_branches <file-path>
```

**参数**：
- `file-path` - 必需，要查询的文件路径（相对于仓库根目录或绝对路径）

**说明**：
- 遍历所有本地分支（refs/heads/），检查该文件是否在该分支历史中被修改
- 若有修改，输出分支名及该分支上对该文件的最近 3 次提交（hash、日期、摘要）
- 用于快速定位哪些分支曾改动过某个文件

**依赖**：
- bash
- git

**示例**：
```bash
# 查询 README 被哪些分支修改过
./list_git_modifying_branches README.md

# 查询源码文件
./list_git_modifying_branches src/main.py
```

---

### 211a. `djvu2pdf.py` - DJVU 转 PDF 文档格式转换

**功能**：将 DJVU 文件转换为 PDF 格式，支持中文路径与中文内容

**用法**：
```bash
python djvu2pdf.py <input> [output]
python djvu2pdf.py <输入目录> --output-dir <输出目录>
```

**参数**：
- `input` - 必需，输入 DJVU 文件或目录路径
- `output` - 可选，单文件时指定输出 PDF 路径（默认：输入同目录、同主名.pdf）
- `-o`, `--output-dir` - 可选，批量转换时的输出目录

**说明**：
- 支持单文件和批量转换（输入目录时处理其中的 .djvu/.djv 文件）
- **支持中文路径和中文内容**：Python 3 使用 UTF-8，DJVU/PDF 可正确保留中文
- 使用 djvulibre 的 `ddjvu` 命令进行转换

**依赖**：
- Python 3.6+（仅用标准库）
- djvulibre（提供 ddjvu 命令）

**安装 djvulibre**：
```bash
# macOS
brew install djvulibre

# Ubuntu/Debian
sudo apt install djvulibre-bin
```

**示例**：
```bash
# 单文件，输出为 book.pdf
python djvu2pdf.py book.djvu

# 指定输出路径
python djvu2pdf.py book.djvu output.pdf

# 支持中文文件名
python djvu2pdf.py 中文书名.djvu

# 批量转换目录
python djvu2pdf.py ./djvu_books/ --output-dir ./pdf_out/
```

---

### 211. `image_filter.py` - 图片滤镜效果

**功能**：对 JPG 图片应用滤镜效果，目前支持高斯模糊。

**用法**：
```bash
python image_filter.py <input.jpg> <output.jpg> [--filter gaussian_blur] [--radius N]
```

**参数**：
- `input` - 必需，输入 JPG 图片文件路径
- `output` - 必需，输出图片文件路径
- `-f`, `--filter` - 可选，滤镜类型，目前仅支持 gaussian_blur（默认）
- `-r`, `--radius` - 可选，高斯模糊半径（像素），数值越大模糊越强（默认 5）

**说明**：
- 依赖 Pillow (PIL)，需先安装：`pip install Pillow`
- 输出格式与输入保持一致（JPG）

**示例**：
```bash
# 使用默认半径 5 的高斯模糊
python image_filter.py photo.jpg output_blurred.jpg

# 指定模糊半径
python image_filter.py photo.jpg output.jpg --filter gaussian_blur --radius 10
python image_filter.py photo.jpg output.jpg -r 8
```

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

### 406. `pick_sound.py` - 音高拾音

**功能**：从麦克风实时采集音频，检测音高（基频），将不同音高分别保存为 WAV 文件

**用法**：
```bash
python pick_sound.py <输出目录>
```

**参数**：
- `输出目录` - 必需，保存各音高 WAV 文件的目录（不存在会自动创建）

**说明**：
- 使用 sounddevice 从默认麦克风录音，librosa YIN 算法检测基频
- 音高范围：C2 ~ C7；每个音高只保存一次，文件名如 `C4.wav`、`A#5.wav`
- 低于能量阈值的片段视为静音/环境噪声，不参与检测
- 按 **Enter** 键结束拾音（无需管理员权限，跨平台可用）
- 每个音高最多保存 1 秒，44.1 kHz 单声道 WAV

**依赖**：
- Python 3.6+
- sounddevice、soundfile、librosa、numpy

**安装依赖**：
```bash
pip install sounddevice soundfile librosa numpy
```

**示例**：
```bash
# 将采样保存到当前目录下的 samples
python pick_sound.py ./samples

# 保存到指定目录
python pick_sound.py ~/Music/piano_notes
```

**注意事项**：
- 需允许终端/IDE 使用麦克风
- 环境安静、音源清晰时识别更稳定

---

### 407. `filter_sound.py` - 音高 WAV 滤波与音量均衡

**功能**：对按音高命名的 WAV 文件进行音高校验、带通滤波和音量均衡后输出

**用法**：
```bash
python filter_sound.py <输入目录> <输出目录>
```

**参数**：
- `输入目录` - 必需，存放待处理的 WAV 文件（文件名即期望音高，如 C4.wav、A#5.wav）
- `输出目录` - 必需，处理后的 WAV 输出目录（不存在会自动创建）

**说明**：
- 仅处理扩展名为 `.wav` 的文件；文件名（不含扩展名）视为期望音高
- 使用 YIN 检测实际音高，仅当「检测音高」与「文件名音高」一致时才通过校验
- 通过校验的音频会做以该音高为中心的带通滤波（默认 ±1 八度），再归一化到目标 RMS 音量后写出
- 未通过校验的文件会打印原因（无法识别音高 / 音高不匹配），不写入输出目录

**依赖**：
- Python 3.6+
- numpy、librosa、soundfile、scipy

**安装依赖**：
```bash
pip install numpy librosa soundfile scipy
```

**示例**：
```bash
# 将 samples 下 WAV 校验、滤波、均衡后输出到 filtered
python filter_sound.py ./samples ./filtered

# 指定绝对路径
python filter_sound.py ~/Music/raw_notes ~/Music/clean_notes
```

**注意事项**：
- 输入文件建议为单音、音高清晰的 WAV（如由 pick_sound.py 采集），校验与滤波效果更好

---

### 408. `trim_audio_silence.py` - 音频去静音并裁剪前段

**功能**：去掉音频开头、结尾的静音，保留有声音区域；可选用 `--lifetime` 只保留有声音开始后的前 N 毫秒。支持 mp3、wav、ogg 等常见格式。

**用法**：
```bash
python trim_audio_silence.py <输入音频> <输出音频> [--lifetime N] [--pre_roll N] [--post_roll N] [--silence_thresh dBFS] [--min_silence_len MS]
```

**参数**：
- `input` - 必需，输入音频文件路径
- `output` - 必需，输出音频文件路径（格式由扩展名决定，如 .mp3 / .wav）
- `--lifetime` - 可选，只保留有声音开始后的前 N 毫秒
- `--pre_roll` - 可选，有声音前保留多少毫秒（默认 30）
- `--post_roll` - 可选，有声音后保留多少毫秒（默认 50）
- `--silence_thresh` - 可选，静音阈值 dBFS，低于此视为静音（默认 -40）
- `--min_silence_len` - 可选，判定静音的最小连续长度 毫秒（默认 20）

**说明**：
- 通过静音检测找到第一段和最后一段有声音的区间，去掉前后静音
- `pre_roll` / `post_roll` 用于在有声音前后多保留一点，避免截断开头或结尾
- `--lifetime` 适合裁剪长录音，只保留前 N 毫秒有效内容
- 若提示「未检测到有效声音」，可尝试调低 `--silence_thresh` 或调小 `--min_silence_len`

**依赖**：
- Python 3.6+
- pydub：`pip install pydub`
- 系统需安装 ffmpeg（pydub 用于解码/编码多种格式）

**示例**：
```bash
# 去首尾静音，输出格式由扩展名决定
python trim_audio_silence.py input.mp3 output.mp3
python trim_audio_silence.py rec.wav out.wav

# 只保留有声音开始后的前 5 秒
python trim_audio_silence.py rec.wav short.wav --lifetime 5000

# 调整前后过渡区与静音判定
python trim_audio_silence.py rec.mp3 short.mp3 --pre_roll 50 --post_roll 80
python trim_audio_silence.py rec.mp3 out.mp3 --silence_thresh -35 --min_silence_len 30
```

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
pip install pydub edge-tts tqdm openai-whisper kafka-python Pillow fpdf2
```

### 系统工具依赖

- **ffmpeg / ffplay**：用于音频处理（play_audio.py, txt2voice.py, voice2txt.py, mix_sound.py, change_sound_volume.py, trim_audio_silence.py）
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
- `clean_docker.sh` - 需要root权限（关闭 Docker 进程与系统服务）

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
| 系统管理 | add_swap.sh, add_user_to_dev_group.sh, space-manager.sh, startup.sh, clean_docker.sh |
| 容器部署 | aws_jenkins_deployee_run_fe.sh |
| Git工具 | clean_worktree_interactive.sh, list_git_modifying_branches, gen_patch.sh, git_nearest_direct_child_commit.sh, git_user_stats.sh |
| Laravel工具 | laravel_diagnose.php |
| Python工具 | pip_pkg_size.sh, png_info.py, png_cutout.py, png2jpg.py, jpg2png.py, md2pdf.py, djvu2pdf.py, image_filter.py, ios_screenshot_resize.py, font_preview.py |
| 数据处理 | filter_row_with_blank_field.sh, map_host_port_and_index_by_uri.sh, parse_uri_ip_and_write_cache.sh |
| API管理 | refresh_api_gateway_token.sh |
| 音视频 | play_audio.py, txt2voice.py, voice2txt.py, wav2mp3.py, mix_sound.py, change_sound_volume.py, pick_sound.py, filter_sound.py, trim_audio_silence.py |
| 网络服务 | debug_server.py, send_kafka_template.py, simple_server.py |

### 按语言分类

| 语言 | 脚本数量 | 脚本列表 |
|-----|---------|---------|
| Bash | 16 | add_swap.sh, add_user_to_dev_group.sh, aws_jenkins_deployee_run_fe.sh, clean_worktree_interactive.sh, clean_docker.sh, list_git_modifying_branches, filter_row_with_blank_field.sh, gen_patch.sh, git_nearest_direct_child_commit.sh, git_user_stats.sh, map_host_port_and_index_by_uri.sh, parse_uri_ip_and_write_cache.sh, pip_pkg_size.sh, refresh_api_gateway_token.sh, space-manager.sh, startup.sh |
| Python | 21 | change_sound_volume.py, debug_server.py, djvu2pdf.py, filter_sound.py, font_preview.py, image_filter.py, ios_screenshot_resize.py, jpg2png.py, md2pdf.py, mix_sound.py, pick_sound.py, play_audio.py, png2jpg.py, png_cutout.py, png_info.py, send_kafka_template.py, simple_server.py, trim_audio_silence.py, txt2voice.py, voice2txt.py, wav2mp3.py |
| PHP | 1 | laravel_diagnose.php |

---

## 更新日志
s

---

## 贡献

如有问题或建议，请直接修改脚本或联系维护者。

---

## 许可证

本脚本工具集为内部使用工具，请根据实际需求使用。

