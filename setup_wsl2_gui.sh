#!/bin/bash
"""
WSL2 GUI设置脚本
自动配置WSL2环境以支持GUI应用程序
"""

echo "🔧 WSL2 GUI设置脚本"
echo "===================="

# 检查是否在WSL2中
if ! grep -q Microsoft /proc/version; then
    echo "❌ 这不是WSL环境"
    exit 1
fi

echo "✅ 检测到WSL环境"

# 设置DISPLAY环境变量
echo "📺 设置DISPLAY环境变量..."
export DISPLAY=:0

# 检查是否已经在bashrc中
if ! grep -q "export DISPLAY=:0" ~/.bashrc; then
    echo "export DISPLAY=:0" >> ~/.bashrc
    echo "✅ 已添加到~/.bashrc"
else
    echo "✅ DISPLAY设置已存在"
fi

# 检查X11应用程序
echo "🔍 检查X11应用程序..."
if command -v xeyes >/dev/null 2>&1; then
    echo "✅ xeyes已安装"
else
    echo "❌ xeyes未安装，正在安装..."
    sudo apt update
    sudo apt install -y x11-apps
fi

# 测试X11连接
echo "🧪 测试X11连接..."
if timeout 3 xeyes >/dev/null 2>&1; then
    echo "✅ X11连接正常"
else
    echo "❌ X11连接失败"
    echo "💡 请在Windows上安装VcXsrv或Xming"
    echo "💡 下载地址: https://sourceforge.net/projects/vcxsrv/"
fi

# 测试pygame
echo "🎮 测试pygame..."
python3 -c "
import pygame
pygame.init()
screen = pygame.display.set_mode((100, 100))
pygame.display.set_caption('Test')
import time
time.sleep(1)
pygame.quit()
print('✅ pygame测试成功')
" 2>/dev/null || echo "❌ pygame测试失败"

echo ""
echo "📋 设置完成！"
echo ""
echo "🚀 下一步操作："
echo "1. 在Windows上安装VcXsrv: https://sourceforge.net/projects/vcxsrv/"
echo "2. 启动VcXsrv并勾选'Disable access control'"
echo "3. 在WSL2中运行: python snake_gui.py"
echo ""
echo "🧪 测试命令："
echo "xeyes &                    # 测试X11"
echo "python test_gui_diagnostic.py  # 测试pygame"
echo "python snake_gui.py        # 运行Snake游戏" 