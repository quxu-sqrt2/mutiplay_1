#!/usr/bin/env python3
"""
GUI诊断工具
检测WSL GUI问题并提供解决方案
"""

import os
import sys
import subprocess
import pygame

def test_x11_connection():
    """测试X11连接"""
    print("🔍 测试X11连接...")
    
    try:
        # 测试xeyes
        result = subprocess.run(['xeyes'], timeout=2, capture_output=True)
        if result.returncode == 0:
            print("✅ xeyes运行成功")
            return True
        else:
            print(f"❌ xeyes运行失败: {result.stderr.decode()}")
            return False
    except subprocess.TimeoutExpired:
        print("✅ xeyes运行成功（超时停止）")
        return True
    except Exception as e:
        print(f"❌ xeyes测试失败: {e}")
        return False

def test_pygame_gui():
    """测试pygame GUI"""
    print("\n🔍 测试pygame GUI...")
    
    try:
        pygame.init()
        print("✅ pygame初始化成功")
        
        # 创建小窗口测试
        screen = pygame.display.set_mode((300, 200))
        pygame.display.set_caption("GUI测试")
        print("✅ 窗口创建成功")
        
        # 绘制一些内容
        screen.fill((255, 255, 255))
        pygame.draw.rect(screen, (255, 0, 0), (50, 50, 100, 100))
        
        # 更新显示
        pygame.display.flip()
        print("✅ 显示更新成功")
        
        # 等待2秒
        import time
        time.sleep(2)
        
        pygame.quit()
        print("✅ pygame GUI测试成功")
        return True
        
    except Exception as e:
        print(f"❌ pygame GUI测试失败: {e}")
        return False

def check_windows_x11_server():
    """检查Windows X11服务器"""
    print("\n🔍 检查Windows X11服务器...")
    
    # 检查常见的X11服务器进程
    x11_servers = ['vcxsrv', 'xming', 'xserver']
    
    try:
        # 在Windows上检查进程
        result = subprocess.run(['tasklist'], capture_output=True, text=True)
        if result.returncode == 0:
            output = result.stdout.lower()
            found_server = False
            
            for server in x11_servers:
                if server in output:
                    print(f"✅ 发现X11服务器: {server}")
                    found_server = True
            
            if not found_server:
                print("❌ 未发现X11服务器")
                return False
            else:
                return True
        else:
            print("❌ 无法检查Windows进程")
            return False
    except Exception as e:
        print(f"❌ 检查X11服务器失败: {e}")
        return False

def provide_solutions():
    """提供解决方案"""
    print("\n" + "="*50)
    print("🔧 GUI问题解决方案")
    print("="*50)
    
    print("\n📋 解决方案按优先级排序:")
    
    print("\n1️⃣ 在Windows上安装VcXsrv (推荐)")
    print("   - 下载: https://sourceforge.net/projects/vcxsrv/")
    print("   - 安装后启动XLaunch")
    print("   - 选择 'Multiple windows'")
    print("   - 勾选 'Disable access control'")
    print("   - 在WSL中运行: export DISPLAY=:0")
    
    print("\n2️⃣ 使用WSL2 GUI支持 (Windows 11)")
    print("   - 在Windows 11中启用WSL2 GUI支持")
    print("   - 运行: wsl --update")
    print("   - 重启WSL")
    
    print("\n3️⃣ 安装Xming")
    print("   - 下载: https://sourceforge.net/projects/xming/")
    print("   - 安装并启动")
    
    print("\n4️⃣ 使用SSH X11转发")
    print("   - 通过SSH连接WSL")
    print("   - 启用X11转发")
    
    print("\n🚀 快速测试命令:")
    print("   export DISPLAY=:0")
    print("   python snake_gui.py")

def main():
    """主函数"""
    print("🎮 WSL GUI诊断工具")
    print("="*50)
    
    # 检查环境变量
    display = os.environ.get('DISPLAY')
    print(f"当前DISPLAY设置: {display}")
    
    # 测试X11连接
    x11_ok = test_x11_connection()
    
    # 测试pygame GUI
    pygame_ok = test_pygame_gui()
    
    # 检查Windows X11服务器
    x11_server_ok = check_windows_x11_server()
    
    print("\n" + "="*50)
    print("📊 诊断结果:")
    print(f"X11连接: {'✅' if x11_ok else '❌'}")
    print(f"pygame GUI: {'✅' if pygame_ok else '❌'}")
    print(f"X11服务器: {'✅' if x11_server_ok else '❌'}")
    
    if x11_ok and pygame_ok:
        print("\n🎉 GUI工作正常！可以运行: python snake_gui.py")
    else:
        print("\n⚠️  GUI有问题，需要配置X11服务器")
        provide_solutions()

if __name__ == "__main__":
    main() 