#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
双轨音频混音脚本

功能：
    将两个音频文件混音后通过系统扬声器实时播放。支持音量、延迟、淡入淡出、
    EQ、压缩和限幅等参数，适用于背景音乐+人声、双轨试听等场景。

用法：
    python mix_sound.py <audio1> <audio2> [options]

示例：
    # 基本混音（等音量）
    python mix_sound.py voice.wav bgm.mp3

    # 调整两轨音量（人声大、背景小）
    python mix_sound.py voice.wav bgm.mp3 --vol1 1.0 --vol2 0.3

    # 背景音循环 + 淡入淡出
    python mix_sound.py voice.wav bgm.mp3 --loop2 --fadein 2 --fadeout 3

    # 第二轨延迟 0.5 秒
    python mix_sound.py a.wav b.wav --delay2 0.5

依赖：
    - Python 3.6+
    - ffmpeg（混音与编码）
    - ffplay（播放，需与 ffmpeg 同装）
"""

import argparse
import subprocess
import sys


def vol_to_ffmpeg(v):
    """
    将音量参数转换为 ffmpeg volume 滤镜字符串。
    支持数值（如 1.0）或分贝（如 -6dB）。
    """
    if v.endswith("db") or v.endswith("dB"):
        return f"volume={v}"
    return f"volume={float(v)}"


def build_filter(args):
    """
    根据命令行参数构建 ffmpeg -filter_complex 字符串。
    包含：两轨音量、第二轨延迟、淡入淡出、可选 EQ、混音及后处理（压缩/限幅）。
    """
    f1 = []  # 第一轨滤镜链
    f2 = []  # 第二轨滤镜链

    # 音量
    f1.append(vol_to_ffmpeg(args.vol1))
    f2.append(vol_to_ffmpeg(args.vol2))

    # 第二轨延迟（秒 -> 毫秒，双声道 adelay=左|右）
    if args.delay2 > 0:
        ms = int(args.delay2 * 1000)
        f2.append(f"adelay={ms}|{ms}")

    # 淡入（从开头）
    if args.fadein > 0:
        f1.append(f"afade=t=in:st=0:d={args.fadein}")
        f2.append(f"afade=t=in:st=0:d={args.fadein}")

    # 淡出（到结尾）
    if args.fadeout > 0:
        f1.append(f"afade=t=out:d={args.fadeout}")
        f2.append(f"afade=t=out:d={args.fadeout}")

    # 可选 EQ（用户传入的 ffmpeg 滤镜，如 highpass=100）
    if args.eq1:
        f1.append(args.eq1)
    if args.eq2:
        f2.append(args.eq2)

    # 混音：两轨混合，dropout_transition=0 避免静音时爆音
    mix = "amix=inputs=2:dropout_transition=0"

    # 可选后处理
    post = []
    if args.compress:
        post.append("acompressor")
    if args.limit:
        post.append("alimiter")

    # 拼接：[0:a] 轨1滤镜 -> [a1]; [1:a] 轨2滤镜 -> [a2]; [a1][a2] 混音(+后处理) -> 输出
    return (
        f"[0:a]{','.join(f1)}[a1];"
        f"[1:a]{','.join(f2)}[a2];"
        f"[a1][a2]{mix}"
        + ("," + ",".join(post) if post else "")
    )


def main():
    """解析参数，调用 ffmpeg 混音并管道输出到 ffplay 播放。"""
    p = argparse.ArgumentParser(
        description="将两个音频文件混音并实时播放（需 ffmpeg、ffplay）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s voice.wav bgm.mp3
  %(prog)s a.wav b.wav --vol1 1.0 --vol2 0.5 --fadein 2 --fadeout 3
  %(prog)s voice.wav loop.mp3 --loop2 --delay2 0.5
        """,
    )

    p.add_argument("audio1", help="第一个音频文件路径")
    p.add_argument("audio2", help="第二个音频文件路径")

    p.add_argument(
        "--vol1",
        default="1.0",
        help="第一轨音量，数值如 1.0 或分贝如 -6dB（默认: 1.0）",
    )
    p.add_argument(
        "--vol2",
        default="1.0",
        help="第二轨音量，数值如 1.0 或分贝如 -6dB（默认: 1.0）",
    )

    p.add_argument(
        "--delay2",
        type=float,
        default=0.0,
        help="第二轨延迟秒数（默认: 0）",
    )
    p.add_argument(
        "--loop2",
        action="store_true",
        help="第二轨循环播放（与第一轨等长或更长时有效）",
    )

    p.add_argument(
        "--fadein",
        type=float,
        default=0.0,
        help="两轨淡入时长（秒，默认: 0）",
    )
    p.add_argument(
        "--fadeout",
        type=float,
        default=0.0,
        help="两轨淡出时长（秒，默认: 0）",
    )

    p.add_argument(
        "--eq1",
        metavar="FILTER",
        help='第一轨 EQ/滤镜，如 "highpass=100" 或 "equalizer=f=1000:width_type=o:width=2:g=-3"',
    )
    p.add_argument(
        "--eq2",
        metavar="FILTER",
        help='第二轨 EQ/滤镜（同上）',
    )

    p.add_argument(
        "--compress",
        action="store_true",
        help="混音后加压缩（acompressor）",
    )
    p.add_argument(
        "--limit",
        action="store_true",
        help="混音后加限幅（alimiter），防止削波",
    )

    args = p.parse_args()

    # 构建 ffmpeg 命令：两路输入 -> filter_complex -> 输出 WAV 到 stdout
    cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error"]
    cmd += ["-i", args.audio1]
    if args.loop2:
        cmd += ["-stream_loop", "-1"]
    cmd += ["-i", args.audio2]
    cmd += [
        "-filter_complex",
        build_filter(args),
        "-f",
        "wav",
        "-",
    ]

    try:
        # ffmpeg 混音输出到管道
        play = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        # ffplay 从 stdin 播放到系统扬声器
        subprocess.run(
            ["ffplay", "-nodisp", "-autoexit", "-"],
            stdin=play.stdout,
        )
    except FileNotFoundError as e:
        print("错误: 未找到 ffmpeg 或 ffplay，请先安装。", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
