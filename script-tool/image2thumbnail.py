#!/usr/bin/env python3
"""将图片缩放为指定尺寸的缩略图（如应用图标、列表小图）。

依赖: pip install Pillow

基本用法:
    python image2thumbnail.py icon.png
    python image2thumbnail.py photo.jpg -o thumb.jpg -W 120 -H 120 -m contain

缩放模式 (-m):
    cover   — 等比缩放后居中裁剪，铺满目标尺寸（默认，适合图标）
    contain — 完整显示原图，不足处透明留白（输出 PNG/WebP 时保留透明）
    stretch — 非等比拉伸至目标宽高
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    from PIL import Image, ImageOps
except ImportError:
    print("请先安装 Pillow: pip install Pillow", file=sys.stderr)
    sys.exit(1)


def resize_to_thumbnail(
    src: Path,
    dst: Path,
    width: int,
    height: int,
    mode: str,
) -> None:
    im = Image.open(src)
    # 非常见模式先转 RGBA，调色板图单独转 RGBA 以保留/处理透明
    if im.mode not in ("RGB", "RGBA", "L", "LA", "P"):
        im = im.convert("RGBA")
    elif im.mode == "P":
        im = im.convert("RGBA")

    size = (width, height)
    resample = Image.Resampling.LANCZOS

    if mode == "stretch":
        out = im.resize(size, resample=resample)
    elif mode == "contain":
        # 缩小到能放进 size 的最大尺寸，再居中贴到透明画布上
        out = ImageOps.contain(im, size, method=resample)
        canvas = Image.new("RGBA", size, (0, 0, 0, 0))
        x = (width - out.width) // 2
        y = (height - out.height) // 2
        if out.mode != "RGBA":
            out = out.convert("RGBA")
        canvas.paste(out, (x, y))
        out = canvas
    elif mode == "cover":
        out = ImageOps.fit(im, size, method=resample, centering=(0.5, 0.5))
    else:
        raise ValueError(f"未知模式: {mode}")

    dst.parent.mkdir(parents=True, exist_ok=True)
    ext = dst.suffix.lower()
    save_kw: dict = {}
    if ext in (".jpg", ".jpeg"):
        out = out.convert("RGB")
        save_kw["quality"] = 92
        save_kw["optimize"] = True
    elif ext == ".webp":
        save_kw["quality"] = 90
    out.save(dst, **save_kw)


def main() -> None:
    p = argparse.ArgumentParser(
        description="将图片缩放到指定尺寸（如 1024×1024 → 58×58）。",
        epilog="示例: %(prog)s app.png -W 58\n       %(prog)s logo.png -o out.png -m contain",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("input", type=Path, help="源图片路径（png、jpg、webp 等）")
    p.add_argument(
        "-o",
        "--output",
        type=Path,
        default=None,
        help="输出路径；默认在源文件同目录生成「原名_thumb.扩展名」",
    )
    p.add_argument(
        "-W",
        "--width",
        type=int,
        default=58,
        help="目标宽度，默认 58",
    )
    p.add_argument(
        "-H",
        "--height",
        type=int,
        default=None,
        help="目标高度；省略则与宽度相同（正方形）",
    )
    p.add_argument(
        "-m",
        "--mode",
        choices=("cover", "contain", "stretch"),
        default="cover",
        help="cover=裁剪填满；contain=完整放入可留白；stretch=拉伸变形",
    )
    args = p.parse_args()
    src = args.input.expanduser().resolve()
    if not src.is_file():
        print(f"文件不存在: {src}", file=sys.stderr)
        sys.exit(1)

    h = args.height if args.height is not None else args.width
    if args.width < 1 or h < 1:
        print("宽、高必须为正整数", file=sys.stderr)
        sys.exit(1)

    if args.output is not None:
        dst = args.output.expanduser().resolve()
    else:
        dst = src.with_name(f"{src.stem}_thumb{src.suffix}")

    resize_to_thumbnail(src, dst, args.width, h, args.mode)
    print(f"已写入: {dst}")


if __name__ == "__main__":
    main()
