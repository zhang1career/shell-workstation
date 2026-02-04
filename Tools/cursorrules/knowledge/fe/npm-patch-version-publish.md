# npm patch 版本升级和发布

## 功能概述

`npm run patch` 是一个自动化工具，用于升级 Monorepo 中包的 patch 版本号并发布到 GitHub Packages。

## 底层机制

### 执行流程（两步）

1. **升级版本号** (`patch-version.sh`)
   - 检查 Git 工作区是否干净（必须无未提交更改）
   - 使用 `npm version patch` 升级所有子包或指定子包的 patch 版本
   - 使用 `--no-git-tag-version` 避免自动创建 tag
   - 手动创建统一的 git commit 和 tag（格式：`包名@版本号`）

2. **发布包** (`publish.sh`)
   - 检查 `GITHUB_TOKEN` 环境变量（从 `.env` 文件或环境变量读取）
   - 使用 `npm publish --registry=https://npm.pkg.github.com` 发布到 GitHub Packages
   - 支持发布所有包、根包或指定子包

### 关键技术点

- **版本管理**：使用 `npm version patch` 自动递增 patch 版本（如 `0.1.0` → `0.1.1`）
- **Git 集成**：自动创建 commit 和 tag，确保版本变更可追溯
- **Monorepo 支持**：使用 `--workspace` 参数支持单独升级/发布指定子包
- **发布目标**：发布到 GitHub Packages（`npm.pkg.github.com`）

## 使用场景

- 修复 bug 后的版本发布
- 需要快速发布 patch 版本更新
- Monorepo 中多个包的批量版本升级和发布

## 使用方式

```bash
# 升级并发布所有子包
npm run patch

# 升级并发布指定的子包
npm run patch -- --workspace core
npm run patch -- --workspace core audio ui

# 列出所有可升级的包
npm run patch -- --list
```

## 前置条件

- Git 工作区必须干净（无未提交更改）
- 需要配置 `GITHUB_TOKEN` 环境变量（用于发布到 GitHub Packages）
- 需要配置 npm registry 认证（`npm login --registry=https://npm.pkg.github.com`）
