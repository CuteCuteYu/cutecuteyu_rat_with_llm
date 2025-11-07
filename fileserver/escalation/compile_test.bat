@echo off
echo 正在编译DLL测试程序...

:: 设置G++编译器路径（根据您的实际安装路径调整）
set GPP_PATH=g++

:: 编译测试程序
%GPP_PATH% -m64 -O2 -o test_dll.exe test_dll.cpp

if %errorlevel% equ 0 (
    echo 编译成功！生成文件: test_dll.exe
    echo.
    echo 使用说明：
    echo 1. 首先运行 compile_dll.bat 编译DLL
    echo 2. 然后运行此程序进行测试
    echo 3. 程序将加载DLL并调用提权函数
    echo 4. 需要以管理员权限运行测试程序
) else (
    echo 编译失败！请检查G++安装和路径设置
)

pause