@echo off
echo Compiling 64-bit privilege escalation DLL...

:: Compile 64-bit DLL
g++ -m64 -O2 -shared -o privilege_escalation.dll main.cpp -ladvapi32

if %errorlevel% equ 0 (
    echo Compilation successful! Generated file: privilege_escalation.dll
    echo.
    echo DLL export function:
    echo extern "C" DLL_EXPORT int EscalateToSystemAndCreateProcess(const char* processName)
    echo Parameters: processName - process to create (e.g., cmd.exe, powershell.exe, etc.)
    echo Return value: 0 for success, non-zero for failure
    echo.
    echo Usage:
    echo 1. Load this DLL in other programs
    echo 2. Call EscalateToSystemAndCreateProcess function with process name
    echo 3. Function will escalate to SYSTEM privilege and create specified process
) else (
    echo Compilation failed! Please check G++ installation and path settings
)

pause