#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
简单HTTP服务器
监听指定端口，接收GET和POST请求，返回预定义的JSON响应数据
用于测试、调试和模拟API服务
"""

from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import argparse
import sys
from datetime import datetime

# 默认响应数据
#RESPONSE_DATA = {
#    "code": 0,
#    "msg": "ok",
#    "data": {
#        "name": "simple-server",
#        "version": "1.0"
#    }
#}
RESPONSE_DATA = {
    "logId": 1,
    "logDateTim": 1767773825497,
    "handleCode": 200,
    "handleMsg": "任务执行成功"
}


class SimpleRequestHandler(BaseHTTPRequestHandler):
    """HTTP请求处理器"""
    
    def log_message(self, format, *args):
        """自定义日志格式"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {format % args}")
    
    def do_GET(self):
        """处理GET请求"""
        self.log_message(f"GET请求: {self.path}")
        self.respond()
    
    def do_POST(self):
        """处理POST请求"""
        self.log_message(f"POST请求: {self.path}")
        
        # 读取请求体
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 0:
                body = self.rfile.read(content_length)
                body_str = body.decode('utf-8')
                self.log_message(f"请求体: {body_str}")
                
                # 尝试解析JSON
                try:
                    body_json = json.loads(body_str)
                    self.log_message(f"解析的JSON: {json.dumps(body_json, ensure_ascii=False)}")
                except json.JSONDecodeError:
                    self.log_message("请求体不是有效的JSON格式")
        except Exception as e:
            self.log_message(f"读取请求体时出错: {str(e)}")
        
        self.respond()
    
    def do_PUT(self):
        """处理PUT请求"""
        self.log_message(f"PUT请求: {self.path}")
        self.do_POST()  # PUT请求处理方式与POST相同
    
    def do_DELETE(self):
        """处理DELETE请求"""
        self.log_message(f"DELETE请求: {self.path}")
        self.respond()
    
    def respond(self):
        """发送响应"""
        try:
            # 设置响应头
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")  # 允许跨域
            self.end_headers()
            
            # 发送JSON响应
            response_json = json.dumps(RESPONSE_DATA, ensure_ascii=False)
            self.wfile.write(response_json.encode('utf-8'))
            
            self.log_message(f"响应: {response_json}")
        except Exception as e:
            self.log_message(f"发送响应时出错: {str(e)}")


def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="简单HTTP服务器 - 监听指定端口并返回预定义的JSON响应",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s                    # 使用默认端口8080
  %(prog)s --port 3000        # 监听3000端口
  %(prog)s --port 9000 --host 127.0.0.1  # 只监听本地地址
        """
    )
    
    parser.add_argument(
        '--port', '-p',
        type=int,
        default=8080,
        help='监听端口 (默认: 8080)'
    )
    
    parser.add_argument(
        '--host', '-H',
        type=str,
        default='0.0.0.0',
        help='监听地址 (默认: 0.0.0.0，监听所有网络接口)'
    )
    
    return parser.parse_args()


def main():
    """主函数"""
    args = parse_arguments()
    
    # 验证端口范围
    if not (1 <= args.port <= 65535):
        print(f"错误: 端口号必须在1-65535之间，当前值: {args.port}", file=sys.stderr)
        sys.exit(1)
    
    # 创建服务器
    try:
        server = HTTPServer((args.host, args.port), SimpleRequestHandler)
        
        print("=" * 60)
        print("简单HTTP服务器已启动")
        print("=" * 60)
        print(f"监听地址: {args.host}")
        print(f"监听端口: {args.port}")
        print(f"访问地址: http://{args.host if args.host != '0.0.0.0' else 'localhost'}:{args.port}")
        print("=" * 60)
        print("支持的请求方法: GET, POST, PUT, DELETE")
        print("响应格式: JSON")
        print("按 Ctrl+C 停止服务器")
        print("=" * 60)
        print()
        
        # 启动服务器
        server.serve_forever()
        
    except OSError as e:
        if e.errno == 48:  # Address already in use
            print(f"错误: 端口 {args.port} 已被占用，请选择其他端口", file=sys.stderr)
        elif e.errno == 49:  # Can't assign requested address
            print(f"错误: 无法绑定地址 {args.host}，请检查地址是否正确", file=sys.stderr)
        else:
            print(f"错误: 启动服务器失败 - {str(e)}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n" + "=" * 60)
        print("服务器已停止")
        print("=" * 60)
        server.shutdown()
        sys.exit(0)
    except Exception as e:
        print(f"错误: 发生未预期的错误 - {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

