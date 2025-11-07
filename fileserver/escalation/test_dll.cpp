#include <windows.h>
#include <iostream>
#include <string>

// DLL function type definition
typedef int (*EscalateToSystemAndCreateProcessFunc)(const char* processName);

// Global variable: process name to launch (user can modify here)
const char* DEFAULT_PROCESS_NAME = "client.exe";

int main() {
    std::cout << "DLL Privilege Escalation Test Program" << std::endl;
    std::cout << "=====================================" << std::endl;
    
    // Load DLL
    HMODULE hDll = LoadLibraryA("privilege_escalation.dll");
    if (!hDll) {
        std::cout << "Error: Unable to load DLL file privilege_escalation.dll" << std::endl;
        std::cout << "Please ensure the DLL file is in the current directory" << std::endl;
        return 1;
    }
    
    // Get function address
    EscalateToSystemAndCreateProcessFunc escalateFunc = 
        (EscalateToSystemAndCreateProcessFunc)GetProcAddress(hDll, "EscalateToSystemAndCreateProcess");
    
    if (!escalateFunc) {
        std::cout << "Error: Unable to find exported function EscalateToSystemAndCreateProcess" << std::endl;
        FreeLibrary(hDll);
        return 1;
    }
    
    std::cout << "DLL loaded successfully!" << std::endl;
    std::cout << std::endl;
    
    // Directly use default process name
    const char* processName = DEFAULT_PROCESS_NAME;
    
    std::cout << std::endl;
    std::cout << "Attempting privilege escalation and creating process: " << processName << std::endl;
    std::cout << "Note: This operation requires administrator privileges to succeed!" << std::endl;
    std::cout << std::endl;
    
    // Call DLL function
    int result = escalateFunc(processName);
    
    std::cout << std::endl;
    if (result == 0) {
        std::cout << "✓ Privilege escalation operation successful!" << std::endl;
        std::cout << "Process " << processName << " should have been launched with SYSTEM privileges" << std::endl;
    } else {
        std::cout << "✗ Privilege escalation operation failed, error code: " << result << std::endl;
        std::cout << "Possible reasons:" << std::endl;
        std::cout << "- Program is not running with administrator privileges" << std::endl;
        std::cout << "- No suitable SYSTEM process available in the system" << std::endl;
        std::cout << "- Specified process does not exist or cannot be launched" << std::endl;
    }
    
    // Clean up resources
    FreeLibrary(hDll);
    
    return 0;
}