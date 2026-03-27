# React Native 添加环境变量文件的方法

## 概述

在 React Native 项目中添加环境变量支持，可以使用 `react-native-config` 库，它支持在 iOS、Android 和 JavaScript 代码中访问环境变量。

## 安装依赖

```bash
cd apps/native
npm install react-native-config
```

## 配置步骤

### 1. 创建环境变量文件

在 React Native 项目根目录（`apps/native/`）创建 `.env` 文件：

```bash
cp .env.example .env
```

`.env` 文件格式示例：

```env
# API 配置
API_BASE_URL=https://api.example.com
API_TIMEOUT=30000

# 功能开关
ENABLE_DEBUG_MODE=false
ENABLE_ANALYTICS=true

# 第三方服务
SENTRY_DSN=
FIREBASE_API_KEY=

# 应用配置
APP_ENV=development
APP_VERSION=1.0.0
```

### 2. 配置 .gitignore

确保 `.env` 文件不会被提交到版本控制：

```gitignore
# Environment variables
.env
.env.local
.env.*.local
```

同时提交 `.env.example` 作为模板。

### 3. iOS 配置

#### 3.1 安装 CocoaPods 依赖

```bash
cd ios
pod install
cd ..
```

#### 3.2 配置 Xcode Build Phase

`react-native-config` 会在 `pod install` 时自动添加 Build Phase 脚本。如果自动添加失败，可以手动添加：

1. 打开 `ios/YourApp.xcworkspace`（注意是 `.xcworkspace`，不是 `.xcodeproj`）
2. 选择项目 → Target → Build Phases
3. 点击 `+` → New Run Script Phase
4. 将脚本放在 `[CP] Copy Pods Resources` 之前
5. 添加脚本：

```bash
set -e

# 读取 .env 文件并生成 .xcconfig
"${SRCROOT}/../node_modules/react-native-config/ios/ReactNativeConfig/BuildXCConfig.rb" "${SRCROOT}/.." "${SRCROOT}/tmp.xcconfig"
```

6. 在 `Input Files` 中添加：
   - `${SRCROOT}/../.env`

### 4. Android 配置

Android 配置通常由 `react-native-config` 自动处理，运行 `pod install` 后即可使用。

## 在代码中使用环境变量

### JavaScript/TypeScript 代码

```typescript
import Config from 'react-native-config';

const apiUrl = Config.API_BASE_URL;
const timeout = parseInt(Config.API_TIMEOUT || '30000', 10);
const debugMode = Config.ENABLE_DEBUG_MODE === 'true';
```

### iOS 原生代码 (Objective-C/Swift)

```objc
#import "ReactNativeConfig.h"

NSString *apiUrl = [ReactNativeConfig envFor:@"API_BASE_URL"];
```

### Android 原生代码 (Java/Kotlin)

```java
import com.lugg.ReactNativeConfig.ReactNativeConfig;

String apiUrl = ReactNativeConfigModule.envFor("API_BASE_URL");
```

## 环境变量文件优先级

1. `.env.development` / `.env.production`（根据构建配置）
2. `.env.local`（本地覆盖，不应提交）
3. `.env`（默认配置）

## 多环境配置

可以创建多个环境文件：

- `.env.development` - 开发环境
- `.env.staging` - 预发布环境
- `.env.production` - 生产环境

在构建时指定环境：

```bash
# iOS
ENVFILE=.env.production npm run ios

# Android
ENVFILE=.env.production npm run android
```

## 注意事项

1. **不要提交 `.env` 文件**：确保敏感信息不会被提交到版本控制
2. **使用 `.env.example`**：作为模板提交到版本控制，供团队成员参考
3. **变量命名**：环境变量名必须大写，使用下划线分隔（如 `API_BASE_URL`）
4. **值类型**：所有值都是字符串，需要在代码中转换类型
5. **重新构建**：修改 `.env` 文件后需要重新构建应用（`npm run ios` 或 `npm run android`）
6. **Xcode 项目**：不需要将 `.env` 文件添加到 Xcode 项目中，文件系统访问即可

## 故障排查

### 问题：环境变量在 iOS 中无法访问

1. 确认已运行 `pod install`
2. 确认 `.env` 文件在项目根目录下（`apps/native/`，不是 `ios/` 目录）
3. 清理构建：`cd ios && xcodebuild clean`
4. 重新构建：`npm run ios`

### 问题：修改 `.env` 后变量未更新

1. 停止 Metro bundler
2. 清理构建缓存
3. 重新运行应用

## 参考文档

- [react-native-config GitHub](https://github.com/lugg/react-native-config)
