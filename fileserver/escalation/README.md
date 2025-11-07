# Windows系统提权DLL - 从普通用户权限提升到SYSTEM权限

## 项目概述

这是一个Windows系统提权DLL，模仿Metasploit的`getsystem`功能，能够将普通用户权限提升到SYSTEM权限。该DLL通过获取SYSTEM进程的令牌，并使用该令牌创建新的SYSTEM权限进程。

## 功能特性

- **权限提升**: 从普通用户权限提升到SYSTEM权限
- **动态进程创建**: 支持创建任意指定的进程（如cmd.exe、powershell.exe等）
- **多级提权策略**: 采用渐进式权限申请策略，提高成功率
- **错误处理**: 完善的错误处理和日志输出
- **中文支持**: 支持中文控制台输出，解决乱码问题

## 文件结构

```
escalation_privilege_as_msf_getsystem/
├── main.cpp              # 主DLL源代码
├── test_dll.cpp          # 测试程序源代码
├── compile_dll.bat       # DLL编译脚本
├── compile_test.bat      # 测试程序编译脚本
├── privilege_escalation.dll  # 编译生成的DLL文件
├── test_dll.exe          # 编译生成的测试程序
└── README.md             # 本说明文件
```

## 编译说明

### 环境要求

- Windows操作系统（Windows 7/8/10/11）
- MinGW-w64或Visual Studio编译器
- 管理员权限（用于测试）

### 编译步骤

1. **编译DLL文件**:
   ```bash
   # 方法1: 使用批处理脚本
   compile_dll.bat
   
   # 方法2: 直接使用g++命令
   g++ -m64 -O2 -shared -o privilege_escalation.dll main.cpp -ladvapi32
   ```

2. **编译测试程序**:
   ```bash
   # 方法1: 使用批处理脚本
   compile_test.bat
   
   # 方法2: 直接使用g++命令
   g++ -m64 -O2 -o test_dll.exe test_dll.cpp
   ```

## 使用方法

### 1. 使用测试程序（推荐）

运行测试程序，选择要创建的进程类型：

```bash
# 以管理员权限运行测试程序
test_dll.exe
```

测试程序提供以下选项：
- **选项1**: 创建SYSTEM权限的cmd.exe
- **选项2**: 创建SYSTEM权限的powershell.exe
- **选项3**: 创建SYSTEM权限的notepad.exe

### 2. 直接调用DLL函数

您也可以在其他程序中动态加载并调用DLL的导出函数：

```cpp
#include <windows.h>
#include <iostream>

typedef int (*EscalateToSystemAndCreateProcessFunc)(const wchar_t* processName);

int main() {
    // 加载DLL
    HMODULE hDll = LoadLibrary(L"privilege_escalation.dll");
    if (!hDll) {
        std::wcout << L"加载DLL失败" << std::endl;
        return 1;
    }
    
    // 获取函数指针
    EscalateToSystemAndCreateProcessFunc escalateFunc = 
        (EscalateToSystemAndCreateProcessFunc)GetProcAddress(hDll, "EscalateToSystemAndCreateProcess");
    
    if (!escalateFunc) {
        std::wcout << L"获取函数失败" << std::endl;
        FreeLibrary(hDll);
        return 1;
    }
    
    // 调用提权函数
    int result = escalateFunc(L"cmd.exe");
    
    // 清理资源
    FreeLibrary(hDll);
    
    if (result == 0) {
        std::wcout << L"提权成功" << std::endl;
    } else {
        std::wcout << L"提权失败" << std::endl;
    }
    
    return result;
}
```

## 技术原理

### 提权流程

1. **启用调试权限**: 为当前进程启用`SE_DEBUG_NAME`权限，允许调试其他进程
2. **查找SYSTEM进程**: 枚举系统进程，优先查找`winlogon.exe`，其次查找`svchost.exe`
3. **获取SYSTEM令牌**: 从目标进程提取安全令牌
4. **创建SYSTEM进程**: 使用获取的令牌创建新的SYSTEM权限进程

### 关键API

- `OpenProcessToken()` - 打开进程令牌
- `DuplicateTokenEx()` - 复制令牌
- `CreateProcessWithTokenW()` - 使用令牌创建进程
- `CreateProcessAsUserW()` - 备选的进程创建方法
- `ImpersonateLoggedOnUser()` - 模拟令牌身份

## 安全注意事项

⚠️ **重要安全警告**:

1. **仅用于授权测试**: 本工具仅可用于授权的安全测试和教育目的
2. **管理员权限**: 测试时需要以管理员权限运行程序
3. **防病毒软件**: 某些防病毒软件可能会将此DLL检测为恶意软件
4. **系统兼容性**: 在不同Windows版本上的行为可能有所不同

## 故障排除

### 常见问题

1. **编译错误**: 
   - 确保安装了正确的编译器（MinGW-w64或Visual Studio）
   - 检查`advapi32.lib`库是否可用

2. **运行时报错**:
   - 确保以管理员权限运行程序
   - 检查DLL文件是否存在且可访问
   - 查看控制台输出的详细错误信息

3. **提权失败**:
   - 某些安全策略可能阻止令牌复制
   - 尝试使用不同的目标进程（winlogon.exe vs svchost.exe）

### 调试技巧

- 启用详细日志输出以了解提权过程
- 使用Process Monitor等工具监控系统调用
- 检查Windows事件日志获取更多信息

## 许可证

本项目仅用于教育和授权安全测试目的。使用者需遵守当地法律法规。

## 更新日志

### v1.0 (2025-11-07)
- 初始版本发布
- 实现基本的提权功能
- 添加测试程序和编译脚本
- 完善错误处理和日志输出

## 联系方式

如有问题或建议，请联系项目维护者。

---

**免责声明**: 本工具仅用于授权的安全测试和教育目的。使用者需对使用本工具产生的后果负责。