# Xcode 脚本阶段生成物作为编译输入时的 output_paths 声明

## 概述

若某 Run Script 阶段**生成的文件**被当作**编译输入**（例如生成 `.m` 供后续 Compile Sources 使用），必须在对应 Script Phase 的 **`output_paths`** 中声明这些输出路径。否则 Xcode 可能报 **「Build input file cannot be found」** 或 **「Did you forget to declare this file as an output of a script phase or custom build rule which produces it?」**。

## 可复用经验

### 1. 何时需要声明

- Script Phase 会**产出**文件（如代码生成）。
- 该产出被添加到 Target 的 **Compile Sources** 或其他 Build Phase 作为输入。
- 产出路径在构建过程中才生成（非一开始就存在于工程目录）。

满足以上时，必须为该 Script Phase 设置 **`output_paths`**，让 Xcode 知道这些文件由该阶段产生，从而正确安排构建顺序与增量构建。

### 2. 如何声明

- 在 **Podfile 的 `post_install`** 中，若通过脚本修改了某 Pod 的 Config codegen 等 Script Phase，可同时设置 `phase.output_paths`（若该 phase 对象支持）：

  ```ruby
  phase.output_paths = [
    '$BUILD_DIR/GeneratedInfoPlistDotEnv.h',
    '$PODS_ROOT/../build/generated-dotenv/GeneratedDotEnv.m'
  ] if phase.respond_to?(:output_paths=)
  ```

- 使用 Xcode 构建变量（如 `$BUILD_DIR`、`$PODS_ROOT`）与脚本实际输出路径保持一致。

### 3. 编译源引用路径

- 若脚本**改写了**生成物目录（例如从 `node_modules/...` 改到 `ios/build/generated-dotenv/`），需要同步修改 Target 的 **Compile Sources**：移除对旧路径的引用，添加对**新路径**的引用（如 `../build/generated-dotenv/GeneratedDotEnv.m`）。

### 4. 配合 pod install 预生成

- 若 Clean 或首次构建前该文件不存在，仍可能触发「Build input file cannot be found」。
- 可在 **`pod install` 的 `post_install`** 中，用同一套生成逻辑**预生成**到相同目录，确保文件在首次构建前就存在。

## 总结

**脚本产出即编译输入** → 必须在 Script Phase 的 **`output_paths`** 中声明；并保证 Compile Sources 引用的是实际输出路径；必要时在 `pod install` 时预生成。
