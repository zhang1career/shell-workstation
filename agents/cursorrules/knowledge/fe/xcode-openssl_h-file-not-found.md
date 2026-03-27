# Flipper-Folly / OpenSSL.h file not found

## 问题解决方案总结

### 一、问题本质（Root Cause）

`Flipper-Folly / OpenSSL.h file not found` 并不是 OpenSSL 本身缺失，而是：

- Flipper（Flipper-Folly）仍被 CocoaPods 引入并参与编译
- 但 Flipper 依赖的 OpenSSL 头文件在当前 macOS / Xcode 环境中不可用或不兼容

在 React Native iOS 项目中，即使表面上"关闭了 Flipper"，由于：

- React Native 新版的隐式启用机制
- CocoaPods 的 Pods / 锁文件 / Xcode 工程残留
- Xcode 的 DerivedData 缓存

导致 Flipper-Folly 仍被编译，从而触发该错误。

### 二、推荐解决思路（结论）

**不要修 OpenSSL，而是彻底移除 Flipper**

- Flipper 对 Release / Archive / 上架无任何必要性
- 这是最稳定、最符合生产环境的做法

### 三、标准解决方案（可落地）

参考 [Pod 关闭 Flipper 的方法](./pod-clean-flipper.md)

并使用 `.xcworkspace` 打开工程重新构建。

### 四、成功判定标准

问题被认为已解决，必须同时满足：

1. **Pods 目录中不存在任何 Flipper-***  
   参考 [Flipper 检测与彻底清理流程](./pod-check-flipper-cleaned.md)。（这在"Pod 关闭 Flipper 的方法"中可能已经被调用过了）。

2. **Xcode 构建日志中不再出现 Flipper-Folly**

3. **不再报 openssl/opensslv.h file not found**

### 五、为什么不推荐"修 OpenSSL"

- Flipper 依赖 OpenSSL 1.1（已过时）
- macOS / Homebrew 默认已切换至 OpenSSL 3
- 手动注入 OpenSSL 路径：
  - 复杂
  - 易碎
  - 对发布无价值
- 关闭 Flipper 是根治方案，而不是权宜之计

### 六、总结

看到 `Flipper-Folly / OpenSSL.h file not found`，不要装 OpenSSL，先把 Flipper 从 Pods 里清干净。
