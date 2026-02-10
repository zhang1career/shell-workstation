"""
字体 PDF 预览工具：根据 TTF/OTF 字体文件生成一页 PDF 预览，并可选择用系统默认程序打开。

支持字体格式：TTF、OTF（含 CFF 轮廓）。预览页包含英文与中文示例句，便于快速查看字体效果。

命令行用法
---------
    python font_preview.py <字体路径> [选项]
    python -m font_preview <字体路径> [选项]

选项
----
    --no-open           生成 PDF 后不自动打开
    -o, --output PATH   指定输出 PDF 路径（默认使用临时文件）

示例
----
    # 生成预览并用默认程序打开
    python font_preview.py /path/to/GenRyuMin2TW-M.otf

    # 仅生成 PDF，不打开，并指定输出路径
    python font_preview.py ./MyFont.ttf --no-open -o preview.pdf

依赖
----
    fpdf2：pip install fpdf2
"""
import argparse
import os
import subprocess
import sys
import tempfile
from pathlib import Path

from fpdf import FPDF
from fpdf.enums import XPos, YPos


def _open_with_default_app(file_path: str) -> None:
    """使用系统默认程序打开文件（macOS: open，Windows: startfile，Linux: xdg-open）。"""
    path = os.path.abspath(file_path)
    if sys.platform == "darwin":
        subprocess.run(["open", path], check=True)
    elif sys.platform == "win32":
        os.startfile(path)
    else:
        subprocess.run(["xdg-open", path], check=True)


def preview(
    font_path: str,
    output_path: str | None = None,
    *,
    open_file: bool = True,
) -> str:
    """
    Generate a PDF preview for a font file (supports TTF and OTF including CFF outlines).

    Args:
        font_path: Path to the font file (.ttf or .otf).
        output_path: Where to write the PDF. If None, uses a temporary file (OS will clean it).
        open_file: Whether to open the generated PDF with the default application.

    Returns:
        The path to the generated PDF file.
    """
    path = Path(font_path)
    if not path.exists():
        raise FileNotFoundError(f"Font file not found: {font_path}")

    font_name = path.stem
    use_temp = output_path is None

    if use_temp:
        fd, output_path = tempfile.mkstemp(suffix=".pdf", prefix="font_preview_")
        os.close(fd)

    # 使用 fpdf2 生成单页 PDF：注册字体、写两行示例文字后输出
    pdf = FPDF()
    pdf.add_page()
    pdf.add_font(font_name, "", str(path))
    pdf.set_font(font_name, size=36)
    pdf.set_xy(50, 30)
    pdf.cell(200, 14, text="The quick brown fox", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.cell(200, 14, text="中文字体测试", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.output(output_path)

    if open_file:
        _open_with_default_app(output_path)

    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate a PDF preview for a font file and open it.",
        prog="font_preview",
    )
    parser.add_argument(
        "font_path",
        type=Path,
        help="Path to the font file (.ttf or .otf)",
    )
    parser.add_argument(
        "--no-open",
        action="store_true",
        help="Do not open the generated PDF after creating it",
    )
    parser.add_argument(
        "-o", "--output",
        dest="output_path",
        type=Path,
        default=None,
        help="Output PDF path (default: temporary file)",
    )
    args = parser.parse_args()

    if not args.font_path.exists():
        print(f"Error: Font file not found: {args.font_path}", file=sys.stderr)
        sys.exit(1)

    out_path = preview(
        str(args.font_path),
        output_path=str(args.output_path) if args.output_path else None,
        open_file=not args.no_open,
    )
    print(out_path)


if __name__ == "__main__":
    main()
