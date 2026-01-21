# iOS Podfile 中使用 Native 环境变量的方法

## 概述

在 React Native iOS 项目中，Podfile 是 Ruby 脚本，默认只能访问系统环境变量。要让 Podfile 能够读取项目根目录下的 `.env` 文件，需要手动加载该文件。

## 问题背景

- Podfile 是 Ruby 脚本，`ENV` 是 Ruby 的环境变量哈希
- `.env` 文件不会自动加载到 Ruby 的 `ENV` 中
- `react-native-config` 主要用于 JS 和原生代码，不会让 Podfile 直接读取 `.env`

## 解决方案

在 Podfile 中添加 `load_dotenv` 函数，在执行时自动读取 `.env` 文件。

## 实现步骤

### 1. 在 Podfile 中添加加载函数

在 Podfile 顶部（在 `source` 之后，其他配置之前）添加以下代码：

```ruby
# Load native .env to ENV
def load_dotenv
  env_file = File.join(__dir__, '..', '.env')
  if File.exist?(env_file)
    File.foreach(env_file) do |line|
      line.strip!
      next if line.empty? || line.start_with?('#')
      key, value = line.split('=', 2)
      next unless key && value
      # 移除引号（如果有）
      value = value.gsub(/^["']|["']$/, '')
      ENV[key.strip] = value.strip unless ENV[key.strip]
    end
  end
end

# preload .env before using ENV variables
load_dotenv
```

### 2. 在 Podfile 中使用环境变量

加载 `.env` 后，可以在 Podfile 中通过 `ENV['VARIABLE_NAME']` 访问环境变量：

```ruby
# 示例：根据环境变量配置 Flipper
flipper_config = ENV['NO_FLIPPER'] == "1" ? FlipperConfiguration.disabled : FlipperConfiguration.enabled

# 示例：根据环境变量配置框架链接方式
linkage = ENV['USE_FRAMEWORKS']
if linkage != nil
  Pod::UI.puts "Configuring Pod with #{linkage}ally linked Frameworks".green
  use_frameworks! :linkage => linkage.to_sym
end
```

### 3. 在 .env 文件中定义变量

在项目根目录（`apps/native/.env`）中定义变量：

```env
NO_FLIPPER=1
USE_FRAMEWORKS=static
```

## 完整示例

```ruby
source 'https://cdn.cocoapods.org/'

# Load native .env to ENV
def load_dotenv
  env_file = File.join(__dir__, '..', '.env')
  if File.exist?(env_file)
    File.foreach(env_file) do |line|
      line.strip!
      next if line.empty? || line.start_with?('#')
      key, value = line.split('=', 2)
      next unless key && value
      value = value.gsub(/^["']|["']$/, '')
      ENV[key.strip] = value.strip unless ENV[key.strip]
    end
  end
end

# preload .env before using ENV variables
load_dotenv

# 使用环境变量
flipper_config = ENV['NO_FLIPPER'] == "1" ? FlipperConfiguration.disabled : FlipperConfiguration.enabled

platform :ios, min_ios_version_supported
prepare_react_native_project!

target 'YourApp' do
  use_react_native!(
    :flipper_configuration => flipper_config,
    # ... 其他配置
  )
end
```

## 工作原理

1. `load_dotenv` 函数查找 `apps/native/.env` 文件（相对于 `ios/` 目录）
2. 逐行解析文件，跳过注释和空行
3. 解析 `KEY=VALUE` 格式，移除引号
4. 将变量加载到 Ruby 的 `ENV` 哈希中（如果系统环境变量已存在，则不会覆盖）

## 注意事项

1. **优先级**：如果系统环境变量中已经存在同名变量，系统环境变量会优先（不会被 `.env` 覆盖）
2. **修改后需要重新运行**：修改 `.env` 文件后，需要重新运行 `pod install` 才能生效
3. **文件路径**：`.env` 文件应该在项目根目录（`apps/native/.env`），不是 `ios/` 目录
4. **格式要求**：`.env` 文件中的变量格式应该是 `KEY=VALUE`，支持带引号的值
5. **不需要添加到 Xcode**：`.env` 文件不需要添加到 Xcode 项目中，Podfile 通过文件系统直接读取

## 使用场景

- 根据环境变量控制 Flipper 的启用/禁用
- 根据环境变量配置框架链接方式（static/dynamic）
- 根据环境变量选择不同的依赖版本
- 根据环境变量配置其他构建选项

## 故障排查

### 问题：Podfile 无法读取 `.env` 文件

1. 确认 `.env` 文件在正确的位置：`apps/native/.env`（相对于 `ios/Podfile`）
2. 检查文件路径：`File.join(__dir__, '..', '.env')` 会解析为 `ios/../.env` = `apps/native/.env`
3. 确认文件存在且可读

### 问题：环境变量值不正确

1. 检查 `.env` 文件格式是否正确（`KEY=VALUE`）
2. 确认没有多余的空格
3. 如果值包含引号，函数会自动移除

### 问题：系统环境变量覆盖了 `.env` 中的值

这是预期行为：系统环境变量优先级更高。如果需要使用 `.env` 中的值，确保系统环境变量中没有同名变量。

## 参考

- [React Native Podfile 文档](https://github.com/facebook/react-native/blob/main/packages/react-native/scripts/react_native_pods.rb)
- [Ruby ENV 文档](https://ruby-doc.org/core-3.0.0/ENV.html)
