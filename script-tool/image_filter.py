#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
图片滤镜效果

对 JPG 图片应用滤镜效果（目前支持高斯模糊）。
依赖：Python 3.6+，Pillow (PIL)
用法：python image_filter.py <input.jpg> <output.jpg> --filter gaussian_blur [--radius N]
"""

import argparse
import os
import sys
from typing import Optional

from PIL import Image, ImageFilter


# 支持的滤镜类型
FILTER_GAUSSIAN_BLUR = "gaussian_blur"


def filter_image(
    input_path: str,
    output_path: str,
    filter_type: str = FILTER_GAUSSIAN_BLUR,
    radius: int = 5,
) -> None:
    """
    对图片应用指定滤镜并保存。

    :param input_path: 输入图片文件路径（JPG）
    :param output_path: 输出图片文件路径
    :param filter_type: 滤镜类型，目前支持 gaussian_blur
    :param radius: 高斯模糊半径（像素），数值越大模糊效果越强，默认 5
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"输入文件不存在: {input_path}")

    # 打开图片
    with Image.open(input_path) as img:
        # 确保为 RGB 模式（部分 JPG 可能为其他模式）
        if img.mode != "RGB":
            img = img.convert("RGB")

        # 根据滤镜类型应用对应效果
        if filter_type == FILTER_GAUSSIAN_BLUR:
            blurred = img.filter(ImageFilter.GaussianBlur(radius))
        else:
            raise ValueError(f"不支持的滤镜类型: {filter_type}，目前仅支持: {FILTER_GAUSSIAN_BLUR}")

        # 确保输出目录存在
        out_dir = os.path.dirname(output_path)
        if out_dir and not os.path.exists(out_dir):
            os.makedirs(out_dir, exist_ok=True)

        # 保存结果
        blurred.save(output_path, quality=95)
        print(f"滤镜处理完成，已保存至: {output_path}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="对 JPG 图片应用滤镜效果，目前支持高斯模糊。",
        epilog="""
示例:
  python image_filter.py photo.jpg output_blurred.jpg
  python image_filter.py photo.jpg output.jpg --filter gaussian_blur --radius 10
        """,
    )
    parser.add_argument("input", help="输入 JPG 图片文件路径")
    parser.add_argument("output", help="输出图片文件路径")
    parser.add_argument(
        "-f",
        "--filter",
        choices=[FILTER_GAUSSIAN_BLUR],
        default=FILTER_GAUSSIAN_BLUR,
        help="滤镜类型，目前仅支持 gaussian_blur（默认）",
    )
    parser.add_argument(
        "-r",
        "--radius",
        type=int,
        default=5,
        metavar="N",
        help="高斯模糊半径（像素），数值越大模糊越强（默认 5）",
    )
    args = parser.parse_args()

    try:
        filter_image(
            input_path=args.input,
            output_path=args.output,
            filter_type=args.filter,
            radius=args.radius,
        )
    except FileNotFoundError as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
