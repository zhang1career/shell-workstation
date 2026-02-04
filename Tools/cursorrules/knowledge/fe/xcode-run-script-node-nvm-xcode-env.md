# Xcode Run Script 中 Node / nvm 找不到的配置方法

## 概述

Xcode 执行 Run Script 时**不是 login shell**，不会加载 `~/.zshrc`、`~/.bash_profile` 或 nvm，因此 `node`、`npm` 等可能找不到。React Native 的「Bundle React Native code and images」等阶段依赖 Node，需要显式配置 `NODE_BINARY`。可通过 `.xcode.env` / `.xcode.env.local` 配合 `with-environment.sh` 解决。

## 可复用经验

### 1. 使用 `.xcode.env` 与 `.xcode.env.local`

- **位置**：`apps/native/ios/` 下。
  - **`.xcode.env`**：版本化，团队共享。
  - **`.xcode.env.local`**：本地覆盖，不提交。
- **加载顺序**：先 `.xcode.env`，再 `.xcode.env.local`（若存在），后者覆盖前者。
- **用途**：设置 **`NODE_BINARY`**，确保 Xcode 能执行 `node`。

### 2. 典型配置

**.xcode.env**（使用 nvm 时先加载 nvm）：

```bash
if [ -s "$HOME/.nvm/nvm.sh" ]; then
  . "$HOME/.nvm/nvm.sh" --no-use
fi
export NODE_BINARY=$(command -v node)
```

**.xcode.env.local**（固定版本，避免机器差异）：

```bash
NVM_NODE="$HOME/.nvm/versions/node/v22.11.0/bin/node"
if [ -x "$NVM_NODE" ]; then
  export NODE_BINARY="$NVM_NODE"
else
  export NODE_BINARY=$(command -v node || echo "")
fi
```

### 3. `with-environment.sh` 的加载逻辑

React Native 的 Bundle 阶段通过 `with-environment.sh` 再执行 `react-native-xcode.sh`。该脚本会：

1. 默认 `NODE_BINARY=$(command -v node || echo "")`
2. 若存在 `$PODS_ROOT/../.xcode.env`，则 `source`
3. 若存在 `$PODS_ROOT/../.xcode.env.local`，再 `source`（覆盖）
4. 若 `NODE_BINARY` 仍为空，则回退到已废弃的 `find-node-for-xcode.sh`

因此，**真正生效的 `NODE_BINARY` 来自 .xcode.env / .xcode.env.local 的最终结果**。应在这两个文件中维护 `NODE_BINARY`，避免依赖废弃逻辑。

### 4. Bundle 阶段的预检

在调用 `with-environment.sh` 前，可先 `source` 上述 env 文件并检查 `NODE_BINARY` 已设置且可执行；否则直接报错退出，提示修复 `.xcode.env` / `.xcode.env.local`，例如：

```bash
[ -f "$ENV_PATH" ] && . "$ENV_PATH"
[ -f "$LOCAL_PATH" ] && . "$LOCAL_PATH"
if [ -z "$NODE_BINARY" ] || ! type "$NODE_BINARY" >/dev/null 2>&1; then
  echo "error: NODE_BINARY not set or not runnable. Fix .xcode.env / .xcode.env.local." >&2
  exit 1
fi
```

### 5. 本地验证

在 `apps/native/ios` 下：

```bash
source .xcode.env; source .xcode.env.local; "$NODE_BINARY" --version
```

应能正常输出 Node 版本（如 `v22.11.0`）。

## 参考

- [React Native 环境配置](https://reactnative.dev/docs/environment-setup#optional-configuring-your-environment)
- `node_modules/react-native/scripts/xcode/with-environment.sh`
