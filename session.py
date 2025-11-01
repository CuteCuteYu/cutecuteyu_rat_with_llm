import json
import time
import socket


class Session:
    """会话管理类"""
    
    def __init__(self, session_id, client_socket, client_address):
        self.session_id = session_id
        self.client_socket = client_socket
        self.client_address = client_address
        self.is_active = True
        self.last_activity = time.time()
    
    def send_command(self, command):
        """向会话发送命令"""
        try:
            message = {
                'type': 'command',
                'command': command
            }
            self.client_socket.send(json.dumps(message).encode('utf-8'))
            return True
        except Exception as e:
            print(f"发送命令失败: {e}")
            self.is_active = False
            return False
    
    def receive_response(self, timeout=5):
        """接收会话响应，支持超时"""
        try:
            # 设置socket超时
            self.client_socket.settimeout(timeout)
            data = self.client_socket.recv(4096).decode('utf-8')
            if data:
                self.last_activity = time.time()
                return json.loads(data)
        except socket.timeout:
            return None  # 超时返回None而不是异常
        except Exception as e:
            self.is_active = False
        finally:
            # 恢复socket为非阻塞模式
            self.client_socket.settimeout(None)
        return None
    
    def disconnect(self):
        """断开会话连接"""
        try:
            if self.client_socket:
                self.client_socket.close()
            self.is_active = False
            return True
        except Exception as e:
            print(f"断开会话 {self.session_id} 连接失败: {e}")
            return False