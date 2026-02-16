#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
音频去静音并裁剪前段

去掉开头、结尾的静音，保留有声音区域；可选用 --lifetime 只保留有声音开始后的前 N 毫秒。
支持常见格式（如 mp3、wav、ogg 等，依赖 pydub/ffmpeg）。

依赖：Python 3.6+，pydub（需系统安装 ffmpeg）
用法：python trim_audio_silence.py <输入音频> <输出音频> [--lifetime N] [--pre_roll N] [--post_roll N] ...
"""

import argparse
import os
import sys
from pathlib import Path

from pydub import AudioSegment
from pydub.silence import detect_nonsilent


def process_audio(
    input_path: str,
    output_path: str,
    lifetime: int = None,      # 毫秒，只保留有声音开始后的前 N 毫秒
    pre_roll: int = 30,        # 有声音前保留多少 ms
    post_roll: int = 50,       # 有声音后保留多少 ms
    silence_thresh: int = -40, # 静音阈值 (dBFS)，低于此视为静音
    min_silence_len: int = 20  # 判定为静音的最小连续长度 ms
) -> None:
    """
    去掉开头结尾静音，并可选只保留有声音区域的前 lifetime 毫秒。

    :param input_path: 输入音频文件路径
    :param output_path: 输出音频文件路径（格式由扩展名决定）
    :param lifetime: 若指定，只保留从“有声音开始”起的该毫秒数
    :param pre_roll: 第一段有声音开始前保留的毫秒数，避免截断开头
    :param post_roll: 最后一段有声音结束后保留的毫秒数，避免截断结尾
    :param silence_thresh: 静音阈值 dBFS，低于此电平视为静音
    :param min_silence_len: 连续静音至少多少毫秒才参与分段
    """
    audio = AudioSegment.from_file(input_path)

    # 找到所有非静音区间
    nonsilent_ranges = detect_nonsilent(
        audio,
        min_silence_len=min_silence_len,
        silence_thresh=silence_thresh,
    )

    if not nonsilent_ranges:
        raise ValueError("未检测到有效声音，请检查文件或调低 silence_thresh / 调小 min_silence_len")

    # 取第一段开始和最后一段结束
    start = nonsilent_ranges[0][0]
    end = nonsilent_ranges[-1][1]

    # 加上过渡区（避免把开头/结尾一点声音裁掉）
    start = max(0, start - pre_roll)
    end = min(len(audio), end + post_roll)

    # 若指定 lifetime，只保留从 start 起的 lifetime 毫秒
    if lifetime is not None:
        end = min(start + lifetime, end)

    trimmed_audio = audio[start:end]

    # 根据输出文件扩展名导出格式
    fmt = Path(output_path).suffix.lstrip(".").lower() or "mp3"
    trimmed_audio.export(output_path, format=fmt)

    print("处理完成")
    print(f"原始长度: {len(audio)} ms")
    print(f"输出长度: {len(trimmed_audio)} ms")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="音频去静音并裁剪：去掉首尾静音，可选只保留有声音开始后的前 N 毫秒。",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
说明：
  通过静音检测找到第一段和最后一段有声音的区间，去掉前后静音；
  可用 --pre_roll / --post_roll 在有声音前后多保留一点，避免截断。
  使用 --lifetime 可只保留“有声音开始”后的前 N 毫秒（适合裁剪长录音前段）。

示例：
  python trim_audio_silence.py input.mp3 output.mp3
  python trim_audio_silence.py rec.wav out.wav --lifetime 5000
  python trim_audio_silence.py rec.mp3 short.mp3 --pre_roll 50 --post_roll 80
        """,
    )
    parser.add_argument("input", help="输入音频文件路径")
    parser.add_argument("output", help="输出音频文件路径（格式由扩展名决定，如 .mp3 / .wav）")
    parser.add_argument(
        "--lifetime",
        type=int,
        default=None,
        metavar="N",
        help="只保留有声音开始后的前 N 毫秒（可选）",
    )
    parser.add_argument(
        "--pre_roll",
        type=int,
        default=30,
        metavar="MS",
        help="有声音前保留多少毫秒（默认 30）",
    )
    parser.add_argument(
        "--post_roll",
        type=int,
        default=50,
        metavar="MS",
        help="有声音后保留多少毫秒（默认 50）",
    )
    parser.add_argument(
        "--silence_thresh",
        type=int,
        default=-40,
        metavar="dBFS",
        help="静音阈值 dBFS，低于此视为静音（默认 -40）",
    )
    parser.add_argument(
        "--min_silence_len",
        type=int,
        default=20,
        metavar="MS",
        help="判定静音的最小连续长度 毫秒（默认 20）",
    )
    args = parser.parse_args()

    if not os.path.isfile(args.input):
        print(f"错误：输入文件不存在：{args.input}", file=sys.stderr)
        sys.exit(1)

    try:
        process_audio(
            input_path=args.input,
            output_path=args.output,
            lifetime=args.lifetime,
            pre_roll=args.pre_roll,
            post_roll=args.post_roll,
            silence_thresh=args.silence_thresh,
            min_silence_len=args.min_silence_len,
        )
    except ValueError as e:
        print(f"错误：{e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"错误：{e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
