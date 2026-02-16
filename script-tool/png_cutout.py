#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PNG 棋盘格转透明脚本

将 PNG 中“棋盘格”颜色（灰白格）的像素改为透明。
常见导出错误会把透明区域变成 #fff / #c0c0c0 等灰白格，本脚本把这些像素的 alpha 置为 0。

依赖：Python 3.6+，Pillow (PIL)
用法：python png_cutout.py <输入.png> [输出.png]
"""

import argparse
import os
import sys
from pathlib import Path

from PIL import Image


def is_checker_color(r: int, g: int, b: int) -> bool:
    """
    判断像素是否为“棋盘格”颜色（灰白格）。

    条件：接近灰色（R≈G≈B，通道差 ≤ 15）且偏亮（平均亮度 ≥ 170）。
    常见导出错误产生的棋盘格多为白或浅灰。

    :param r: 红色 0–255
    :param g: 绿色 0–255
    :param b: 蓝色 0–255
    :return: 是则 True
    """
    avg = (r + g + b) / 3
    spread = max(r, g, b) - min(r, g, b)
    return spread <= 15 and avg >= 170


def checker_to_transparent(input_path: str, output_path: str) -> tuple:
    """
    将输入 PNG 中棋盘格颜色的像素设为透明，写入输出 PNG。

    :param input_path: 输入 PNG 路径
    :param output_path: 输出 PNG 路径
    :return: (被设为透明的像素数, 总像素数)
    """
    img = Image.open(input_path).convert("RGBA")
    width, height = img.size
    pixels = img.load()
    replaced = 0

    for y in range(height):
        for x in range(width):
            r, g, b, a = pixels[x, y]
            if is_checker_color(r, g, b):
                pixels[x, y] = (r, g, b, 0)
                replaced += 1

    img.save(output_path, "PNG")
    return replaced, width * height


def main() -> None:
    parser = argparse.ArgumentParser(
        description="将 PNG 中棋盘格（灰白格）颜色的像素改为透明。",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
说明：
  常见导出错误会把透明区域变成白色或浅灰棋盘格，本脚本将这些像素的 alpha 置为 0。
  判定条件：像素接近灰色（R≈G≈B）且偏亮（平均亮度 ≥ 170）。

示例：
  python png_cutout.py image.png
  python png_cutout.py image.png -o image_transparent.png
  python png_cutout.py image.png --output image_clean.png
        """,
    )
    parser.add_argument(
        "input",
        type=str,
        help="输入 PNG 文件路径（必填）",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default=None,
        help="输出 PNG 路径（可选，默认：输入同目录下 输入名.transparent.png）",
    )
    args = parser.parse_args()

    input_path = args.input
    if not os.path.isfile(input_path):
        print(f"错误：输入文件不存在：{input_path}", file=sys.stderr)
        sys.exit(1)
    if not input_path.lower().endswith(".png"):
        print("提示：输入文件建议为 PNG 格式，其他格式会按图像读取并输出为 PNG。", file=sys.stderr)

    if args.output is not None:
        output_path = args.output
    else:
        p = Path(input_path)
        output_path = str(p.parent / f"{p.stem}.transparent.png")

    if os.path.abspath(input_path) == os.path.abspath(output_path):
        print("错误：输出路径不能与输入路径相同，以免覆盖原图。请使用 -o 指定其他文件。", file=sys.stderr)
        sys.exit(1)

    try:
        replaced, total = checker_to_transparent(input_path, output_path)
        print(f"已保存：{output_path}")
        print(f"设为透明的像素：{replaced} / {total}")
    except Exception as e:
        print(f"错误：{e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
