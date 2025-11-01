# CuteCuteyu-RAT: TCP Remote Command Execution System with LLM Integration

## Language Versions

This documentation is available in multiple languages:
- **English**: [README.md](README.md) | [Command Documentation](command.md)
- **中文 (Chinese)**: [README-zh-cn.md](README-zh-cn.md) | [命令文档](command-zh-cn.md)

---

## Overview

CuteCuteyu-RAT is a powerful TCP remote command execution system that integrates Large Language Model (LLM) capabilities for intelligent command generation and advanced terminal interaction. This system provides comprehensive remote management functionality with AI-assisted automation.

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
├── server.py              # Main server application
├── client.py              # Client application
├── terminal.py            # Terminal interface and command processing
├── tab_completer.py       # Tab auto-completion functionality
├── llm_info.py            # LLM API configuration
├── listener.py            # Listener management
├── session.py             # Session management
├── command.md             # Complete command documentation (English)
├── README.md              # Project documentation (English)
├── command-zh-cn.md       # Complete command documentation (Chinese)
├── README-zh-cn.md        # Project documentation (Chinese)
└── requirements.txt       # Python dependencies
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
python -m rat_with_llm.server
```

#### Method 2: Using pip
```bash
# Install dependencies
pip install -r requirements.txt

# Run the server
python -m rat_with_llm.server
```

### Running the System

1. **Start the Server**:
   ```bash
   python -m rat_with_llm.server
   ```

2. **Configure Listeners**:
   - Use the `listen` command to start TCP listeners
   - Default configuration: localhost:8888
   - Support for multiple listeners on different ports

3. **Client Connection**:
   ```bash
   python -m rat_with_llm.client <server_ip> <server_port>
   ```

## Usage Instructions

### Basic Operation Flow

1. **Start the server** and configure listeners
2. **Connect clients** to the server
3. **Manage sessions** using the interactive terminal
4. **Execute commands** on target systems
5. **Use AI features** for intelligent command generation

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