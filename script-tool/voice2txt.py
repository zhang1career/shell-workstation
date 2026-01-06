#!/usr/bin/env python3
#
# 功能：将音频文件转换为文本（使用OpenAI Whisper）
# 用法：python voice2txt.py <audio_file> [--model MODEL] [--language LANGUAGE] [--output OUTPUT]
# 参数：
#   audio_file - 必需，音频文件路径（支持mp3, wav, m4a等格式）
#   --model    - 可选，Whisper模型名称，默认：base
#   --language - 可选，指定语言代码（如zh, en），默认：自动检测
#   --output   - 可选，输出文本文件路径，默认：输出到控制台
# 说明：
#   - 使用OpenAI Whisper进行语音识别
#   - 支持多种音频格式和语言
#   - 模型大小：tiny < base < small < medium < large（越大越准确，但越慢）
# 依赖：
#   - openai-whisper
#   - ffmpeg（用于音频处理）
# 模型说明：
#   - tiny:   最快，准确度较低，适合快速测试
#   - base:   平衡速度和准确度（推荐）
#   - small:  更准确，速度较慢
#   - medium: 高准确度，速度慢
#   - large:  最高准确度，速度最慢
# 示例：
#   python voice2txt.py audio.mp3
#   python voice2txt.py audio.mp3 --model small
#   python voice2txt.py audio.mp3 --language zh
#   python voice2txt.py audio.mp3 --output transcript.txt
#

import sys
import argparse
from pathlib import Path
import whisper


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="将音频文件转换为文本（使用OpenAI Whisper）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
模型选择指南:
  - tiny:   最快，准确度较低，适合快速测试
  - base:   平衡速度和准确度（推荐，默认）
  - small:  更准确，速度较慢
  - medium: 高准确度，速度慢
  - large:  最高准确度，速度最慢（需要大量内存）

语言代码示例:
  - zh: 中文
  - en: 英文
  - ja: 日文
  - ko: 韩文
  - 不指定则自动检测

示例:
  %(prog)s audio.mp3
  %(prog)s audio.mp3 --model small
  %(prog)s audio.mp3 --language zh
  %(prog)s audio.mp3 --output transcript.txt
  %(prog)s audio.mp3 --model medium --language en --output result.txt
        """
    )
    
    parser.add_argument(
        "audio_file",
        help="音频文件路径（mp3, wav, m4a等格式）"
    )
    
    parser.add_argument(
        "--model",
        default="base",
        choices=["tiny", "base", "small", "medium", "large"],
        help="Whisper模型名称 (默认: base)"
    )
    
    parser.add_argument(
        "--language",
        default=None,
        help="指定语言代码（如zh, en），不指定则自动检测"
    )
    
    parser.add_argument(
        "--output",
        default=None,
        help="输出文本文件路径，不指定则输出到控制台"
    )
    
    args = parser.parse_args()
    
    # 检查音频文件是否存在
    audio_path = Path(args.audio_file)
    if not audio_path.exists():
        print(f"❌ 错误：文件不存在: {args.audio_file}", file=sys.stderr)
        sys.exit(1)
    
    if not audio_path.is_file():
        print(f"❌ 错误：不是有效的文件: {args.audio_file}", file=sys.stderr)
        sys.exit(1)
    
    # 显示配置信息
    print("=" * 60)
    print("🎤 语音转文本工具")
    print("=" * 60)
    print(f"音频文件: {args.audio_file}")
    print(f"模型:     {args.model}")
    print(f"语言:     {args.language if args.language else '自动检测'}")
    if args.output:
        print(f"输出文件: {args.output}")
    else:
        print(f"输出:     控制台")
    print("=" * 60)
    print("")
    
    # 加载Whisper模型
    print(f"⏳ 正在加载Whisper模型: {args.model}...")
    print("   （首次使用会下载模型，请耐心等待）")
    try:
        model = whisper.load_model(args.model)
        print("✅ 模型加载成功")
    except Exception as e:
        print(f"❌ 错误：模型加载失败: {e}", file=sys.stderr)
        print("💡 提示：请确保已安装openai-whisper和ffmpeg", file=sys.stderr)
        sys.exit(1)
    
    print("")
    
    # 转录音频
    print(f"🔄 正在转录音频文件...")
    print("   （这可能需要几分钟，取决于音频长度和模型大小）")
    try:
        transcribe_options = {}
        if args.language:
            transcribe_options["language"] = args.language
        
        result = model.transcribe(str(audio_path), **transcribe_options)
        print("✅ 转录完成")
    except Exception as e:
        print(f"❌ 错误：转录失败: {e}", file=sys.stderr)
        print("💡 提示：请确保已安装ffmpeg并可以处理该音频格式", file=sys.stderr)
        sys.exit(1)
    
    # 获取转录文本
    text = result["text"].strip()
    
    # 输出结果
    print("")
    print("=" * 60)
    print("📝 转录结果")
    print("=" * 60)
    
    if args.output:
        # 保存到文件
        try:
            output_path = Path(args.output)
            output_path.write_text(text, encoding="utf-8")
            print(f"✅ 文本已保存到: {args.output}")
            print(f"📊 文本长度: {len(text)} 字符")
        except Exception as e:
            print(f"❌ 错误：保存文件失败: {e}", file=sys.stderr)
            print("\n转录文本内容：")
            print(text)
            sys.exit(1)
    else:
        # 输出到控制台
        print(text)
    
    # 显示额外信息（如果可用）
    if "language" in result:
        detected_lang = result["language"]
        print("")
        print(f"🌐 检测到的语言: {detected_lang}")
    
    print("=" * 60)
    print("✅ 完成")


if __name__ == "__main__":
    main()

