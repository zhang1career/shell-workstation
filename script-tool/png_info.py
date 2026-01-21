#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PNG图片信息分析工具

功能：
    分析PNG图片的尺寸信息（宽度和高度），并打印出来。

依赖：
    - Python 3.6+
    - Pillow (PIL) 库

用法：
    python png_info.py <image.png>

示例：
    python png_info.py example.png
    python png_info.py /path/to/image.png
"""

import sys
import os
from PIL import Image


def print_usage():
    """打印使用说明"""
    print("Usage:")
    print("  python png_info.py <image.png>")
    print("")
    print("Description:")
    print("  Analyze a PNG image and print its pixel dimensions (width x height).")
    print("")
    print("Example:")
    print("  python png_info.py example.png")
    print("  python png_info.py /path/to/image.png")


def analyze_image(image_path):
    """
    分析PNG图片的尺寸信息
    
    参数：
        image_path: 图片文件路径
    
    返回：
        tuple: (width, height) 图片尺寸，失败时返回 None
    """
    try:
        # 检查文件是否存在
        if not os.path.exists(image_path):
            print(f"错误: 文件不存在 -> {image_path}")
            return None
        
        # 检查文件扩展名
        _, ext = os.path.splitext(image_path)
        if ext.lower() not in ['.png']:
            print(f"警告: 文件扩展名不是 .png ({ext})，但仍会尝试解析")
        
        # 打开并分析图片
        with Image.open(image_path) as img:
            # 获取图片格式
            img_format = img.format
            if img_format and img_format.upper() != 'PNG':
                print(f"警告: 图片格式是 {img_format}，不是 PNG")
            
            # 获取图片尺寸
            width, height = img.size
            
            # 获取文件大小
            file_size = os.path.getsize(image_path)
            file_size_mb = file_size / (1024 * 1024)
            
            # 打印信息
            print("=" * 60)
            print("PNG 图片信息")
            print("=" * 60)
            print(f"文件路径: {image_path}")
            print(f"图片格式: {img_format or 'Unknown'}")
            print(f"图片尺寸: {width} x {height} 像素")
            print(f"文件大小: {file_size:,} 字节 ({file_size_mb:.2f} MB)")
            print(f"宽高比: {width/height:.2f}" if height > 0 else "宽高比: N/A")
            print("=" * 60)
            
            return (width, height)
            
    except FileNotFoundError:
        print(f"错误: 文件未找到 -> {image_path}")
        return None
    except PermissionError:
        print(f"错误: 没有权限读取文件 -> {image_path}")
        return None
    except Exception as e:
        print(f"错误: {type(e).__name__} - {str(e)}")
        return None


def main():
    """主函数"""
    # 检查参数数量
    if len(sys.argv) != 2:
        print("错误: 参数数量不正确")
        print()
        print_usage()
        sys.exit(1)
    
    # 检查帮助参数
    image_path = sys.argv[1]
    if image_path in ['-h', '--help', 'help']:
        print_usage()
        sys.exit(0)
    
    # 分析图片
    result = analyze_image(image_path)
    
    # 根据结果退出
    if result is None:
        sys.exit(2)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()

