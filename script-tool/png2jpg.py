#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PNG 转 JPG 图片格式转换

将 PNG 图片转换为 JPG 格式。若 PNG 有透明通道，会先以白色填充后再导出。
依赖：Python 3.6+，Pillow (PIL)
用法：python png2jpg.py <input.png> [output.jpg] [--quality N]
"""

import argparse
import os
import sys
from typing import Optional

from PIL import Image


def png_to_jpg(
    input_path: str,
    output_path: Optional[str] = None,
    quality: int = 95,
) -> None:
    """
    将 PNG 图片转换为 JPG 格式。

    :param input_path: 输入 PNG 文件路径
    :param output_path: 输出 JPG 路径，未指定时默认与输入同目录、同主名的 .jpg
    :param quality: JPEG 质量 1–100，默认 95
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"文件不存在: {input_path}")

    if output_path is None:
        output_path = os.path.splitext(input_path)[0] + ".jpg"

    with Image.open(input_path) as img:
        # PNG 有透明通道时，需先以白色填充（JPG 不支持透明）
        if img.mode in ("RGBA", "LA"):
            background = Image.new("RGB", img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[-1])
            img = background
        else:
            img = img.convert("RGB")

        img.save(output_path, "JPEG", quality=quality)

    print(f"转换完成: {output_path}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="将 PNG 图片转换为 JPG 格式；若 PNG 有透明通道，以白色填充后导出。",
        epilog="""
示例:
  python png2jpg.py logo.png
  python png2jpg.py logo.png logo.jpg
  python png2jpg.py logo.png --quality 90
        """,
    )
    parser.add_argument("input", help="输入 PNG 文件路径")
    parser.add_argument("output", nargs="?", default=None, help="输出 JPG 路径（可选，默认：输入名.jpg）")
    parser.add_argument(
        "-q",
        "--quality",
        type=int,
        default=95,
        metavar="N",
        help="JPEG 质量 1–100（默认 95）",
    )
    args = parser.parse_args()

    try:
        png_to_jpg(args.input, args.output, quality=args.quality)
    except FileNotFoundError as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

