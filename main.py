#!/usr/bin/env python3
"""
CuteCuteyu-RAT - Remote Command Terminal
TCP Remote Command Execution Tool

主程序入口文件，负责导入和启动终端
"""

from terminal import CuteCuteyuRatTerminal


def main():
    """主函数"""
    terminal = CuteCuteyuRatTerminal()
    terminal.main_loop()


if __name__ == "__main__":
    main()
