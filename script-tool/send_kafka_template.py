#!/usr/bin/env python3
#
# 功能：基于JSON模板生成并发送Kafka消息
# 用法：python send_kafka_template.py --topic TOPIC --template_file FILE [--bootstrap SERVER] [--interval SECONDS]
# 参数：
#   --topic         - 必需，Kafka主题名称
#   --template_file - 必需，JSON模板文件路径
#   --bootstrap     - 可选，Kafka服务器地址，默认：localhost:9092
#   --interval      - 可选，发送消息的间隔（秒），默认：1
# 模板规则：
#   - random_int_MIN_MAX: 生成MIN到MAX之间的随机整数
#   - random_choice_A_B_C: 从A、B、C中随机选择一个
#   - now_ts: 当前时间戳（精确到毫秒）
#   - 普通字符串: 直接使用该值
#   - 数字/布尔值: 直接使用该值
# 说明：
#   - 根据模板文件生成消息，每秒发送一条（可配置）
#   - 支持动态生成随机值和时间戳
#   - 用于测试和模拟数据流
# 依赖：
#   - kafka-python
# 示例：
#   python send_kafka_template.py --topic test-topic --template_file template.json
#   python send_kafka_template.py --topic test-topic --template_file template.json --bootstrap kafka:9092 --interval 2
#

import json
import random
import argparse
import sys
from datetime import datetime
from pathlib import Path
from kafka import KafkaProducer
from kafka.errors import KafkaError
import time


def generate_value(rule: str):
    """
    根据规则字符串生成字段值
    
    支持的规则：
    - random_int_MIN_MAX: 生成MIN到MAX之间的随机整数
    - random_choice_A_B_C: 从A、B、C中随机选择一个值
    - now_ts: 当前时间戳（格式：YYYY-MM-DD HH:MM:SS.mmm）
    - 普通字符串: 直接返回该字符串
    
    参数:
        rule: 规则字符串
    
    返回:
        生成的值
    """
    # 规则：随机整数 random_int_10000_99999
    if rule.startswith("random_int_"):
        try:
            parts = rule.split("_")
            if len(parts) >= 4:
                min_v = int(parts[2])
                max_v = int(parts[3])
                if min_v > max_v:
                    raise ValueError(f"最小值 {min_v} 不能大于最大值 {max_v}")
                return random.randint(min_v, max_v)
            else:
                raise ValueError(f"random_int规则格式错误: {rule}，应为 random_int_MIN_MAX")
        except (ValueError, IndexError) as e:
            raise ValueError(f"解析random_int规则失败: {rule}, 错误: {e}")

    # 规则：随机选择 random_choice_click_login_logout
    if rule.startswith("random_choice_"):
        parts = rule.split("_")[2:]  # 提取选项列表 ["click","login","logout"]
        if len(parts) == 0:
            raise ValueError(f"random_choice规则格式错误: {rule}，至少需要一个选项")
        return random.choice(parts)

    # 规则：当前时间戳 now_ts
    if rule == "now_ts":
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

    # 普通字符串，直接返回
    return rule


def generate_message(template: dict):
    """
    根据模板生成完整消息
    
    参数:
        template: 消息模板字典
    
    返回:
        生成的消息字典
    """
    msg = {}
    for key, rule in template.items():
        if isinstance(rule, str):
            # 字符串类型，尝试应用规则
            try:
                msg[key] = generate_value(rule)
            except ValueError as e:
                print(f"⚠️  警告：字段 '{key}' 的规则 '{rule}' 处理失败: {e}", file=sys.stderr)
                msg[key] = rule  # 失败时使用原始值
        else:
            # 数字、布尔值等，直接使用
            msg[key] = rule
    return msg


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="基于JSON模板生成并发送Kafka消息",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
模板文件示例 (template.json):
{
  "user_id": "random_int_1000_9999",
  "action": "random_choice_click_login_logout",
  "timestamp": "now_ts",
  "status": "active"
}

