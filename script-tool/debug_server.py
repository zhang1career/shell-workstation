#!/usr/bin/env python3
#
# 功能：HTTP调试服务器，用于查看和分析HTTP请求详情
# 用法：python debug_server.py [--host HOST] [--port PORT] [--path PATH]
# 参数：
#   --host  - 可选，监听地址，默认：0.0.0.0
#   --port  - 可选，监听端口，默认：7788
#   --path  - 可选，调试路径前缀，默认：/debug
# 说明：
#   - 启动一个HTTP服务器，接收所有请求
#   - 当请求路径以指定前缀开头时，打印详细的请求信息
#   - 支持GET和POST请求
#   - 用于调试HTTP客户端、API调用等场景
# 示例：
#   python debug_server.py
#   python debug_server.py --port 8080
#   python debug_server.py --host 127.0.0.1 --port 9000 --path /api
#

import argparse
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
import sys
from datetime import datetime


class DebugHandler(BaseHTTPRequestHandler):
    """HTTP请求处理器，用于调试和查看请求详情"""
    
    def _print_request_info(self):
        """打印请求的详细信息"""
        parsed = urlparse(self.path)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        print("\n" + "=" * 60)
        print(f"📥 收到请求 - {timestamp}")
        print("=" * 60)
        print(f"方法:     {self.command}")
        print(f"路径:     {parsed.path}")
        print(f"查询参数: {parse_qs(parsed.query) if parsed.query else '无'}")

        # 打印请求头
        print("\n--- 请求头 ---")
        if self.headers:
            for k, v in self.headers.items():
                print(f"  {k}: {v}")
        else:
            print("  (无请求头)")

        # 打印请求体（如果有）
        content_length = int(self.headers.get("Content-Length", 0))
        if content_length > 0:
            body = self.rfile.read(content_length)
            print(f"\n--- 请求体 ({content_length} 字节) ---")
            try:
                # 尝试以UTF-8解码
                body_text = body.decode("utf-8")
                print(body_text)
            except UnicodeDecodeError:
                # 如果解码失败，显示原始字节（十六进制）
                print(f"  (二进制数据，前100字节):")
                print(f"  {body[:100].hex()}")
        else:
            print("\n--- 请求体 ---")
            print("  (无请求体)")

        print("=" * 60 + "\n")

    def log_message(self, format, *args):
        """重写日志方法，使用更友好的格式"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {format % args}")

    def do_GET(self):
        """处理GET请求"""
        if self.path.startswith(self.server.debug_path):
            self._print_request_info()

        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(b"OK\n")

    def do_POST(self):
        """处理POST请求"""
        if self.path.startswith(self.server.debug_path):
            self._print_request_info()

        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(b"OK\n")

    def do_PUT(self):
        """处理PUT请求"""
        if self.path.startswith(self.server.debug_path):
            self._print_request_info()

        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(b"OK\n")

    def do_DELETE(self):
        """处理DELETE请求"""
        if self.path.startswith(self.server.debug_path):
            self._print_request_info()

        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(b"OK\n")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="HTTP调试服务器 - 用于查看和分析HTTP请求详情",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s
  %(prog)s --port 8080
  %(prog)s --host 127.0.0.1 --port 9000 --path /api
  
使用说明:
  - 启动服务器后，所有发送到指定路径的请求都会被打印到控制台
  - 服务器会响应所有请求并返回 "OK"
  - 按 Ctrl+C 停止服务器
        """
    )
    
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="监听地址 (默认: 0.0.0.0)"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=7788,
        help="监听端口 (默认: 7788)"
    )
    
    parser.add_argument(
        "--path",
        default="/debug",
        help="调试路径前缀 (默认: /debug)"
    )
    
    args = parser.parse_args()
    
    # 验证端口范围
    if not (1 <= args.port <= 65535):
        print("❌ 错误：端口必须在1-65535之间", file=sys.stderr)
        sys.exit(1)
    
    # 创建服务器
    server = HTTPServer((args.host, args.port), DebugHandler)
    server.debug_path = args.path
    
    # 显示启动信息
    print("=" * 60)
    print("🚀 HTTP调试服务器已启动")
    print("=" * 60)
    print(f"监听地址: {args.host}:{args.port}")
    print(f"调试路径: {args.path}*")
    print(f"访问URL: http://{args.host if args.host != '0.0.0.0' else 'localhost'}:{args.port}{args.path}")
    print("=" * 60)
    print("💡 提示：")
    print("   - 发送到调试路径的请求会被详细打印")
    print("   - 按 Ctrl+C 停止服务器")
    print("=" * 60)
    print()
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\n🛑 收到停止信号，正在关闭服务器...")
        server.shutdown()
        print("✅ 服务器已关闭")
        sys.exit(0)


if __name__ == "__main__":
    main()

