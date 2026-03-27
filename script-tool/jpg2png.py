#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
JPG 转 PNG 图片格式转换

将 JPG/JPEG 图片转换为 PNG 格式。PNG 为无损格式，适合需要保留图片质量或后续编辑的场景。
依赖：Python 3.6+，Pillow (PIL)
用法：python jpg2png.py <input.jpg> [output.png] [-c N]
"""

import argparse
import os
import sys
from typing import Optional

from PIL import Image


def jpg_to_png(
    input_path: str,
    output_path: Optional[str] = None,
    compression: int = 6,
) -> None:
    """
    将 JPG/JPEG 图片转换为 PNG 格式。

    :param input_path: 输入 JPG/JPEG 文件路径
    :param output_path: 输出 PNG 路径，未指定时默认与输入同目录、同主名的 .png
    :param compression: PNG 压缩级别 0–9，0 无压缩最快，9 最高压缩最小文件（默认 6）
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"文件不存在: {input_path}")

    if output_path is None:
        output_path = os.path.splitext(input_path)[0] + ".png"

    with Image.open(input_path) as img:
        # JPG 通常为 RGB 模式，直接保存为 PNG
        # 若为其他模式（如 CMYK），转换为 RGB
        if img.mode not in ("RGB", "RGBA", "L"):
            img = img.convert("RGB")
        img.save(output_path, "PNG", compress_level=compression)

    print(f"转换完成: {output_path}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="将 JPG/JPEG 图片转换为 PNG 格式。PNG 为无损格式，适合保留图片质量或后续编辑。",
        epilog="""
示例:
  python jpg2png.py photo.jpg
  python jpg2png.py photo.jpg photo.png
  python jpg2png.py photo.jpg --compression 9
        """,
    )
    parser.add_argument("input", help="输入 JPG/JPEG 文件路径")
    parser.add_argument(
        "output",
        nargs="?",
        default=None,
        help="输出 PNG 路径（可选，默认：输入名.png）",
    )
    parser.add_argument(
        "-c",
        "--compression",
        type=int,
        default=6,
        metavar="N",
        help="PNG 压缩级别 0–9，0 无压缩最快，9 最小文件（默认 6）",
    )
    args = parser.parse_args()

    if not (0 <= args.compression <= 9):
        print("错误: 压缩级别必须在 0–9 之间", file=sys.stderr)
        sys.exit(1)

    try:
        jpg_to_png(args.input, args.output, compression=args.compression)
    except FileNotFoundError as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
