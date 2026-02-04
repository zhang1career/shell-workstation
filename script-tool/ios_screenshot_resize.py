#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
iOS App Store 截屏尺寸转换工具

功能：
    将截屏图片转换为 App Store Connect 要求的尺寸。
    支持预设尺寸（iPhone 6.9"/6.5"/6.1" 等）或自定义宽高。
    支持多种缩放模式：适配（留边）、填充（裁剪）、拉伸。

依赖：
    - Python 3.6+
    - Pillow (PIL)：pip install Pillow

用法：
    # 单张图，转为 iPhone 6.7" 竖版（1290 x 2796）
    python ios_screenshot_resize.py screenshot.png --preset iphone67

    # 指定自定义尺寸
    python ios_screenshot_resize.py screenshot.png --size 1290x2796

    # 整个目录批量转换
    python ios_screenshot_resize.py ./screenshots/ --preset iphone67 --output ./out/

    # 缩放模式：fill=裁剪填满，fit=留边适配，stretch=拉伸
    python ios_screenshot_resize.py screenshot.png --preset iphone67 --mode fill
"""

import argparse
import os
import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    print("错误: 需要安装 Pillow。请执行: pip install Pillow")
    sys.exit(1)

# App Store 常用截屏尺寸（竖版 portrait，宽 x 高）
PRESETS = {
    "iphone69": (1260, 2736),   # 6.9" (部分机型)
    "iphone67": (1290, 2796),   # 6.7" iPhone 14/15 Pro Max 等
    "iphone67b": (1320, 2868),  # 6.7" 新机型
    "iphone65": (1284, 2778),   # 6.5" iPhone 14 Plus, 13 Pro Max 等
    "iphone63": (1206, 2622),   # 6.3" iPhone 15 Pro 等
    "iphone61": (1170, 2532),   # 6.1" 常用
    "iphone61b": (1125, 2436),  # 6.1" X/XS
    "iphone55": (1242, 2208),   # 5.5" iPhone 8 Plus 等
    "iphone47": (750, 1334),    # 4.7" iPhone 8/SE 等
    "ipad129": (2048, 2732),    # iPad Pro 12.9"
    "ipad129b": (2064, 2752),   # iPad Pro 13"
    "ipad11": (1668, 2388),     # iPad Pro 11" 等
}


def parse_size(s: str) -> tuple[int, int]:
    """解析 '宽x高' 或 '宽*高' 字符串，返回 (width, height)。"""
    s = s.strip().lower().replace("*", "x")
    if "x" not in s:
        raise ValueError(f"尺寸格式应为 宽x高，例如 1290x2796，当前: {s}")
    parts = s.split("x", 1)
    w, h = int(parts[0].strip()), int(parts[1].strip())
    if w <= 0 or h <= 0:
        raise ValueError("宽高必须为正整数")
    return (w, h)


def resize_image(
    img: Image.Image,
    target_w: int,
    target_h: int,
    mode: str = "fit",
) -> Image.Image:
    """
    将图片缩放到目标尺寸。
    mode: fit=适配留边, fill=填充裁剪, stretch=拉伸
    """
    w, h = img.size
    if mode == "stretch":
        return img.resize((target_w, target_h), Image.Resampling.LANCZOS)

    scale_fit = min(target_w / w, target_h / h)   # 适配：能完整放进目标
    scale_fill = max(target_w / w, target_h / h)  # 填充：铺满目标

    if mode == "fit":
        new_w = round(w * scale_fit)
        new_h = round(h * scale_fit)
        resized = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
        out = Image.new("RGB", (target_w, target_h), (0, 0, 0))
        paste_x = (target_w - new_w) // 2
        paste_y = (target_h - new_h) // 2
        if resized.mode == "RGBA":
            out.paste(resized, (paste_x, paste_y), resized)
        else:
            out.paste(resized, (paste_x, paste_y))
        return out

    if mode == "fill":
        new_w = round(w * scale_fill)
        new_h = round(h * scale_fill)
        resized = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
        x = (new_w - target_w) // 2
        y = (new_h - target_h) // 2
        return resized.crop((x, y, x + target_w, y + target_h))

    raise ValueError(f"未知 mode: {mode}，可选: fit, fill, stretch")


def process_file(
    path: Path,
    target_w: int,
    target_h: int,
    mode: str,
    out_dir: Path,
    suffix: str = "",
) -> bool:
    """处理单张图片，保存到 out_dir。返回是否成功。"""
    try:
        with Image.open(path) as img:
            rgb = img.convert("RGB") if img.mode not in ("RGB", "RGBA") else img
            out_img = resize_image(rgb, target_w, target_h, mode)
        out_name = path.stem + suffix + ".jpg"
        out_path = out_dir / out_name
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_img.save(out_path, "JPEG", quality=95)
        print(f"  OK: {path.name} -> {out_path}")
        return True
    except Exception as e:
        print(f"  失败: {path.name} - {e}", file=sys.stderr)
        return False


def main() -> None:
    parser = argparse.ArgumentParser(
        description="将截屏转换为 iOS App Store 所需尺寸",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "input",
        help="输入文件或目录路径",
    )
    parser.add_argument(
        "--preset", "-p",
        choices=list(PRESETS.keys()),
        help="预设尺寸名称（如 iphone67、iphone65、ipad129）",
    )
    parser.add_argument(
        "--size", "-s",
        metavar="WxH",
        help="自定义尺寸，例如 1290x2796",
    )
    parser.add_argument(
        "--output", "-o",
        default=None,
        help="输出目录，默认在输入同目录下创建 ios_screenshots_out",
    )
    parser.add_argument(
        "--mode", "-m",
        choices=["fit", "fill", "stretch"],
        default="fill",
        help="缩放模式: fit=留边适配, fill=裁剪填满(默认), stretch=拉伸",
    )
    parser.add_argument(
        "--suffix",
        default="_ios",
        help="输出文件名后缀，默认 _ios",
    )
    args = parser.parse_args()

    if not args.preset and not args.size:
        parser.error("必须指定 --preset 或 --size 之一")

    if args.preset:
        target_w, target_h = PRESETS[args.preset]
        print(f"使用预设: {args.preset} = {target_w} x {target_h}")
    else:
        target_w, target_h = parse_size(args.size)
        print(f"目标尺寸: {target_w} x {target_h}")

    path = Path(args.input)
    if not path.exists():
        print(f"错误: 路径不存在 -> {path}")
        sys.exit(2)

    if args.output:
        out_dir = Path(args.output)
    else:
        out_dir = (path.parent if path.is_file() else path) / "ios_screenshots_out"
    out_dir = out_dir.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"输出目录: {out_dir}")
    print(f"缩放模式: {args.mode}\n")

    if path.is_file():
        ok = process_file(path, target_w, target_h, args.mode, out_dir, args.suffix)
        sys.exit(0 if ok else 3)
    else:
        count, failed = 0, 0
        for f in sorted(path.iterdir()):
            if f.suffix.lower() in (".png", ".jpg", ".jpeg", ".webp"):
                if process_file(f, target_w, target_h, args.mode, out_dir, args.suffix):
                    count += 1
                else:
                    failed += 1
        print(f"\n完成: 成功 {count} 张，失败 {failed} 张")
        sys.exit(3 if failed else 0)


if __name__ == "__main__":
    main()
