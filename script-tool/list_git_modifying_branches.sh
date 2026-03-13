#!/bin/bash
#
# list_git_modifying_branches.sh - 列出给定文件曾被修改过的本地分支
#
# 用法: ./list_git_modifying_branches <file-path>
#
# 说明:
#   遍历所有本地分支，检查指定文件是否在该分支的历史中被修改过。
#   若有修改，则输出分支名及该分支上对该文件的最近 3 次提交摘要。
#
# 依赖: bash, git
#
# 示例:
#   ./list_git_modifying_branches README.md
#   ./list_git_modifying_branches src/main.py
#

FILE=$1

if [ -z "$FILE" ]; then
  echo "Usage: $0 <file-path>"
  echo ""
  echo "列出给定文件曾被修改过的本地分支。"
  echo "每个有修改的分支会显示最近 3 次相关提交。"
  exit 1
fi

# 禁用 Git 分页器，避免多行输出时需要多次按 q 退出
export GIT_PAGER=cat

echo "Checking branches for modifications of: $FILE"
echo

for branch in $(git for-each-ref --format='%(refname:short)' refs/heads/)
do
    commits=$(git log $branch --pretty=oneline -- $FILE)

    if [ ! -z "$commits" ]; then
        echo "Branch: $branch"
        git log $branch --pretty=format:"  %h %ad %s" --date=short -n 3 -- $FILE
        echo
    fi
done
