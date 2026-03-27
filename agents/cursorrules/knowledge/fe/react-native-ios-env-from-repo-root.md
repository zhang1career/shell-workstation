# React Native iOS 使用项目根路径 .env 的实践

## 概述

在 Monorepo 中，若希望用**项目根路径**（仓库根）的 `.env` 驱动 React Native iOS 端（`react-native-config`），需避免 Xcode 构建阶段路径推导错误导致部分变量在 iOS 上不生效。可通过「pod install 时用根目录 .env 覆盖 GeneratedDotEnv.m + 构建阶段不再覆盖」实现。

常规单项目、.env 在应用根（如 `apps/native/`）的用法见 [react-native-add-env-file.md](./react-native-add-env-file.md)。

## 问题背景

- `react-native-config` 在 Xcode 构建时通过 `[CP-User] Config codegen` 执行 `BuildDotenvConfig.rb`，读取 `.env` 并生成 `GeneratedDotEnv.m`。
- 该脚本接收的「根目录」由构建时的 `SRCROOT` 等推导；在 Pod 构建时 `SRCROOT` 可能指向 Pods 或 pod 路径，导致读错目录，**仓库根的 .env 未被使用**，JS/原生侧拿到的仍是默认或旧值。

## 实践做法

### 1. pod install 时用根目录 .env 生成并覆盖

在 Podfile 的 `post_install` 中：

- 使用 **monorepo 根目录**（如 `File.expand_path(File.join(__dir__, '..', '..', '..'))`，以 `__dir__` 为 `ios/` 为准）。
- 调用 `BuildDotenvConfig.rb`，传入根目录与**输出目录**，将输出目录设为 `node_modules/react-native-config/ios/ReactNativeConfig/`，直接覆盖其中的 `GeneratedDotEnv.m`。

这样，每次 `pod install` 都会用**根目录的 .env** 重新生成并写入该文件，iOS 编译时只会用到这一份。

### 2. 构建阶段不再覆盖（Config codegen 改为 no-op）

在 `post_install` 中，对 `react-native-config` 的 `[CP-User] Config codegen` 阶段：

- 将脚本改为仅输出提示后 `exit 0`，不再执行 `BuildDotenvConfig.rb`。
- 可选：将 `output_paths` 置空，避免 Xcode 期望产出文件。

这样构建时不再依赖 `SRCROOT` 推导路径，也不会覆盖 pod install 时写好的 `GeneratedDotEnv.m`。

### 3. 生效流程

1. 在 **monorepo 根目录** 维护 `.env`（如 `INTERACTION_MIN_RECORDING_DURATION_FOR_ECHO=2500`）。
2. 执行 `pod install`，触发上述覆盖逻辑。
3. 重新编译并运行 iOS 应用；JS 与原生通过 `Config` 读取到的值即来自根目录 .env。

修改根目录 `.env` 后需再次执行 `pod install` 再编译，否则 iOS 端不会更新。

## 与「不写 node_modules」的关系

本做法在 **pod install**（Ruby 进程）时写入 `node_modules/.../GeneratedDotEnv.m`，构建阶段不写，可避免构建时 EPERM。若需完全避免写 node_modules（如严格只读），可参考 [monorepo-codegen-avoid-write-node-modules.md](./monorepo-codegen-avoid-write-node-modules.md)，将输出改到 `ios/build/...` 并调整引用与 HEADER_SEARCH_PATHS。

## 故障排查

如何确认某环境变量是否在 iOS 端生效：检查 `node_modules/react-native-config/ios/ReactNativeConfig/GeneratedDotEnv.m` 是否包含该变量（格式为 `@"KEY":@"value"`）。可使用项目中的检测脚本：

```bash
# 在 apps/native 下
npm run check:ios:env -- VARIABLE_NAME
```

无参数时列出当前文件中出现的变量名或提示用法。

## 相关文档

- [react-native-add-env-file.md](./react-native-add-env-file.md)：常规 RN 项目 .env 配置（应用根目录）
- [pod-env-vs-react-native-env.md](./pod-env-vs-react-native-env.md)：Podfile 与 Build Phases 对 .env 的时机
- [monorepo-codegen-avoid-write-node-modules.md](./monorepo-codegen-avoid-write-node-modules.md)：避免向 node_modules 写入生成文件
