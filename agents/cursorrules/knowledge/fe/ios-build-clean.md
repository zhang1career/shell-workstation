# iOS 构建清理工具

## 功能概述

`npm run clean:ios` 是一个完整的 iOS 构建缓存清理工具，用于解决构建失败、编译错误、依赖问题等缓存相关的构建问题。

## 底层机制

### 清理流程（六步）

1. **关闭 Xcode 进程** (`kill-xcode.sh`)
   - 强制关闭所有 Xcode 相关进程
   - 释放文件锁，避免清理时文件被占用

2. **清理 DerivedData** (`clean-derived-data.sh`)
   - 删除 `~/Library/Developer/Xcode/DerivedData/` 下的项目数据
   - 清理编译产物、索引、模块缓存

3. **清理构建文件夹** (`clean-build.sh`)
   - 删除项目本地的 `ios/build/` 目录
   - 清理所有构建临时文件

4. **清理 Pods** (`clean-pods.sh`)
   - 删除 `Pods/` 目录和 `Podfile.lock`
   - **注意**：不自动重新安装，需要手动执行 `pod install`

5. **清理 Xcode 模块缓存**
   - 删除 `~/Library/Caches/com.apple.dt.Xcode/` 下的所有缓存
   - 清理 Xcode 内部模块缓存

6. **清理 Swift Package Manager 缓存**
   - 删除 `~/Library/Caches/org.swift.swiftpm/`
   - 解决 PIF (Project Interchange Format) 相关问题

## 适用场景

- **构建失败**：编译错误、链接错误
- **PIF 错误**：`unable to initiate PIF transfer session`
- **依赖图错误**：`Could not compute dependency graph`
- **缓存问题**：构建服务相关的缓存问题
- **Xcode 异常**：Xcode 行为异常，需要彻底清理

## 清理后的操作

1. 重新安装 Pods：`cd ios && pod install`
2. 重新打开 Xcode
3. 在 Xcode 中执行 `Product → Clean Build Folder` (Shift+Cmd+K)
4. 重新构建项目：`Product → Build` (Cmd+B)

## 注意事项

- 清理 Pods 后需要重新安装依赖
- 清理 DerivedData 会删除所有项目的编译缓存（影响所有 Xcode 项目）
- 如果问题仍然存在，可能是代码签名配置问题，而非缓存问题
