#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DJVU 转 PDF 格式转换

将 DJVU 文件转换为 PDF 格式，支持中文路径和中文内容。
依赖：Python 3.6+，djvulibre（ddjvu 命令）
用法：python djvu2pdf.py <input> [output] [--output-dir DIR]
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path
from typing import List, Optional, Tuple


def find_ddjvu() -> Optional[str]:
    """查找 ddjvu 命令路径。"""
    try:
        result = subprocess.run(
            ["which", "ddjvu"],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except (FileNotFoundError, OSError):
        pass
    return None


def convert_djvu_to_pdf(
    input_path: Path,
    output_path: Path,
) -> Tuple[bool, str]:
    """
    将单个 DJVU 文件转换为 PDF。

    :param input_path: 输入 DJVU 文件路径
    :param output_path: 输出 PDF 文件路径
    :return: (成功与否, 错误信息)
    """
    ddjvu = find_ddjvu()
    if not ddjvu:
        return False, "未找到 ddjvu 命令，请先安装 djvulibre。\n  macOS: brew install djvulibre\n  Ubuntu: sudo apt install djvulibre-bin"

    # 使用字符串路径，支持中文等 Unicode 路径
    inp = str(input_path.resolve())
    out = str(output_path.resolve())

    try:
        subprocess.run(
            [ddjvu, "-format=pdf", inp, out],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        return True, ""
    except subprocess.CalledProcessError as e:
        err = (e.stderr or e.stdout or "").strip() or str(e)
        return False, err
    except Exception as e:
        return False, str(e)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="将 DJVU 文件转换为 PDF 格式，支持中文路径与中文内容。",
        epilog="""
示例:
  python djvu2pdf.py book.djvu
  python djvu2pdf.py book.djvu book.pdf
  python djvu2pdf.py ./djvu_dir/ --output-dir ./pdf_out/
  python djvu2pdf.py 中文书名.djvu
        """,
    )
    parser.add_argument(
        "input",
        help="输入 DJVU 文件或目录路径（目录会批量转换其中的 .djvu 文件）",
    )
    parser.add_argument(
        "output",
        nargs="?",
        default=None,
        help="输出 PDF 路径（单文件时可选，默认：输入同目录、同主名.pdf）",
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        default=None,
        metavar="DIR",
        help="批量转换时的输出目录（与 input 为目录时配合使用）",
    )
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"错误：文件或目录不存在: {input_path}", file=sys.stderr)
        sys.exit(1)

    # 单文件转换
    if input_path.is_file():
        if not input_path.suffix.lower() in (".djvu", ".djv"):
            print("错误：输入文件扩展名应为 .djvu 或 .djv", file=sys.stderr)
            sys.exit(1)
        output_path: Optional[Path]
        if args.output:
            output_path = Path(args.output)
        else:
            output_path = input_path.with_suffix(".pdf")

        output_path.parent.mkdir(parents=True, exist_ok=True)
        ok, err = convert_djvu_to_pdf(input_path, output_path)
        if ok:
            print(f"转换完成: {output_path}")
        else:
            print(f"转换失败: {err}", file=sys.stderr)
            sys.exit(1)
        return

    # 目录批量转换
    if not input_path.is_dir():
        print("错误：输入路径既不是文件也不是目录", file=sys.stderr)
        sys.exit(1)

    out_dir: Path
    if args.output_dir:
        out_dir = Path(args.output_dir)
    elif args.output:
        out_dir = Path(args.output)
    else:
        out_dir = input_path

    out_dir.mkdir(parents=True, exist_ok=True)
    files: List[Path] = sorted(
        f for f in input_path.iterdir()
        if f.is_file() and f.suffix.lower() in (".djvu", ".djv")
    )
    if not files:
        print(f"未在目录中找到 .djvu/.djv 文件: {input_path}", file=sys.stderr)
        sys.exit(1)

    success = 0
    for i, f in enumerate(files, 1):
        out_file = out_dir / (f.stem + ".pdf")
        ok, err = convert_djvu_to_pdf(f, out_file)
        if ok:
            success += 1
            print(f"[{i}/{len(files)}] ✓ {f.name} -> {out_file.name}")
        else:
            print(f"[{i}/{len(files)}] ✗ {f.name}: {err}", file=sys.stderr)

    print(f"\n完成: 成功 {success}/{len(files)}")
    if success < len(files):
        sys.exit(1)


if __name__ == "__main__":
    main()
