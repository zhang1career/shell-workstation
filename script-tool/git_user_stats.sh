#!/bin/bash
#
# 功能：显示Git仓库中用户的统计信息
# 用法：./git_user_stats.sh [git_log_options]
# 参数：
#   git_log_options - 可选，传递给git log的选项（如 --since="2024-01-01" --until="2024-12-31"）
# 说明：
#   - 统计每个用户的提交数、修改文件数、新增行数、删除行数和总修改行数
#   - 按总修改行数降序排列
#   - 支持使用git log的所有选项来过滤提交范围
# 示例：
#   ./git_user_stats.sh
#   ./git_user_stats.sh --since="2024-01-01"
#   ./git_user_stats.sh --author="john@example.com"
#   ./git_user_stats.sh --since="2024-01-01" --until="2024-12-31"
#

set -e  # 遇到错误立即退出

# 保存git log的选项参数
git_log_opts=( "$@" )

echo "📊 Git用户统计工具"
if [ ${#git_log_opts[@]} -gt 0 ]; then
    echo "🔍 过滤条件: ${git_log_opts[*]}"
fi
echo ""
echo "⏳ 正在分析Git提交历史..."
echo ""

# 检查是否在Git仓库中
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo "❌ 错误：当前目录不是Git仓库"
    exit 1
fi

# 执行git log并统计
# --format='author: %ae': 输出作者邮箱
# --numstat: 显示每个文件的增删行数统计
git log "${git_log_opts[@]}" --format='author: %ae' --numstat 2>/dev/null \
    | tr '[A-Z]' '[a-z]' \
    | grep -v '^$' \
    | grep -v '^-' \
    | gawk '
        {
            if ($1 == "author:") {
                # 提取作者邮箱
                author = $2;
                commits[author]++;
            } else {
                # 统计文件修改信息
                # $1: 新增行数, $2: 删除行数, $3: 文件名
                insertions[author] += $1;
                deletions[author] += $2;
                total[author] += $1 + $2;
                
                # 统计修改的文件数（每个文件只计数一次）
                author_file = author ":" $3;
                if (!(author_file in seen)) {
                    seen[author_file] = 1;
                    files[author]++;
                }
            }
        }
        END {
            # 如果没有数据，显示提示
            if (length(commits) == 0) {
                print "⚠️  未找到匹配的提交记录";
                exit 0;
            }
            
            # 打印表头
            printf("%-35s\t%-10s\t%-10s\t%-12s\t%-12s\t%-12s\n",
                   "Email", "Commits", "Files",
                   "Insertions", "Deletions", "Total Lines");
            printf("%-35s\t%-10s\t%-10s\t%-12s\t%-12s\t%-12s\n",
                   "-----", "-------", "-----",
                   "----------", "---------", "-----------");
            
            # 按总修改行数降序排列并打印统计结果
            n = asorti(total, sorted_emails, "@val_num_desc");
            for (i = 1; i <= n; i++) {
                email = sorted_emails[i];
                printf("%-35s\t%-10s\t%-10s\t%-12s\t%-12s\t%-12s\n",
                       email, commits[email], files[email],
                       insertions[email], deletions[email], total[email]);
            }
        }
'

echo ""
echo "✅ 统计完成"
