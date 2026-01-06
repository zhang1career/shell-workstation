#!/usr/bin/env python3
#
# 功能：播放音频文件，支持指定播放区间和播放速度
# 用法：python play_audio.py <audio_file> [--start SECONDS] [--end SECONDS] [--speed SPEED]
# 参数：
#   audio_file - 必需，音频文件路径（支持mp3, m4a, wav等格式）
#   --start    - 可选，开始播放时间（秒），默认：0
#   --end      - 可选，结束播放时间（秒），默认：播放到文件末尾
#   --speed    - 可选，播放速度倍数，默认：1.0（正常速度）
# 说明：
#   - 支持多种音频格式（mp3, m4a, wav, flac等）
#   - 可以指定播放的起始和结束时间
#   - 可以调整播放速度（0.5-2.0倍速）
# 依赖：
#   - pydub
#   - 系统需要安装ffmpeg或相应的音频解码器
# 示例：
#   python play_audio.py music.mp3
#   python play_audio.py music.mp3 --start 10 --end 60
#   python play_audio.py music.mp3 --speed 1.5
#   python play_audio.py music.mp3 --start 30 --end 90 --speed 0.8
#

import argparse
import sys
from pathlib import Path
from pydub import AudioSegment
from pydub.playback import play


def change_speed(audio, speed=1.0):
    """
    通过改变帧率来调整播放速度
    
    参数:
        audio: AudioSegment对象
        speed: 播放速度倍数（1.0为正常速度）
    
    返回:
        调整速度后的AudioSegment对象
    """
    new_frame_rate = int(audio.frame_rate * speed)
    return audio._spawn(
        audio.raw_data,
        overrides={"frame_rate": new_frame_rate}
    ).set_frame_rate(audio.frame_rate)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="播放音频文件，支持指定播放区间和播放速度",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s music.mp3
  %(prog)s music.mp3 --start 10 --end 60
  %(prog)s music.mp3 --speed 1.5
  %(prog)s music.mp3 --start 30 --end 90 --speed 0.8

支持的音频格式:
  mp3, m4a, wav, flac, ogg, aac 等（需要系统安装相应的解码器）
        """
    )
    
    parser.add_argument(
        "audio_file",
        help="音频文件路径（mp3, m4a, wav等格式）"
    )
    
    parser.add_argument(
        "--start",
        type=float,
        default=0,
        help="开始播放时间（秒），默认：0"
    )
    
    parser.add_argument(
        "--end",
        type=float,
        default=None,
        help="结束播放时间（秒），默认：播放到文件末尾"
    )
    
    parser.add_argument(
        "--speed",
        type=float,
        default=1.0,
        help="播放速度倍数（例如：0.5, 0.8, 1.0, 1.5, 2.0），默认：1.0"
    )
    
    args = parser.parse_args()
    
    # 检查文件是否存在
    audio_path = Path(args.audio_file)
    if not audio_path.exists():
        print(f"❌ 错误：文件不存在: {args.audio_file}", file=sys.stderr)
        sys.exit(1)
    
    if not audio_path.is_file():
        print(f"❌ 错误：不是有效的文件: {args.audio_file}", file=sys.stderr)
        sys.exit(1)
    
    # 验证参数
    if args.start < 0:
        print("❌ 错误：开始时间不能为负数", file=sys.stderr)
        sys.exit(1)
    
    if args.end is not None and args.end <= args.start:
        print("❌ 错误：结束时间必须大于开始时间", file=sys.stderr)
        sys.exit(1)
    
    if args.speed <= 0 or args.speed > 3.0:
        print("⚠️  警告：播放速度建议在0.5-2.0之间，当前值可能影响音质", file=sys.stderr)
    
    # 加载音频文件
    print(f"📂 正在加载音频文件: {args.audio_file}")
    try:
        audio = AudioSegment.from_file(args.audio_file)
    except Exception as e:
        print(f"❌ 错误：无法加载音频文件: {e}", file=sys.stderr)
        print("💡 提示：请确保系统已安装ffmpeg或相应的音频解码器", file=sys.stderr)
        sys.exit(1)
    
    file_duration = len(audio) / 1000.0  # 转换为秒
    print(f"✅ 音频加载成功（时长: {file_duration:.2f}秒）")
    
    # 应用时间切片
    start_ms = int(args.start * 1000)
    end_ms = int(args.end * 1000) if args.end else len(audio)
    
    # 验证时间范围
    if start_ms >= len(audio):
        print(f"❌ 错误：开始时间 ({args.start}秒) 超出音频长度 ({file_duration:.2f}秒)", file=sys.stderr)
        sys.exit(1)
    
    if end_ms > len(audio):
        print(f"⚠️  警告：结束时间 ({args.end}秒) 超出音频长度，将播放到文件末尾", file=sys.stderr)
        end_ms = len(audio)
    
    sliced = audio[start_ms:end_ms]
    slice_duration = len(sliced) / 1000.0
    
    # 应用速度调整
    if args.speed != 1.0:
        print(f"⚡ 正在调整播放速度为 {args.speed}x...")
        sliced = change_speed(sliced, args.speed)
    
    # 显示播放信息
    print("")
    print("=" * 60)
    print("🎵 播放信息")
    print("=" * 60)
    print(f"文件:     {args.audio_file}")
    print(f"开始:     {args.start}秒")
    print(f"结束:     {args.end if args.end else f'{file_duration:.2f}秒（文件末尾）'}")
    print(f"时长:     {slice_duration:.2f}秒")
    print(f"速度:     {args.speed}x")
    print("=" * 60)
    print("")
    
    # 播放音频
    print("▶️  开始播放...")
    try:
        play(sliced)
        print("✅ 播放完成")
    except KeyboardInterrupt:
        print("\n⚠️  播放已中断")
        sys.exit(0)
    except Exception as e:
        print(f"❌ 错误：播放失败: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

