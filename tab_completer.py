from enum import Enum


class SessionState(Enum):
    """会话状态枚举"""
    MAIN = "main"
    SESSION = "session"


class TabCompleter:
    """Tab键自动补全类"""
    
    def __init__(self):
        # 主界面命令列表
        self.main_commands = [
            'listen', 'sessions', 'session', 'jobs', 'stop', 'help', 'exit'
        ]
        
        # 会话界面命令列表
        self.session_commands = [
            'background', 'ai', 'exit'
        ]
        
        # 监听器参数补全
        self.listen_params = ['localhost', '127.0.0.1']
        
        # jobs命令参数补全
        self.jobs_params = ['-k']
        
    def get_completions(self, text, state, current_state, terminal_instance=None):
        """获取补全选项"""
        # 获取当前可用的命令列表
        if current_state == SessionState.MAIN:
            commands = self.main_commands
        else:
            commands = self.session_commands
        
        # 过滤匹配的命令
        matches = [cmd for cmd in commands if cmd.startswith(text)]
        
        # 处理session命令的参数补全
        if text.startswith('session ') and current_state == SessionState.MAIN:
            parts = text.split()
            if len(parts) == 2:
                # 补全会话ID - 使用实际的会话ID
                if terminal_instance and hasattr(terminal_instance, 'sessions'):
                    session_ids = [str(sid) for sid in terminal_instance.sessions.keys()]
                else:
                    session_ids = [str(sid) for sid in range(1, 10)]  # 备用方案
                
                partial_id = parts[1]
                matches = [f"session {sid}" for sid in session_ids if str(sid).startswith(partial_id)]
        
        # 处理listen命令的参数补全
        elif text.startswith('listen ') and current_state == SessionState.MAIN:
            parts = text.split()
            if len(parts) == 2:
                # 补全主机参数
                partial_host = parts[1]
                matches = [f"listen {host}" for host in self.listen_params if host.startswith(partial_host)]
            elif len(parts) == 3:
                # 补全端口参数
                partial_port = parts[2]
                common_ports = ['8888', '8080', '9999', '4444', '5555']
                matches = [f"listen {parts[1]} {port}" for port in common_ports if port.startswith(partial_port)]
        
        # 处理jobs命令的参数补全
        elif text.startswith('jobs ') and current_state == SessionState.MAIN:
            parts = text.split()
            if len(parts) == 2:
                # 补全jobs参数
                partial_param = parts[1]
                matches = [f"jobs {param}" for param in self.jobs_params if param.startswith(partial_param)]
            elif len(parts) == 3 and parts[1] == '-k':
                # 补全监听器ID
                partial_id = parts[2]
                if terminal_instance and hasattr(terminal_instance, 'listeners'):
                    listener_ids = [str(lid) for lid in terminal_instance.listeners.keys() 
                                   if terminal_instance.listeners[lid]['is_running']]
                else:
                    listener_ids = [str(lid) for lid in range(1, 10)]  # 备用方案
                
                matches = [f"jobs -k {lid}" for lid in listener_ids if str(lid).startswith(partial_id)]
        
        # 返回匹配的补全选项
        if state < len(matches):
            return matches[state]
        return None