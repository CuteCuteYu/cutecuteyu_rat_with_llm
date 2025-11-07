import socket
import threading
import http.server
import socketserver
import os


class WebServerManager:
    """Web服务器管理器"""
    
    def __init__(self):
        self.webservers = {}  # {webserver_id: {thread, directory, port, is_running}}
        self.next_webserver_id = 1
    
    def start_webserver(self, directory=None, port=8000):
        """启动Web服务器
        
        Args:
            directory: Web服务器目录，默认为当前项目下的escalation目录
            port: Web服务器端口，默认为8000
            
        Returns:
            webserver_id: 启动的Web服务器ID，失败返回None
        """
        webserver_id = self.next_webserver_id
        self.next_webserver_id += 1
        
        # 设置默认目录
        if directory is None:
            # 获取当前文件所在目录的父目录
            current_dir = os.path.dirname(os.path.abspath(__file__))
            directory = os.path.join(current_dir, "fileserver")
        
        # 检查目录是否存在
        if not os.path.exists(directory):
            print(f"[-] Web服务器目录不存在: {directory}")
            return None
        
        def webserver_thread(webserver_id):
            try:
                # 切换到指定目录
                os.chdir(directory)
                
                # 创建HTTP服务器
                handler = http.server.SimpleHTTPRequestHandler
                
                with socketserver.TCPServer(("", port), handler) as httpd:
                    print(f"[+] Web服务器 {webserver_id} 启动在端口 {port}")
                    print(f"[+] 服务目录: {directory}")
                    print(f"[+] 访问地址: http://0.0.0.0:{port} (本地访问: http://localhost:{port})")
                    
                    # 设置超时以便检查停止标志
                    httpd.timeout = 1
                    
                    while self.webservers[webserver_id]['is_running']:
                        try:
                            httpd.handle_request()
                        except socket.timeout:
                            continue
                        except Exception as e:
                            if self.webservers[webserver_id]['is_running']:
                                print(f"[-] Web服务器 {webserver_id} 错误: {e}")
                            break
                
                print(f"[-] Web服务器 {webserver_id} 已停止")
                
            except Exception as e:
                print(f"[-] Web服务器 {webserver_id} 启动失败: {e}")
        
        # 创建Web服务器线程
        thread = threading.Thread(target=webserver_thread, args=(webserver_id,))
        thread.daemon = True
        
        # 保存Web服务器信息
        self.webservers[webserver_id] = {
            'thread': thread,
            'directory': directory,
            'port': port,
            'is_running': True
        }
        
        thread.start()
        return webserver_id
    
    def stop_webserver(self, webserver_id):
        """停止指定Web服务器
        
        Args:
            webserver_id: Web服务器ID
            
        Returns:
            bool: 是否成功停止
        """
        if webserver_id not in self.webservers:
            print(f"[-] Web服务器 {webserver_id} 不存在")
            return False
        
        if not self.webservers[webserver_id]['is_running']:
            print(f"[-] Web服务器 {webserver_id} 已经停止")
            return False
        
        # 停止Web服务器
        self.webservers[webserver_id]['is_running'] = False
        print(f"[+] Web服务器 {webserver_id} 正在停止...")
        return True
    
    def show_webservers(self):
        """显示所有Web服务器"""
        # 清理已停止的Web服务器记录
        stopped_webservers = [wid for wid, info in self.webservers.items() if not info['is_running']]
        for webserver_id in stopped_webservers:
            del self.webservers[webserver_id]
        
        # 只显示正在运行的Web服务器
        running_webservers = [wid for wid, info in self.webservers.items() if info['is_running']]
        if not running_webservers:
            print("[-] 没有运行的Web服务器")
            return
        
        print("\n运行中的Web服务器:")
        print("ID\t端口\t目录")
        print("-" * 80)
        for webserver_id in running_webservers:
            webserver_info = self.webservers[webserver_id]
            print(f"{webserver_id}\t{webserver_info['port']}\t{webserver_info['directory']}")
        print()
    
    def get_running_webservers(self):
        """获取正在运行的Web服务器ID列表
        
        Returns:
            list: 正在运行的Web服务器ID列表
        """
        # 清理已停止的Web服务器记录
        stopped_webservers = [wid for wid, info in self.webservers.items() if not info['is_running']]
        for webserver_id in stopped_webservers:
            del self.webservers[webserver_id]
        
        return [wid for wid, info in self.webservers.items() if info['is_running']]
    
    def is_webserver_running(self, webserver_id):
        """检查指定Web服务器是否正在运行
        
        Args:
            webserver_id: Web服务器ID
            
        Returns:
            bool: 是否正在运行
        """
        if webserver_id not in self.webservers:
            return False
        return self.webservers[webserver_id]['is_running']