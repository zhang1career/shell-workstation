# iOS 构建诊断工具

## 功能概述

`npm run diagnose:ios` 是一个自动化的 iOS 构建问题诊断工具，通过分步骤检查来定位构建失败的根本原因。

## 底层机制

### 诊断流程（三步）

1. **被动检查失败的 Phase** (`check-failed-phase.sh`)
   - 读取 `/tmp/echo-last-phase.txt`（由构建脚本记录）
   - 识别最后执行的 Phase，通常是失败的那个
   - 针对常见失败 Phase 提供具体排查建议

2. **主动诊断 Build Phases** (`run-build-phases-diagnostic.sh`)
   - 依次执行所有自定义 Build Phase 脚本
   - 检查 `BuildXCConfig`（生成 `tmp.xcconfig`）
   - 检查 `Update Launch Screen`（更新启动屏）
   - 检查 `Config codegen`（生成环境变量配置）
   - 在独立环境中运行，避免 Xcode 构建上下文干扰

3. **专项诊断 Bundle Phase** (`run-bundle-phase-diagnostic.sh`)
   - 检查 React Native Bundle 阶段
   - 验证 Node.js 环境、Metro 配置
   - 检查 `.xcode.env` 和 `.xcode.env.local` 配置

### 诊断结果

- **统计信息**：通过的步骤数、失败的步骤数
- **失败定位**：明确指出哪个 Phase 失败
- **修复建议**：针对不同失败类型提供具体解决方案

## 使用场景

- Xcode 构建失败但错误信息不明确
- PhaseScriptExecution 错误
- 需要快速定位构建问题
- 验证构建环境配置是否正确

## 常见问题诊断

- **Bundle Phase 失败**：检查 Node.js 路径、Metro 配置
- **BuildXCConfig 失败**：检查 `.env` 文件和 `react-native-config`
- **Config codegen 失败**：检查 `build/generated-dotenv` 目录权限
