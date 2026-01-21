# Flipper 检测与彻底清理流程

### 背景

在 React Native iOS 项目中，即使在 Podfile 中配置关闭 Flipper，由于 CocoaPods 缓存、Pods 工程残留或 RN 新版启用机制，Flipper-Folly 仍可能被编译，从而引发典型错误：

**Flipper-Folly / OpenSSL.h file not found**

因此需要一套可验证、可重复的清理流程。

### 一、Flipper 是否仍被启用（检测）

```bash
ls Pods | grep Flipper
```

#### 结果判定

- ✅ **无输出**：Flipper 已彻底移除

- ❌ **有输出**（如 Flipper-Folly / FlipperKit）：Flipper 仍在生效

> **只要 Pods 目录中存在 Flipper-*，Xcode 构建阶段就一定会继续编译 Flipper**

### 二、Flipper 的标准清理流程（必须整体执行）

```bash
cd apps/native/ios

# 1. 删除 Pods 及锁文件（清除历史解析结果）
rm -rf Pods Podfile.lock

# 2. 从 Xcode 工程中移除 Pods 集成信息
pod deintegrate

# 3. 重新解析并安装 Pods（基于当前 Podfile）
pod install

# 4. 再次检测 Flipper 是否被引入
ls Pods | grep Flipper
```

#### 核心原则

- **Podfile 的修改只对"下一次 pod install"生效**
- **不删除 Pods / Podfile.lock = 旧的 Flipper Target 仍会存在**
- **pod deintegrate 用于清理 Xcode 工程级残留（很多问题来自这里）**

### 三、Xcode 构建缓存清理（必须配合）

```bash
space-manager.sh clean ~/Library/Developer/Xcode/DerivedData
```
（其中，脚本 space-manager.sh 的完整路径为：~/script-tool/space-manager.sh）

#### 作用

- 清除 Xcode 已缓存的 Pods 编译产物
- 避免已删除的 Flipper 目标仍被旧缓存引用

### 四、完整成功判定标准（Checklist）

在重新打开 Xcode 并构建前，必须满足：

1. ✅ `ls Pods | grep Flipper` 无任何输出

2. ✅ 使用 `.xcworkspace` 打开工程

3. ✅ 已清理 DerivedData

4. ✅ Xcode 构建日志中不再出现 Flipper-Folly

### 五、关键结论（经验总结）

- **Flipper 是否真的被关闭，不看 Podfile 配置，而看 Pods 目录结果**
- **配置 ≠ 生效**
- **Pods 结果才是唯一事实**
- **`ls Pods | grep Flipper` 是最快、最可靠的判断方式**
