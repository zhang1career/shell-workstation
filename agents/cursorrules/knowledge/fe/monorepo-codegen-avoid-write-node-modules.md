# Monorepo 下避免将代码生成写入 node_modules

## 概述

在 Monorepo 或某些 CI/权限环境下，直接向 `node_modules` 目录**写入**文件（如代码生成脚本输出到 `node_modules/react-native-config/.../GeneratedDotEnv.m`）可能触发 **EPERM (Operation not permitted)**，导致 `PhaseScriptExecution` 失败。代码生成等输出应优先写到可写目录（如 `ios/build`），再在工程中引用。

## 可复用经验

### 1. 问题表现

- 某 Run Script（如 `[CP-User] Config codegen`）将生成文件写到 `node_modules/...`。
- 构建时报 **EPERM** 或 **PhaseScriptExecution failed**，且与写文件相关。

### 2. 处理方式

- **改写输出目录**：将代码生成脚本的输出目录从 `node_modules/...` 改为 **`ios/build/...`**（或其它可写的构建目录），例如：
  - `ios/build/generated-dotenv/GeneratedDotEnv.m`
- **修改脚本**：在 Podfile `post_install` 中覆盖该 Script Phase 的脚本，令其调用生成逻辑时传入**新输出目录**；确保 `mkdir -p` 等在新目录下执行。
- **更新工程引用**：将 Target 的 Compile Sources（或其它 Build Phase）中对生成文件的引用，从 `node_modules` 路径改为 **新路径**（如 `../build/generated-dotenv/GeneratedDotEnv.m`）。
- **声明 output_paths**：为该 Script Phase 设置 `output_paths`，指向新路径，避免「Build input file cannot be found」类报错（见 [xcode-script-phase-output-paths-declare](./xcode-script-phase-output-paths-declare.md)）。

### 3. 原则

- **不向 `node_modules` 写入**：代码生成、构建中间产物等优先放到 `ios/build`、`DerivedData` 等可写目录。
- **生成物路径与工程引用一致**：脚本输出路径、`output_paths`、Compile Sources 引用三者保持一致。

## 相关文档

- [xcode-script-phase-output-paths-declare](./xcode-script-phase-output-paths-declare.md)
