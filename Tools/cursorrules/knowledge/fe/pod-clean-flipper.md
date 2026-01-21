# Pod 关闭 Flipper 的方法

## 概述

在 React Native iOS 项目中关闭 Flipper 需要三个步骤，通过环境变量统一控制，确保 Podfile 和 React Native CLI 都能正确识别并排除 Flipper 相关依赖。

## 配置方法

### 第一步：在环境变量文件中添加配置

在 native 的环境变量文件（`apps/native/.env`）中，添加：

```env
NO_FLIPPER=1
```

**说明：**
- 如果 `.env` 文件不存在，可以从 `.env.example` 复制：`cp .env.example .env`
- 确保 `.env` 文件在 `apps/native/` 目录下（不是 `ios/` 目录）
- `.env` 文件不应提交到版本控制（已在 `.gitignore` 中）

### 第二步：在 iOS Podfile 中使用 Native 环境变量

确保 Podfile 能够读取 `.env` 文件中的环境变量。参考 [pod-load-env.md](./pod-load-env.md) 进行配置。

**Podfile 中使用环境变量：**

```ruby
flipper_config = ENV['NO_FLIPPER'] == "1" ? FlipperConfiguration.disabled : FlipperConfiguration.enabled

use_react_native!(
  :flipper_configuration => flipper_config,
  # ... 其他配置
)
```

### 第三步：在 react-native.config.js 中排除依赖

在 native 的配置文件（`apps/native/react-native.config.js`）中，添加配置以排除 `react-native-flipper`：

```javascript
module.exports = {
  dependencies: {
    // 根据环境变量排除 react-native-flipper
    // 当设置 NO_FLIPPER=1 时，会排除 iOS 平台的 react-native-flipper
    ...(process.env.NO_FLIPPER === '1'
      ? { 'react-native-flipper': { platforms: { ios: null } } }
      : {}),
  },
};
```

**说明：**
- `react-native.config.js` 文件应放在 `apps/native/` 目录下（与 `package.json` 同级）
- 这个配置告诉 React Native CLI 在链接依赖时排除 `react-native-flipper`
- `platforms: { ios: null }` 表示在 iOS 平台上排除该依赖

## 完整工作流程

### 1. 配置环境变量

```bash
# 编辑 .env 文件
cd apps/native
echo "NO_FLIPPER=1" >> .env
```

### 2. 验证 Podfile 配置

确保 `ios/Podfile` 中包含 `load_dotenv` 函数，并且使用了 `ENV['NO_FLIPPER']`。

### 3. 配置 react-native.config.js

确保 `apps/native/react-native.config.js` 中包含排除 Flipper 的配置。

### 4. 重新安装依赖，验证 Flipper 已关闭
参考 [Flipper 检测与彻底清理流程](./pod-check-flipper-cleaned.md)


## 为什么需要三步？

### 第一步：环境变量文件
- 提供统一的配置入口
- 方便不同环境使用不同配置
- 避免硬编码

### 第二步：Podfile 配置
- Podfile 需要读取环境变量来决定是否启用 Flipper
- 通过 `FlipperConfiguration.disabled` 禁用 Flipper 功能

### 第三步：react-native.config.js 配置
- React Native CLI 在自动链接依赖时需要知道排除哪些包
- 防止 `react-native-flipper` 被自动链接到项目中
- 避免构建时出现依赖冲突

## 故障排查

### 问题 1：环境变量未生效

**检查项：**
1. 确认 `.env` 文件在正确位置：`apps/native/.env`
2. 确认 Podfile 中的 `load_dotenv` 函数路径正确
3. 确认 `react-native.config.js` 中读取的是 `process.env.NO_FLIPPER`

## 参考文档

- [Podfile 中使用 Native 环境变量](./pod-load-env.md)
- [Flipper 检测与彻底清理流程](./pod-check-flipper-cleaned.md)
- [React Native 配置文件文档](https://github.com/react-native-community/cli/blob/main/docs/configuration.md)
- [CocoaPods 官方文档](https://guides.cocoapods.org/)
