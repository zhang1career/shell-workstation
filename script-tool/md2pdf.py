#!/usr/bin/env python3
"""
将 Markdown 文件转换为 PDF。
用法: python md2pdf.py input.md [output.pdf]

优先使用 Chromium（与 Chrome 打印相同引擎），将文字转为 Type3 矢量字形内嵌，中文显示正确。
"""

import argparse
import sys
import tempfile
from pathlib import Path


def md2pdf(md_path: str, pdf_path: str | None = None) -> None:
    """将 Markdown 文件转换为 PDF。"""
    # 先检查 markdown 依赖，避免后续流程走到一半才失败。
    try:
        import markdown
    except ImportError:
        print("请先安装 markdown: pip install markdown", file=sys.stderr)
        sys.exit(1)

    md_file = Path(md_path)
    if not md_file.exists():
        print(f"文件不存在: {md_path}", file=sys.stderr)
        sys.exit(1)

    if pdf_path is None:
        pdf_path = md_file.with_suffix(".pdf")
    pdf_path = Path(pdf_path)
    print(f"开始转换: {md_file} -> {pdf_path}")

    with open(md_file, encoding="utf-8") as f:
        md_content = f.read()

    html_content = markdown.markdown(
        md_content,
        extensions=["tables", "fenced_code", "toc"],
        extension_configs={"toc": {"title": ""}},
    )

    # 使用系统字体，Chromium 会正确渲染并转为 Type3 矢量内嵌
    font_family = '"PingFang SC", "Microsoft YaHei", "SimHei", "Hiragino Sans GB", sans-serif'

    full_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body {{ font-family: {font_family}; line-height: 1.6; padding: 2em; }}
        h1 {{ font-size: 1.8em; border-bottom: 1px solid #ccc; padding-bottom: 0.3em; }}
        h2 {{ font-size: 1.4em; margin-top: 1.2em; }}
        h3 {{ font-size: 1.2em; }}
        table {{ border-collapse: collapse; margin: 1em 0; }}
        th, td {{ border: 1px solid #ddd; padding: 0.5em 0.8em; text-align: left; }}
        th {{ background: #f5f5f5; }}
        code {{ background: #f4f4f4; padding: 0.2em 0.4em; font-size: 0.9em; }}
        pre {{ background: #f4f4f4; padding: 1em; overflow-x: auto; }}
        hr {{ border: none; border-top: 1px solid #ccc; margin: 1.5em 0; }}
    </style>
</head>
<body>
{html_content}
</body>
</html>"""

    # 优先使用 Playwright + Chromium（与 Chrome 打印相同，Type3 矢量内嵌，中文正确）
    # 只要可用就走这个分支，保证跨平台渲染一致性。
    use_playwright = False
    try:
        from playwright.sync_api import sync_playwright

        use_playwright = True
    except ImportError:
        pass

    if use_playwright:
        print("使用 Playwright + Chromium 生成 PDF...")
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".html", delete=False, encoding="utf-8"
        ) as f:
            f.write(full_html)
            html_path = Path(f.name)
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch()
                page = browser.new_page()
                page.goto(html_path.as_uri())
                page.pdf(path=str(pdf_path))
                browser.close()
            print(f"已生成: {pdf_path}")
        except Exception as exc:
            print(f"Playwright 生成失败: {exc}", file=sys.stderr)
            print("将尝试使用 pdfkit 作为备选方案...", file=sys.stderr)
        finally:
            html_path.unlink(missing_ok=True)
        if pdf_path.exists():
            return

    # 备选: pdfkit
    try:
        import pdfkit

        print("使用 pdfkit 生成 PDF...")
        options = {"encoding": "UTF-8"}
        pdfkit.from_string(full_html, str(pdf_path), options=options)
        print(f"已生成: {pdf_path}")
        return
    except ImportError:
        print("未安装 pdfkit，无法使用备选方案。", file=sys.stderr)
    except Exception as exc:
        print(f"pdfkit 生成失败: {exc}", file=sys.stderr)

    print(
        "转换失败。请优先安装 playwright（推荐，中文支持最好）:\n"
        "  pip install markdown playwright\n"
        "  playwright install chromium\n\n"
        "或使用 pdfkit 方案（需系统安装 wkhtmltopdf）:\n"
        "  pip install pdfkit",
        file=sys.stderr,
    )
    sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser(description="将 Markdown 文件转换为 PDF")
    parser.add_argument("input", help="输入的 .md 文件")
    parser.add_argument("output", nargs="?", help="输出的 .pdf 文件（可选）")
    args = parser.parse_args()

    md2pdf(args.input, args.output)


if __name__ == "__main__":
    main()
