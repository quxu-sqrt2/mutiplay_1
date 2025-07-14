#!/usr/bin/env python3
"""
无头模式Snake游戏
在没有GUI的环境中运行，保存截图而不是显示窗口
"""

import os
import sys
import time
import pygame
import numpy as np
from typing import Optional, Tuple, Dict, Any
from games.snake import SnakeGame, SnakeEnv
from agents import RandomBot, SnakeAI, SmartSnakeAI, HumanAgent

# 设置无头模式
os.environ['SDL_VIDEODRIVER'] = 'dummy'

# 颜色定义
COLORS = {
    'WHITE': (255, 255, 255),
    'BLACK': (0, 0, 0),
    'RED': (255, 0, 0),
    'BLUE': (0, 0, 255),
    'GREEN': (0, 255, 0),
    'GRAY': (128, 128, 128),
    'LIGHT_GRAY': (211, 211, 211),
    'DARK_GRAY': (64, 64, 64),
    'YELLOW': (255, 255, 0),
    'ORANGE': (255, 165, 0),
    'CYAN': (0, 255, 255)
}

class HeadlessSnakeGame:
    """无头模式Snake游戏"""
    
    def __init__(self, board_size=20):
        # 初始化pygame（无头模式）
        pygame.init()
        
        self.board_size = board_size
        self.cell_size = 25
        self.margin = 50
        
        self.window_width = self.board_size * self.cell_size + self.margin * 2 + 300
        self.window_height = self.board_size * self.cell_size + self.margin * 2
        
        # 创建虚拟屏幕
        self.screen = pygame.display.set_mode((self.window_width, self.window_height))
        pygame.display.set_caption("Snake AI Battle (Headless)")
        
        # 字体
        self.font_large = pygame.font.Font(None, 36)
        self.font_medium = pygame.font.Font(None, 24)
        self.font_small = pygame.font.Font(None, 18)
        
        # 游戏状态
        self.env = SnakeEnv(board_size=self.board_size)
        self.human_agent = HumanAgent(name="Human Player", player_id=1)
        self.ai_agent = SnakeAI(name="Snake AI", player_id=2)
        self.current_agent = self.human_agent
        self.game_over = False
        self.winner = None
        self.selected_ai = "SnakeAI"
        
        # 游戏计时
        self.last_update = time.time()
        self.update_interval = 0.5  # 500ms更新一次
        self.frame_count = 0
        
        self.reset_game()
    
    def reset_game(self):
        """重置游戏"""
        self.env.reset()
        self.game_over = False
        self.winner = None
        self.current_agent = self.human_agent
        self.last_update = time.time()
        self.frame_count = 0
    
    def update_game(self):
        """更新游戏状态"""
        if self.game_over:
            return
        
        current_time = time.time()
        
        # AI思考时间
        if isinstance(self.current_agent, (SnakeAI, SmartSnakeAI, RandomBot)):
            if current_time - self.last_update < 0.5:  # 500ms思考时间
                return
            
            # AI移动
            state = self.env.game.get_state()
            action = self.current_agent.get_action(state, self.env)
            
            if action is not None:
                self.env.step(action)
                
                # 检查游戏是否结束
                if self.env.game.is_terminal():
                    self.game_over = True
                    self.winner = self.env.game.get_winner()
                    return
                
                # 切换回人类玩家
                self.current_agent = self.human_agent
            
            self.last_update = current_time
    
    def draw(self):
        """绘制游戏界面"""
        # 清空屏幕
        self.screen.fill(COLORS['WHITE'])
        
        # 绘制游戏区域
        self._draw_snake_game()
        
        # 绘制UI
        self._draw_ui()
        
        # 绘制游戏状态
        self._draw_game_status()
        
        # 保存截图
        filename = f"snake_frame_{self.frame_count:04d}.png"
        pygame.image.save(self.screen, filename)
        print(f"📸 保存截图: {filename}")
        
        self.frame_count += 1
    
    def _draw_snake_game(self):
        """绘制贪吃蛇游戏"""
        # 绘制游戏区域背景
        game_rect = pygame.Rect(
            self.margin, 
            self.margin,
            self.board_size * self.cell_size,
            self.board_size * self.cell_size
        )
        pygame.draw.rect(self.screen, COLORS['LIGHT_GRAY'], game_rect)
        pygame.draw.rect(self.screen, COLORS['BLACK'], game_rect, 2)
        
        # 绘制网格
        for i in range(self.board_size + 1):
            # 垂直线
            x = self.margin + i * self.cell_size
            pygame.draw.line(self.screen, COLORS['GRAY'], 
                           (x, self.margin), 
                           (x, self.margin + self.board_size * self.cell_size), 1)
            # 水平线
            y = self.margin + i * self.cell_size
            pygame.draw.line(self.screen, COLORS['GRAY'], 
                           (self.margin, y), 
                           (self.margin + self.board_size * self.cell_size, y), 1)
        
        # 绘制游戏元素
        state = self.env.game.get_state()
        board = state['board']
        
        for row in range(self.board_size):
            for col in range(self.board_size):
                if board[row, col] != 0:
                    x = self.margin + col * self.cell_size + 2
                    y = self.margin + row * self.cell_size + 2
                    rect = pygame.Rect(x, y, self.cell_size - 4, self.cell_size - 4)
                    
                    if board[row, col] == 1:  # 蛇1头部
                        pygame.draw.rect(self.screen, COLORS['BLUE'], rect)
                        # 绘制眼睛
                        eye_size = 3
                        pygame.draw.circle(self.screen, COLORS['WHITE'], 
                                         (x + 6, y + 6), eye_size)
                        pygame.draw.circle(self.screen, COLORS['WHITE'], 
                                         (x + self.cell_size - 10, y + 6), eye_size)
                    elif board[row, col] == 2:  # 蛇1身体
                        pygame.draw.rect(self.screen, COLORS['CYAN'], rect)
                    elif board[row, col] == 3:  # 蛇2头部
                        pygame.draw.rect(self.screen, COLORS['RED'], rect)
                        # 绘制眼睛
                        eye_size = 3
                        pygame.draw.circle(self.screen, COLORS['WHITE'], 
                                         (x + 6, y + 6), eye_size)
                        pygame.draw.circle(self.screen, COLORS['WHITE'], 
                                         (x + self.cell_size - 10, y + 6), eye_size)
                    elif board[row, col] == 4:  # 蛇2身体
                        pygame.draw.rect(self.screen, COLORS['ORANGE'], rect)
                    elif board[row, col] == 5:  # 食物
                        pygame.draw.ellipse(self.screen, COLORS['GREEN'], rect)
    
    def _draw_ui(self):
        """绘制UI界面"""
        start_x = self.board_size * self.cell_size + self.margin + 20
        
        # 绘制标题
        title_text = self.font_medium.render("Snake AI Battle (Headless)", True, COLORS['BLACK'])
        self.screen.blit(title_text, (start_x, 25))
        
        # 绘制游戏信息
        state = self.env.game.get_state()
        len1 = len(state['snake1']) if state['alive1'] else 0
        len2 = len(state['snake2']) if state['alive2'] else 0
        alive1 = "Alive" if state['alive1'] else "Dead"
        alive2 = "Alive" if state['alive2'] else "Dead"
        
        info_texts = [
            f"Player 1: {len1} ({alive1})",
            f"Player 2: {len2} ({alive2})",
            f"Current Player: {state['current_player']}",
            f"Frame: {self.frame_count}",
            f"Food Count: {len(state['foods'])}"
        ]
        
        for i, text in enumerate(info_texts):
            text_surface = self.font_small.render(text, True, COLORS['DARK_GRAY'])
            self.screen.blit(text_surface, (start_x, 60 + i * 20))
    
    def _draw_game_status(self):
        """绘制游戏状态"""
        start_x = self.board_size * self.cell_size + self.margin + 20
        status_y = 200
        
        if self.game_over:
            if self.winner == 1:
                status_text = "Player 1 Wins!"
                color = COLORS['GREEN']
            elif self.winner == 2:
                status_text = "Player 2 Wins!"
                color = COLORS['RED']
            else:
                status_text = "Draw!"
                color = COLORS['ORANGE']
        else:
            if isinstance(self.current_agent, HumanAgent):
                status_text = "Player 1 Turn"
                color = COLORS['BLUE']
            else:
                status_text = "Player 2 Turn"
                color = COLORS['RED']
        
        text_surface = self.font_large.render(status_text, True, color)
        self.screen.blit(text_surface, (start_x, status_y))
    
    def run(self, max_frames=100):
        """运行游戏"""
        print("🐍 启动无头模式Snake游戏")
        print(f"📸 将保存最多 {max_frames} 张截图")
        print("⏹️  按 Ctrl+C 停止游戏")
        
        try:
            while self.frame_count < max_frames and not self.game_over:
                # 更新游戏
                self.update_game()
                
                # 绘制界面
                self.draw()
                
                # 短暂延迟
                time.sleep(0.1)
            
            if self.game_over:
                print(f"🎮 游戏结束！获胜者: {self.winner}")
            else:
                print(f"📸 已达到最大帧数: {max_frames}")
            
            print("✅ 游戏完成，截图已保存")
            
        except KeyboardInterrupt:
            print("\n⏹️  游戏被用户中断")
        finally:
            pygame.quit()

def main():
    """主函数"""
    print("🎮 无头模式Snake游戏")
    print("=" * 40)
    print("这个版本在没有GUI的环境中运行")
    print("游戏状态将保存为截图文件")
    print()
    
    try:
        game = HeadlessSnakeGame(board_size=15)
        game.run(max_frames=50)  # 运行50帧
    except Exception as e:
        print(f"❌ 游戏错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 