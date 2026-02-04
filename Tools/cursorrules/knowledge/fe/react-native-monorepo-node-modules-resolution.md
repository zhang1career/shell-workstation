# Monorepo 下 React Native 的 node_modules 解析与 Metro 包解析

## 概述

在 Monorepo 中，依赖常被 hoist 到根目录 `node_modules`，而 CocoaPods、Metro 的默认解析路径可能仍指向 app 目录（如 `apps/native/node_modules`）。若解析路径与**实际** `node_modules` 位置不一致，会触发「找不到文件」、CocoaPods 报错、或 Metro bundle 时解析到错误版本的包（如根目录的 `react-native` 含 Flow 语法导致 Babel "Missing semicolon"）。需对 CocoaPods、Metro 做显式绑定或优先规则配置。

## 可复用经验

### 1. CocoaPods / 原生侧

- **Hoisting**：某包若被提升到根 `node_modules`，而 CocoaPods 在 `apps/native/node_modules` 查找，会报错（如 `PrivacyInfo.xcprivacy` 找不到）。
- **处理**：
  - 在 `react-native.config.js` 的 `dependencies` 中**排除**该包的 autolinking（如 `platforms: { ios: null }`）。
  - 在 Podfile 中通过 `:path` **显式指定**根目录路径，例如：
    ```ruby
    pod 'AsyncStorage', :path => '../../../node_modules/@react-native-async-storage/async-storage'
    ```
- **原则**：CocoaPods 的解析路径要与实际 `node_modules` 位置一致；必要时用 `:path` 做显式绑定。

### 2. Metro / JS 侧

- **根与 app 的 node_modules 并存**：Monorepo 中常同时存在根 `node_modules` 与 `apps/native/node_modules`。Metro 默认解析可能走到根目录，例如解析到根目录的 `react-native`，其 `index.js` 含 Flow 语法（如 `} as ReactNativePublicAPI`），Babel 无法解析，报 "Missing semicolon"，导致 **Bundle React Native** 阶段失败。
- **处理**：在 `metro.config.js` 的 `resolver.resolveRequest` 中，对 **`react`** 与 **`react-native`** 等关键包**强制**从 `apps/native/node_modules` 解析，避免解析到根目录。可配合 `extraNodeModules` 将 `react` / `react-native` 指向 app 的 `node_modules`。
- **原则**：根与 app 的 `node_modules` 并存时，对关键包在 `resolveRequest` 里写死从 app 的 `node_modules` 解析，避免解析到根目录的错误版本。

## 相关文档

- [react-native-config 与 Build Phases](https://github.com/lugg/react-native-config)
- [Metro 配置](https://facebook.github.io/metro/docs/configuration)
- [React Native Monorepo 指南](https://reactnative.dev/docs/monorepo)
