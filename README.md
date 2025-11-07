# CuteCuteyu-RAT: TCP Remote Command Execution System with LLM Integration

## Language Versions

This documentation is available in multiple languages:

- **English**: [README.md](README.md) | [Command Documentation](command.md)
- **中文 (Chinese)**: [README-zh-cn.md](README-zh-cn.md) | [命令文档](command-zh-cn.md)

---

## Overview

CuteCuteyu-RAT is a powerful TCP remote command execution system that integrates Large Language Model (LLM) capabilities for intelligent command generation and advanced terminal interaction. This system provides comprehensive remote management functionality with AI-assisted automation.

![](mytest.gif)

## Core Features

### Basic Functionality

- **TCP Communication**: Reliable TCP-based client-server communication
- **Remote Command Execution**: Execute arbitrary system commands on target machines
- **Multi-session Management**: Support for multiple concurrent sessions
- **Listener Management**: Flexible listener configuration and management
- **Real-time Interaction**: Interactive terminal with real-time command execution

### Advanced Features

- **LLM Integration**: DeepSeek AI-powered intelligent command generation
- **Interactive Terminal**: User-friendly command-line interface
- **Tab Auto-completion**: Intelligent command and parameter completion
- **Background Session Management**: Session persistence and quick switching
- **Multi-listener Support**: Concurrent operation of multiple listeners

### Security Features

- **Connection Monitoring**: Real-time connection status tracking
- **Session Isolation**: Independent session management
- **Resource Cleanup**: Automatic cleanup of resources upon disconnection
- **Error Handling**: Comprehensive error handling and recovery mechanisms

## Project Structure

```
rat_with_llm/
├── .gitignore
├── .python-version
├── LICENSE
├── README-zh-cn.md
├── README.md
├── client/
│   └── client.py         # Client application
├── command-zh-cn.md
├── command.md
├── fileserver/
│   └── escalation/       # Privilege escalation files
│       ├── README.md
│       ├── client.exe
│       ├── compile_dll.bat
│       ├── compile_test.bat
│       ├── main.cpp
│       ├── privilege_escalation.dll
│       ├── test_dll.cpp
│       └── test_dll.exe
├── llm_info.py           # LLM API configuration
├── main.py               # Main server application entry point
├── mytest.gif
├── ps.py                 # PowerShell code generation
├── pyproject.toml        # Project configuration and dependencies
├── session.py            # Session management
├── tab_completer.py      # Tab auto-completion functionality
├── terminal.py           # Terminal interface and command processing
├── uv.lock               # uv dependency lock file
└── webserver.py          # Web server functionality
```

## Installation and Running

### Prerequisites

- Python 3.8 or higher
- Windows 10/11 or Windows Server 2016+
- Internet connection (for LLM functionality)

### Installation Methods

#### Method 1: Using uv (Recommended)

```bash
# Install uv if not already installed
pip install uv

# Clone and install the project
uv sync

# Run the server
uv run python main.py
```

#### Method 2: Using pip

```bash
# Install dependencies
pip install -r requirements.txt

# Run the server
python main.py
```

### Running the System

1. **Start the Server**:

   ```bash
   python main.py
   ```
2. **Configure Listeners**:

   - Use the `listen` command to start TCP listeners
   - Default configuration: localhost:8888
   - Support for multiple listeners on different ports
3. **Client Connection**:

   ```bash
   python client.py <server_ip> <server_port>
   ```

## Usage Instructions

### Basic Operation Flow

1. **Start the server** and configure listeners
2. **Connect clients** to the server
3. **Manage sessions** using the interactive terminal
4. **Execute commands** on target systems
5. **Use AI features** for intelligent command generation

### Web Server Management

The system includes built-in web server functionality for file download services, particularly useful for privilege escalation operations:

1. **Start Web Server**

   ```bash
   rat> webserver
   ```

   - Default port: 8000
   - Default directory: `fileserver/`
   - Automatically assigns Web Server ID
2. **View Running Web Servers**

   ```bash
   rat> webservers
   ```

   - Displays all running web servers
   - Includes ID, port, and service directory information
3. **Stop Web Server**

   ```bash
   rat> webserver -k 1
   ```

   - Stops the web server with specified ID
   - Supports Tab key auto-completion for Web Server ID
4. **Web Server Usage**

   - Provides file download services for clients
   - Supports privilege escalation file distribution
   - Supports custom directories and ports

### Privilege Escalation Process

The system supports privilege escalation functionality through the `getsystem` command:

1. **Start File Server**

   ```bash
   rat> webserver
   ```

   This starts an HTTP file server that provides the necessary files for privilege escalation.
2. **Run Client as Administrator**
   Run the client program with administrator privileges:

   ```bash
   uv run client.py
   ```
3. **Execute Privilege Escalation Command**
   Enter the `getsystem` command in the session interface:

   ```bash
   session 1> getsystem
   ```
4. **Automatic Privilege Escalation Process**

   - Client automatically downloads privilege escalation files from the file server
   - After download completion, automatically executes the privilege escalation program
   - Client automatically disconnects after privilege escalation is completed

**Note**: Privilege escalation requires running the client with administrator privileges and the file server must be running normally.

### Configuration Options

#### Server Configuration

- **Default Port**: 8888
- **Host Binding**: localhost or 0.0.0.0 for all interfaces
- **Session Timeout**: 5 seconds
- **Max Connections**: Configurable based on system resources

#### LLM Configuration

Configure API settings in `llm_info.py`:

- API endpoint
- Authentication credentials
- Request timeout settings

## Security Considerations

### Important Warnings

- ⚠️ **This system allows remote execution of arbitrary system commands**
- ⚠️ **Use only in controlled and trusted environments**
- ⚠️ **Ensure proper network isolation and access controls**
- ⚠️ **Monitor system activity and maintain audit logs**

### Security Best Practices

1. **Network Isolation**: Deploy in isolated network segments
2. **Access Control**: Implement strict access controls
3. **Monitoring**: Maintain comprehensive activity logs
4. **Regular Updates**: Keep the system and dependencies updated

## Technical Implementation

### Architecture Overview

- **Client-Server Model**: TCP-based communication architecture
- **Multi-threading**: Concurrent session and listener management
- **Modular Design**: Separated functionality for maintainability
- **Error Resilience**: Robust error handling and recovery

### Key Components

- **Server Module**: Main application entry point and coordination
- **Client Module**: Target system connection and command execution
- **Terminal Interface**: User interaction and command processing
- **LLM Integration**: AI-powered command generation and execution

## Dependencies

### Core Dependencies

- **Python Standard Library**: sockets, threading, subprocess, etc.
- **External Libraries**: LLM API client libraries

### Optional Dependencies

- Development tools for testing and debugging
- Network monitoring tools for deployment

## License

This project is provided for educational and research purposes. Users are responsible for complying with all applicable laws and regulations.

*For detailed command usage and advanced features, please refer to the [command documentation](command.md).*
