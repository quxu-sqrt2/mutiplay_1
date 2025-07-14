#!/usr/bin/env python3
"""
简单GUI测试
检查pygame是否能真正显示窗口
"""

import pygame
import sys
import time

def main():
    print("🎮 简单GUI测试")
    print("=" * 30)
    
    try:
        # 初始化pygame
        pygame.init()
        print("✅ pygame初始化成功")
        
        # 创建小窗口
        screen = pygame.display.set_mode((400, 300))
        pygame.display.set_caption("GUI测试 - 按ESC退出")
        print("✅ 窗口创建成功")
        
        # 设置颜色
        WHITE = (255, 255, 255)
        RED = (255, 0, 0)
        BLUE = (0, 0, 255)
        
        # 主循环
        running = True
        clock = pygame.time.Clock()
        start_time = time.time()
        
        print("🖥️  如果看到窗口，说明GUI工作正常")
        print("⏹️  按ESC键退出测试")
        
        while running:
            current_time = time.time()
            
            # 处理事件
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_SPACE:
                        print("⏸️  空格键被按下")
            
            # 清屏
            screen.fill(WHITE)
            
            # 绘制移动的图形
            elapsed = current_time - start_time
            
            # 移动的红色矩形
            x = int(50 + 100 * (elapsed % 2))
            pygame.draw.rect(screen, RED, (x, 50, 80, 60))
            
            # 移动的蓝色圆形
            y = int(150 + 50 * (elapsed % 1))
            pygame.draw.circle(screen, BLUE, (200, y), 30)
            
            # 显示文本
            font = pygame.font.Font(None, 36)
            text = font.render(f"时间: {elapsed:.1f}s", True, (0, 0, 0))
            screen.blit(text, (10, 10))
            
            # 更新显示
            pygame.display.flip()
            clock.tick(60)
        
        pygame.quit()
        print("✅ GUI测试完成")
        return True
        
    except Exception as e:
        print(f"❌ GUI测试失败: {e}")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("🎉 GUI工作正常！现在可以运行: python snake_gui.py")
    else:
        print("❌ GUI有问题，需要配置X11服务器") 