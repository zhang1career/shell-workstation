#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MP3 响度归一化脚本

功能：
    使用 EBU R128 标准对 MP3 进行响度归一化，尽量不损失声音细节。
    可指定目标响度（LUFS）、真峰值限制（TP）和响度范围（LRA），输出为高质量 MP3。

用法：
    python change_sound_volume.py <input_mp3> [output_mp3] [options]

示例：
    # 使用默认目标响度 -16 LUFS
    python change_sound_volume.py input.mp3

    # 指定输出文件和目标响度
    python change_sound_volume.py input.mp3 output_normalized.mp3 -l -14

    # 查看帮助
    python change_sound_volume.py --help

依赖：
    - Python 3.6+
    - ffmpeg（需包含 loudnorm 滤镜与 libmp3lame 编码器）
"""

import argparse
import subprocess
import sys
from pathlib import Path


def normalize_mp3_lufs(
    input_mp3: str,
    output_mp3: str,
    target_lufs: int = -16,
    tp_db: float = -1.5,
    lra: float = 11.0,
) -> None:
    """
    使用 EBU R128 标准对 MP3 进行响度归一化，尽量不损失声音细节。

    参数：
        input_mp3: 输入 MP3 文件路径
        output_mp3: 输出 MP3 文件路径
        target_lufs: 目标响度（LUFS），常用 -16（广播/播客）或 -14（流媒体）
        tp_db: 真峰值限制（dB），默认 -1.5，避免数字削波
        lra: 响度范围（Loudness Range），默认 11.0
    """
    cmd = [
        "ffmpeg",
        "-y",  # 覆盖已存在的输出文件
        "-i", input_mp3,
        "-af", f"loudnorm=I={target_lufs}:TP={tp_db}:LRA={lra}",
        "-vn",  # 不处理视频
        "-c:a", "libmp3lame",
        "-q:a", "0",  # LAME V0（高质量，约 245 kbps VBR）
        output_mp3,
    ]
    subprocess.run(cmd, check=True)


def main() -> None:
    """解析命令行参数并执行响度归一化。"""
    parser = argparse.ArgumentParser(
        description="使用 EBU R128 对 MP3 进行响度归一化（需 ffmpeg）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s input.mp3
  %(prog)s input.mp3 output_normalized.mp3
  %(prog)s input.mp3 -l -14
  %(prog)s input.mp3 out.mp3 -l -14 -t -2.0
        """,
    )

    parser.add_argument(
        "input_mp3",
        type=str,
        help="输入 MP3 文件路径",
    )
    parser.add_argument(
        "output_mp3",
        type=str,
        nargs="?",
        default=None,
        help="输出 MP3 文件路径（默认：在输入文件名后加 _normalized）",
    )
    parser.add_argument(
        "-l", "--lufs",
        type=int,
        default=-16,
        metavar="LUFS",
        help="目标响度 LUFS，常用 -16（广播/播客）或 -14（流媒体）（默认: -16）",
    )
    parser.add_argument(
        "-t", "--tp",
        type=float,
        default=-1.5,
        metavar="DB",
        help="真峰值限制 dB（默认: -1.5）",
    )
    parser.add_argument(
        "-r", "--lra",
        type=float,
        default=11.0,
        metavar="LRA",
        help="响度范围 LRA（默认: 11.0）",
    )

    args = parser.parse_args()

    input_path = Path(args.input_mp3)
    if not input_path.exists():
        print(f"错误: 输入文件不存在 -> {args.input_mp3}", file=sys.stderr)
        sys.exit(1)
    if not input_path.is_file():
        print(f"错误: 输入路径不是文件 -> {args.input_mp3}", file=sys.stderr)
        sys.exit(1)

    # 默认输出：输入名_normalized.mp3，与输入同目录
    if args.output_mp3 is None:
        output_path = input_path.parent / f"{input_path.stem}_normalized{input_path.suffix}"
    else:
        output_path = Path(args.output_mp3)

    # 避免覆盖输入文件
    if output_path.resolve() == input_path.resolve():
        print("错误: 输出路径不能与输入路径相同", file=sys.stderr)
        sys.exit(1)

    print(f"输入: {input_path}")
    print(f"输出: {output_path}")
    print(f"目标响度: {args.lufs} LUFS")
    print("正在处理...")

    try:
        normalize_mp3_lufs(
            str(input_path),
            str(output_path),
            target_lufs=args.lufs,
            tp_db=args.tp,
            lra=args.lra,
        )
        print("完成 ✅")
    except FileNotFoundError:
        print("错误: 未找到 ffmpeg，请先安装。", file=sys.stderr)
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"错误: ffmpeg 执行失败（退出码 {e.returncode}）", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