支持的规则:
  - random_int_MIN_MAX: 生成MIN到MAX之间的随机整数
  - random_choice_A_B_C: 从A、B、C中随机选择一个
  - now_ts: 当前时间戳（精确到毫秒）
  - 普通字符串/数字/布尔值: 直接使用

示例:
  %(prog)s --topic test-topic --template_file template.json
  %(prog)s --topic test-topic --template_file template.json --bootstrap kafka:9092
  %(prog)s --topic test-topic --template_file template.json --interval 2
        """
    )
    
    parser.add_argument(
        "--bootstrap",
        default="localhost:9092",
        help="Kafka服务器地址 (默认: localhost:9092)"
    )
    
    parser.add_argument(
        "--topic",
        required=True,
        help="Kafka主题名称"
    )
    
    parser.add_argument(
        "--template_file",
        required=True,
        help="JSON模板文件路径"
    )
    
    parser.add_argument(
        "--interval",
        type=float,
        default=1.0,
        help="发送消息的间隔（秒） (默认: 1.0)"
    )
    
    args = parser.parse_args()
    
    # 验证间隔时间
    if args.interval <= 0:
        print("❌ 错误：发送间隔必须大于0", file=sys.stderr)
        sys.exit(1)
    
    # 检查模板文件
    template_path = Path(args.template_file)
    if not template_path.exists():
        print(f"❌ 错误：模板文件不存在: {args.template_file}", file=sys.stderr)
        sys.exit(1)
    
    if not template_path.is_file():
        print(f"❌ 错误：不是有效的文件: {args.template_file}", file=sys.stderr)
        sys.exit(1)
    
    # 加载模板
    print(f"📂 正在加载模板文件: {args.template_file}")
    try:
        with open(args.template_file, "r", encoding="utf-8") as f:
            template = json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ 错误：模板文件JSON格式错误: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ 错误：无法读取模板文件: {e}", file=sys.stderr)
        sys.exit(1)
    
    if not isinstance(template, dict):
        print("❌ 错误：模板文件必须是JSON对象（字典）", file=sys.stderr)
        sys.exit(1)
    
    print(f"✅ 模板加载成功（包含 {len(template)} 个字段）")
    print("")
    
    # 创建Kafka生产者
    print(f"🔗 正在连接到Kafka服务器: {args.bootstrap}")
    try:
        producer = KafkaProducer(
            bootstrap_servers=args.bootstrap,
            value_serializer=lambda v: json.dumps(v, ensure_ascii=False).encode("utf-8")
        )
        # 测试连接
        producer.list_topics(timeout=5)
        print("✅ Kafka连接成功")
    except KafkaError as e:
        print(f"❌ 错误：无法连接到Kafka服务器: {e}", file=sys.stderr)
        print(f"💡 提示：请检查Kafka服务器地址和网络连接", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ 错误：Kafka连接失败: {e}", file=sys.stderr)
        sys.exit(1)
    
    print("")
    print("=" * 60)
    print("🚀 Kafka消息生产者已启动")
    print("=" * 60)
    print(f"主题:     {args.topic}")
    print(f"服务器:   {args.bootstrap}")
    print(f"间隔:     {args.interval}秒")
    print("=" * 60)
    print("💡 提示：按 Ctrl+C 停止发送")
    print("=" * 60)
    print("")
    
    # 发送消息
    message_count = 0
    try:
        while True:
            msg = generate_message(template)
            future = producer.send(args.topic, msg)
            
            # 等待发送完成（可选，用于错误检测）
            try:
                record_metadata = future.get(timeout=10)
                message_count += 1
                print(f"[{message_count}] ✅ 已发送: {json.dumps(msg, ensure_ascii=False)}")
            except KafkaError as e:
                print(f"❌ 发送失败: {e}", file=sys.stderr)
            
            time.sleep(args.interval)
    except KeyboardInterrupt:
        print("\n\n🛑 收到停止信号，正在关闭...")
        producer.close()
        print(f"✅ 已停止，共发送 {message_count} 条消息")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 错误：{e}", file=sys.stderr)
        producer.close()
        sys.exit(1)


if __name__ == "__main__":
    main()

