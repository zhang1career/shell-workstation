#!/usr/bin/env python3
"""将图片转为指定宽高的新图（通用尺寸转换）。

与 image2thumbnail.py 共用同一套缩放算法；本脚本侧重「必须指定目标尺寸」、
默认输出文件名带「宽x高」后缀，便于批量与归档。

依赖: pip install Pillow

用法示例:
    python image_resize.py photo.jpg --size 1920x1080
    python image_resize.py icon.png -W 512 -H 512 -o out.png -m contain
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# Pillow 未安装时，导入 image2thumbnail 会提示并退出
from image2thumbnail import resize_to_thumbnail


def parse_size(s: str) -> tuple[int, int]:
    """解析 '1920x1080'、'800X600'、'1920×1080' 等为 (宽, 高)。"""
    normalized = s.strip().lower().replace("×", "x")
    if not re.fullmatch(r"\d+x\d+", normalized):
        raise ValueError(f"尺寸格式应为 宽x高，例如 1920x1080，当前: {s!r}")
    w_str, h_str = normalized.split("x", 1)
    return int(w_str), int(h_str)


def resolve_dimensions(args: argparse.Namespace) -> tuple[int, int]:
    if args.size is not None:
        return parse_size(args.size)
    if args.width is not None:
        h = args.height if args.height is not None else args.width
        return args.width, h
    raise SystemExit(
        "请指定目标尺寸：--size 宽x高（如 1920x1080），或使用 -W / --width "
        "与可选的 -H / --height（省略高度时与宽度相同，输出正方形）。"
    )


def default_output_path(src: Path, width: int, height: int) -> Path:
    """默认：同目录下「原名_宽x高.扩展名」。"""
    return src.with_name(f"{src.stem}_{width}x{height}{src.suffix}")


def main() -> None:
    p = argparse.ArgumentParser(
        description="将图片缩放为指定的宽度与高度（cover/contain/stretch）。",
        epilog=(
            "示例:\n"
            "  %(prog)s photo.jpg --size 1280x720\n"
            "  %(prog)s a.png -W 800 -H 600 -m contain -o small.png"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("input", type=Path, help="源图片路径")
    p.add_argument(
        "--size",
        type=str,
        metavar="WxH",
        default=None,
        help="目标尺寸，如 1920x1080（与 -W/-H 二选一；若都不写则报错）",
    )
    p.add_argument(
        "-W",
        "--width",
        type=int,
        default=None,
        help="目标宽度（像素）；与 --size 二选一时可单独使用，此时高度默认同宽度",
    )
    p.add_argument(
        "-H",
        "--height",
        type=int,
        default=None,
        help="目标高度；仅在使用 -W 且未使用 --size 时生效，省略则等于宽度",
    )
    p.add_argument(
        "-o",
        "--output",
        type=Path,
        default=None,
        help="输出路径；默认在源文件同目录生成「原名_宽x高.扩展名」",
    )
    p.add_argument(
        "-m",
        "--mode",
        choices=("cover", "contain", "stretch"),
        default="cover",
        help="cover=裁剪铺满；contain=完整放入可留白；stretch=拉伸变形（默认 cover）",
    )
    args = p.parse_args()

    if args.size is not None and (args.width is not None or args.height is not None):
        print("错误: 不要同时使用 --size 与 -W/-H。", file=sys.stderr)
        sys.exit(1)

    try:
        width, height = resolve_dimensions(args)
    except ValueError as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)

    if width < 1 or height < 1:
        print("错误: 宽、高必须为正整数。", file=sys.stderr)
        sys.exit(1)

    src = args.input.expanduser().resolve()
    if not src.is_file():
        print(f"文件不存在: {src}", file=sys.stderr)
        sys.exit(1)

    if args.output is not None:
        dst = args.output.expanduser().resolve()
    else:
        dst = default_output_path(src, width, height)

    resize_to_thumbnail(src, dst, width, height, args.mode)
    print(f"已写入: {dst}")


if __name__ == "__main__":
    main()
