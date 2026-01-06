#!/usr/bin/env python3
#
# 功能：将文本文件转换为语音（使用Microsoft Edge TTS）
# 用法：python txt2voice.py <input_file> [output_file] [voice]
# 参数：
#   input_file  - 必需，输入文本文件路径
#   output_file - 可选，输出音频文件路径，默认：output.mp3
#   voice       - 可选，语音模型，默认：en-US-JennyNeural
# 说明：
#   - 使用Microsoft Edge TTS服务进行文本转语音
#   - 自动将长文本分割为多个片段处理
#   - 支持多种语言和语音模型
#   - 输出MP3格式音频文件
# 依赖：
#   - edge-tts
#   - pydub
#   - tqdm
# 常用语音模型：
#   - zh-CN-XiaoxiaoNeural (中文，女声)
#   - zh-CN-YunxiNeural (中文，男声)
#   - en-US-JennyNeural (英文，女声)
#   - en-US-GuyNeural (英文，男声)
# 示例：
#   python txt2voice.py text.txt
#   python txt2voice.py text.txt output.mp3
#   python txt2voice.py text.txt output.mp3 zh-CN-XiaoxiaoNeural
#

import sys
import asyncio
import argparse
import edge_tts
from pathlib import Path
from tqdm import tqdm
import re
from pydub import AudioSegment


def split_text(text, max_len=300):
    """
    将长文本拆分为多个小段，避免单次调用过长导致API错误
    
    参数:
        text: 要分割的文本
        max_len: 每段的最大长度（字符数），默认300
    
    返回:
        文本片段列表
    """
    # 按句子标点符号分割
    sentences = re.split(r'([。！？.!?])', text)
    chunks = []
    temp = ''
    
    for part in sentences:
        temp += part
        # 当累积长度达到最大值时，保存当前片段
        if len(temp) >= max_len:
            chunks.append(temp.strip())
            temp = ''
    
    # 添加剩余文本
    if temp:
        chunks.append(temp.strip())
    
    return chunks


async def text_to_speech_with_progress(input_file, output_file="output.mp3", voice="en-US-JennyNeural"):
    """
    将文本文件转换为语音文件
    
    参数:
        input_file: 输入文本文件路径
        output_file: 输出音频文件路径
        voice: 语音模型名称
    """
    path = Path(input_file)
    
    # 检查文件是否存在
    if not path.is_file():
        print(f"❌ 错误：文件不存在: {input_file}", file=sys.stderr)
        sys.exit(1)
    
    # 读取文本文件
    try:
        text = path.read_text(encoding='utf-8').strip()
    except UnicodeDecodeError:
        print(f"❌ 错误：无法读取文件，请确保文件是UTF-8编码", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ 错误：读取文件失败: {e}", file=sys.stderr)
        sys.exit(1)
    
    if not text:
        print("⚠️  警告：文件为空", file=sys.stderr)
        sys.exit(1)
    
    print(f"📄 文本文件: {input_file}")
    print(f"📊 文本长度: {len(text)} 字符")
    print(f"🎤 语音模型: {voice}")
    print("")
    
    # 分割文本
    chunks = split_text(text)
    print(f"📝 文本已分割为 {len(chunks)} 个片段")
    print("🔄 开始语音合成...")
    print("")
    
    # 生成每个片段的音频
    temp_files = []
    try:
        for i, chunk in enumerate(tqdm(chunks, desc="合成进度", ncols=80, unit="片段")):
            temp_file = f"temp_part_{i}.mp3"
            try:
                tts = edge_tts.Communicate(chunk, voice=voice)
                await tts.save(temp_file)
                temp_files.append(temp_file)
            except Exception as e:
                print(f"\n⚠️  警告：片段 {i+1} 合成失败: {e}", file=sys.stderr)
                # 继续处理其他片段
    except KeyboardInterrupt:
        print("\n\n🛑 合成已中断")
        # 清理临时文件
        for temp in temp_files:
            Path(temp).unlink(missing_ok=True)
        sys.exit(1)
    
    if not temp_files:
        print("❌ 错误：没有成功生成任何音频片段", file=sys.stderr)
        sys.exit(1)
    
    # 合并所有音频片段
    print("")
    print("🔄 正在合并音频片段...")
    try:
        combined = AudioSegment.empty()
        for temp in temp_files:
            audio_segment = AudioSegment.from_file(temp, format="mp3")
            combined += audio_segment
            # 删除临时文件
            Path(temp).unlink(missing_ok=True)
        
        # 导出最终音频文件
        combined.export(output_file, format="mp3")
        duration = len(combined) / 1000.0  # 转换为秒
        print(f"✅ 语音文件已保存: {output_file}")
        print(f"📊 音频时长: {duration:.2f} 秒")
    except Exception as e:
        print(f"❌ 错误：合并音频失败: {e}", file=sys.stderr)
        # 清理临时文件
        for temp in temp_files:
            Path(temp).unlink(missing_ok=True)
        sys.exit(1)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="将文本文件转换为语音（使用Microsoft Edge TTS）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
常用语音模型:
  中文:
    zh-CN-XiaoxiaoNeural (女声)
    zh-CN-YunxiNeural (男声)
    zh-CN-YunyangNeural (男声，新闻播报)
  
  英文:
    en-US-JennyNeural (女声)
    en-US-GuyNeural (男声)
    en-US-AriaNeural (女声)
  
  其他语言:
    使用 edge-tts --list-voices 查看所有可用语音

示例:
  %(prog)s text.txt
  %(prog)s text.txt output.mp3
  %(prog)s text.txt output.mp3 zh-CN-XiaoxiaoNeural
        """
    )
    
    parser.add_argument(
        "input_file",
        help="输入文本文件路径"
    )
    
    parser.add_argument(
        "output_file",
        nargs="?",
        default="output.mp3",
        help="输出音频文件路径 (默认: output.mp3)"
    )
    
    parser.add_argument(
        "voice",
        nargs="?",
        default="en-US-JennyNeural",
        help="语音模型 (默认: en-US-JennyNeural)"
    )
    
    args = parser.parse_args()
    
    # 运行异步函数
    try:
        asyncio.run(text_to_speech_with_progress(
            args.input_file,
            args.output_file,
            args.voice
        ))
    except KeyboardInterrupt:
        print("\n\n🛑 操作已取消")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 错误: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

