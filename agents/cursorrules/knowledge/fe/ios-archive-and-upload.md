# iOS 打包和上传流程

## 功能概述

`npm run archive-and-upload:ios` 是一个完整的 iOS 应用打包和上传流程，自动执行清理、预处理、打包、导出和上传到 App Store Connect。

## 底层机制

### 执行流程

1. **清理构建产物** (`xcode-clean.sh`)
   - 使用 `xcodebuild clean` 清理 Debug 和 Release 配置
   - 清理 Xcode 构建缓存

2. **构建前预处理** (`prebuild.sh`)
   - 同步版本号：从 `.env` 读取版本信息并更新到 `Info.plist`
   - 生成构建号：自动递增构建号

3. **打包 Archive** (`xcode-archive.sh`)
   - 使用 `xcodebuild archive` 命令打包
   - 生成 `.xcarchive` 文件到 `~/Library/Developer/Xcode/Archives/`
   - 支持自动代码签名和 Provisioning Profile 更新

4. **导出和上传** (`xcode-upload.sh`)
   - 从 `.xcarchive` 导出 `.ipa` 文件
   - 自动生成 `ExportOptions.plist`（从 Archive 中提取签名信息）
   - 上传到 App Store Connect（使用 `xcrun altool`）

### 关键技术点

- **代码签名自动化**：从 Archive 中提取 Team ID、Provisioning Profile UUID
- **凭据管理**：支持环境变量、`.env.local` 文件、交互式输入三种方式
- **错误处理**：提供详细的错误诊断和修复建议

## 使用场景

- 发布前完整打包流程
- CI/CD 自动化构建和上传
- 需要一次性完成清理、打包、上传的场景

## 注意事项

- 需要配置代码签名（Xcode → Signing & Capabilities → Team）
- 上传需要 Apple ID 和 App-Specific Password
- 确保 `.env` 文件包含正确的版本信息
