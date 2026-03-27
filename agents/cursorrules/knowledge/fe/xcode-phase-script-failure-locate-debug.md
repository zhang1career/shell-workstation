# Xcode PhaseScriptExecution 失败时如何定位与调试

## 概述

Xcode 报 `Command PhaseScriptExecution failed with a nonzero exit code` 时，通常只提示某 Run Script 失败，不指明具体是哪一个。通过注入阶段名、写标记文件、捕获 stderr，可快速定位失败阶段并拿到完整错误输出。

## 可复用经验

### 1. 定位失败阶段

- 在每个 Run Script 开头：
  - 使用 **`trap '...' ERR`**：脚本任一命令失败时执行 `trap`，便于统一打印阶段名并退出。
  - **`echo "[Phase] 阶段名"`**：在构建日志中显式标出当前阶段。
  - 将当前阶段名写入 **`/tmp/echo-last-phase.txt`**：构建结束后，用辅助脚本读该文件即可知道「最后一个执行的阶段」（通常即失败阶段）。

示例：

```bash
PN="Bundle React Native code and images"
echo "$PN" > /tmp/echo-last-phase.txt
echo "[Phase] $PN"
trap 'echo "FAILED: $PN" >&2; exit 1' ERR
set -e
# ... 实际脚本逻辑
```

### 2. 查看最后运行的阶段

在 `ios` 目录下运行：

```bash
./scripts/check-failed-phase.sh
```

或手动：

```bash
cat /tmp/echo-last-phase.txt
```

根据输出阶段名，在 Xcode Report Navigator (⌘9) 中展开对应 Run Script，查看完整输出。

### 3. Bundle React Native 阶段单独捕获 stderr

若失败阶段是 **「Bundle React Native code and images」**，可将该阶段的 stderr 重定向到文件，失败时再打印其末尾，例如：

```bash
# 重定向 bundle 命令的 stderr
/bin/sh -c "$WITH_ENVIRONMENT $REACT_NATIVE_XCODE" 2>/tmp/echo-bundle-err.txt || \
  { e=$?; [ -s /tmp/echo-bundle-err.txt ] && tail -80 /tmp/echo-bundle-err.txt >&2; exit $e; }
```

排查时：

```bash
cat /tmp/echo-bundle-err.txt
```

即可查看完整错误输出。

## 总结

- 用 **`trap` + 阶段名 + `/tmp/echo-last-phase.txt`** 定位失败阶段。
- 对 Bundle 阶段可额外将 stderr 写入 **`/tmp/echo-bundle-err.txt`**，便于排查 Metro / Node 相关错误。
