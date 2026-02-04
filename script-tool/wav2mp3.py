#!/usr/bin/env python3
"""
WAV to MP3 Converter - 批量或单文件 WAV 转 MP3

功能：将 WAV 音频文件转换为 MP3 格式，支持自定义采样率和比特率

用法：
    python wav2mp3.py <input_path> <output_path> [options]

参数：
    input_path   - 输入文件或目录路径
    output_path  - 输出目录路径

选项：
    --sample-rate, -r  采样率 (Hz)，默认: 44100
    --bitrate, -b      比特率 (kbps)，默认: 256

依赖：
    - pydub: pip install pydub
    - ffmpeg: 需要系统安装 ffmpeg
"""

import os
import sys
import argparse
from pathlib import Path

try:
    from pydub import AudioSegment
except ImportError:
    print("错误: 缺少 pydub 库，请运行: pip install pydub")
    sys.exit(1)


def convert_wav_to_mp3(
    input_file: Path,
    output_file: Path,
    sample_rate: int = 44100,
    bitrate: int = 256
) -> bool:
    """
    将单个 WAV 文件转换为 MP3
    
    Args:
        input_file: 输入 WAV 文件路径
        output_file: 输出 MP3 文件路径
        sample_rate: 采样率 (Hz)
        bitrate: 比特率 (kbps)
    
    Returns:
        bool: 转换是否成功
    """
    try:
        # 加载 WAV 文件
        audio = AudioSegment.from_wav(str(input_file))
        
        # 设置采样率
        audio = audio.set_frame_rate(sample_rate)
        
        # 确保输出目录存在
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # 导出为 MP3
        audio.export(
            str(output_file),
            format="mp3",
            bitrate=f"{bitrate}k"
        )
        
        return True
    except Exception as e:
        print(f"转换失败 [{input_file}]: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="WAV to MP3 Converter - 将 WAV 音频转换为 MP3 格式",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 转换单个文件
  python wav2mp3.py input.wav ./output/
  
  # 批量转换目录下所有 WAV 文件
  python wav2mp3.py ./wav_files/ ./mp3_files/
  
  # 自定义采样率和比特率
  python wav2mp3.py input.wav ./output/ -r 48000 -b 320
  
  # 使用较低比特率（节省空间）
  python wav2mp3.py ./wav_files/ ./mp3_files/ -b 128
        """
    )
    
    parser.add_argument(
        "input_path",
        type=str,
        help="输入文件或目录路径"
    )
    
    parser.add_argument(
        "output_path",
        type=str,
        help="输出目录路径"
    )
    
    parser.add_argument(
        "-r", "--sample-rate",
        type=int,
        default=44100,
        help="采样率 (Hz)，默认: 44100"
    )
    
    parser.add_argument(
        "-b", "--bitrate",
        type=int,
        default=256,
        help="比特率 (kbps)，默认: 256"
    )
    
    args = parser.parse_args()
    
    input_path = Path(args.input_path)
    output_path = Path(args.output_path)
    sample_rate = args.sample_rate
    bitrate = args.bitrate
    
    # 验证输入路径
    if not input_path.exists():
        print(f"错误: 输入路径不存在: {input_path}")
        sys.exit(1)
    
    # 收集要转换的文件
    wav_files = []
    if input_path.is_file():
        if input_path.suffix.lower() == ".wav":
            wav_files.append(input_path)
        else:
            print(f"错误: 输入文件不是 WAV 格式: {input_path}")
            sys.exit(1)
    else:
        # 目录模式：递归查找所有 WAV 文件
        wav_files = list(input_path.rglob("*.wav")) + list(input_path.rglob("*.WAV"))
        if not wav_files:
            print(f"错误: 目录中没有找到 WAV 文件: {input_path}")
            sys.exit(1)
    
    # 打印转换参数
    print("=" * 60)
    print("WAV to MP3 Converter")
    print("=" * 60)
    print(f"输入路径: {input_path}")
    print(f"输出路径: {output_path}")
    print(f"采样率: {sample_rate} Hz")
    print(f"比特率: {bitrate} kbps")
    print(f"文件数量: {len(wav_files)}")
    print("=" * 60)
    
    # 转换文件
    success_count = 0
    fail_count = 0
    
    for i, wav_file in enumerate(wav_files, 1):
        # 计算输出文件路径
        if input_path.is_file():
            # 单文件模式：直接放到输出目录
            mp3_file = output_path / (wav_file.stem + ".mp3")
        else:
            # 目录模式：保持相对路径结构
            relative_path = wav_file.relative_to(input_path)
            mp3_file = output_path / relative_path.with_suffix(".mp3")
        
        print(f"[{i}/{len(wav_files)}] 转换: {wav_file.name} -> {mp3_file.name}")
        
        if convert_wav_to_mp3(wav_file, mp3_file, sample_rate, bitrate):
            success_count += 1
            print(f"  ✓ 成功")
        else:
            fail_count += 1
            print(f"  ✗ 失败")
    
    # 打印统计
    print("=" * 60)
    print(f"转换完成: 成功 {success_count}, 失败 {fail_count}")
    print("=" * 60)
    
    if fail_count > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
