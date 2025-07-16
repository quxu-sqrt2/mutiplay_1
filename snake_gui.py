"""
贪吃蛇游戏专用GUI – 实时双蛇并行版本
"""

import pygame
import sys
import time
from typing import Dict, Any, Tuple
from games.snake import SnakeEnv   # 你的 SnakeEnv
from agents import SnakeAI, SmartSnakeAI, RandomBot, HumanAgent

# ---------------- 颜色表 ----------------
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

# -------------------------------------------------
# ✅ 1. 人类Agent：缓存下一次方向，不阻塞
# -------------------------------------------------
class RealTimeHumanAgent:
    def __init__(self, player_id: int):
        self.player_id = player_id
        self.next_dir = (0, 1)  # 默认向右

    def set_next_dir(self, direction: Tuple[int, int]):
        self.next_dir = direction

    def get_action(self, obs, env):
        env.game.set_next_direction(self.player_id, self.next_dir)  # 确保同步
        return self.next_dir

# -------------------------------------------------
class SnakeGUI:
    def __init__(self):
        pygame.init()

        self.board_size = 20
        self.cell_size = 25
        self.margin = 50

        self.window_width = self.board_size * self.cell_size + self.margin * 2 + 300
        self.window_height = self.board_size * self.cell_size + self.margin * 2
        self.screen = pygame.display.set_mode((self.window_width, self.window_height))
        pygame.display.set_caption("Snake AI Battle – Real-time")
        self.clock = pygame.time.Clock()

        self.font_large = pygame.font.Font(None, 36)
        self.font_medium = pygame.font.Font(None, 24)
        self.font_small = pygame.font.Font(None, 18)
        
        # ✅ 2. 实时双蛇环境
        self.env = SnakeEnv(board_size=self.board_size)
        self.human_agent = RealTimeHumanAgent(player_id=1)
        self.ai_agent = SnakeAI(name="AI", player_id=2)

        self.game_over = False
        self.winner = None
        self.selected_ai = "SnakeAI"
        self.paused = False

        self.buttons = self._create_buttons()

        self.last_update = time.time()
        self.update_interval = 0.3  # 500 ms 一步，可调
        self.MOVE_EVENT = pygame.USEREVENT + 1
        pygame.time.set_timer(self.MOVE_EVENT, 300) 
        self.reset_game()

    # ---------------- 按钮 ----------------
    def _create_buttons(self) -> Dict[str, Dict[str, Any]]:
        bw, bh = 120, 30
        sx = self.board_size * self.cell_size + self.margin + 20
        return {
            'snake_ai':   {'rect': pygame.Rect(sx,  50, bw, bh), 'text': 'Basic AI',  'color': COLORS['YELLOW']},
            'smart_ai':   {'rect': pygame.Rect(sx,  90, bw, bh), 'text': 'Smart AI',  'color': COLORS['LIGHT_GRAY']},
            'random_ai':  {'rect': pygame.Rect(sx, 130, bw, bh), 'text': 'Random AI', 'color': COLORS['LIGHT_GRAY']},
            'new_game':   {'rect': pygame.Rect(sx, 190, bw, bh), 'text': 'New Game',  'color': COLORS['GREEN']},
            'pause':      {'rect': pygame.Rect(sx, 230, bw, bh), 'text': 'Pause',     'color': COLORS['ORANGE']},
            'quit':       {'rect': pygame.Rect(sx, 270, bw, bh), 'text': 'Quit',      'color': COLORS['RED']}
        }

    # ---------------- 工具 ----------------
    def _create_ai_agent(self):
        if self.selected_ai == "SnakeAI":
            self.ai_agent = SnakeAI(name="Snake AI", player_id=2)
        elif self.selected_ai == "SmartSnakeAI":
            self.ai_agent = SmartSnakeAI(name="Smart AI", player_id=2)
        elif self.selected_ai == "RandomBot":
            self.ai_agent = RandomBot(name="Random AI", player_id=2)

    def reset_game(self):
        pygame.time.set_timer(self.MOVE_EVENT, 300)  # 重置速度
        self.env.reset()
        self.game_over = False
        self.winner = None
        self.paused = False
        self.buttons['pause']['text'] = 'Pause'
        

    # ---------------- 事件处理 ----------------
    def handle_events(self) -> bool:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            # 1. 键盘方向键/WASD → 立即缓存方向
            elif event.type == pygame.KEYDOWN and not (self.game_over or self.paused):
                key_to_dir = {
                    pygame.K_UP: (-1, 0), pygame.K_w: (-1, 0),
                    pygame.K_DOWN: (1, 0),  pygame.K_s: (1, 0),
                    pygame.K_LEFT: (0, -1), pygame.K_a: (0, -1),
                    pygame.K_RIGHT: (0, 1), pygame.K_d: (0, 1),
                }
                if event.key in key_to_dir:
                    new_dir = key_to_dir[event.key]
                    self.human_agent.set_next_dir(new_dir)  # 更新 Agent 缓存
                    self.env.game.set_next_direction(1, new_dir)  # 直接更新游戏

            # 2. MOVE_EVENT → 双蛇并行移动
            elif event.type == self.MOVE_EVENT and not (self.game_over or self.paused):
                # 玩家蛇
                self.env.game.move_snake1()
                # AI 蛇
                obs = self.env._get_observation()
                act2 = self.ai_agent.get_action(obs, self.env)
                self.env.game.set_next_direction(2, act2)
                self.env.game.move_snake2()

                if self.env.game.is_game_over():
                    self.game_over = True
                    self.winner = self.env.game.get_winner()

            # 3. 鼠标点击按钮
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self._handle_button_click(pygame.mouse.get_pos())

        return True

    def _handle_button_click(self, mouse: Tuple[int, int]):
        for name, info in self.buttons.items():
            if info['rect'].collidepoint(mouse):
                if name == 'new_game':
                    self.reset_game()
                elif name == 'quit':
                    pygame.quit(); sys.exit()
                elif name == 'pause':
                    self.paused = not self.paused
                    info['text'] = 'Resume' if self.paused else 'Pause'
                elif name.endswith('_ai'):
                    for k in ['snake_ai', 'smart_ai', 'random_ai']:
                        self.buttons[k]['color'] = COLORS['LIGHT_GRAY']
                    if name == 'snake_ai':
                        self.selected_ai = "SnakeAI"
                    elif name == 'smart_ai':
                        self.selected_ai = "SmartSnakeAI"
                    elif name == 'random_ai':
                        self.selected_ai = "RandomBot"
                    self.buttons[name]['color'] = COLORS['YELLOW']
                    self._create_ai_agent()
                    self.reset_game()

    # ---------------- 实时更新 ----------------


    # ---------------- 绘制 ----------------
    def draw(self):
        self.screen.fill(COLORS['WHITE'])
        self._draw_snake_game()
        self._draw_ui()
        self._draw_game_status()
        pygame.display.flip()

    # 其余绘制函数保持不变
    def _draw_snake_game(self):
        rect = pygame.Rect(self.margin, self.margin,
                           self.board_size * self.cell_size,
                           self.board_size * self.cell_size)
        pygame.draw.rect(self.screen, COLORS['LIGHT_GRAY'], rect)
        pygame.draw.rect(self.screen, COLORS['BLACK'], rect, 2)

        for i in range(self.board_size + 1):
            x = self.margin + i * self.cell_size
            y = self.margin + i * self.cell_size
            pygame.draw.line(self.screen, COLORS['GRAY'],
                             (x, self.margin), (x, self.margin + self.board_size * self.cell_size))
            pygame.draw.line(self.screen, COLORS['GRAY'],
                             (self.margin, y), (self.margin + self.board_size * self.cell_size, y))

        state = self.env.game.get_state()
        board = state['board']
        for r in range(self.board_size):
            for c in range(self.board_size):
                val = board[r, c]
                if val == 0:
                    continue
                x = self.margin + c * self.cell_size + 2
                y = self.margin + r * self.cell_size + 2
                cell = pygame.Rect(x, y, self.cell_size - 4, self.cell_size - 4)
                if val == 1:  # 蛇1头
                    pygame.draw.rect(self.screen, COLORS['BLUE'], cell)
                elif val == 2:  # 蛇1身
                    pygame.draw.rect(self.screen, COLORS['CYAN'], cell)
                elif val == 3:  # 蛇2头
                    pygame.draw.rect(self.screen, COLORS['RED'], cell)
                elif val == 4:  # 蛇2身
                    pygame.draw.rect(self.screen, COLORS['ORANGE'], cell)
                elif val == 5:  # 食物
                    pygame.draw.ellipse(self.screen, COLORS['GREEN'], cell)

    def _draw_ui(self):
        for name, info in self.buttons.items():
            pygame.draw.rect(self.screen, info['color'], info['rect'])
            pygame.draw.rect(self.screen, COLORS['BLACK'], info['rect'], 2)
            txt = self.font_medium.render(info['text'], True, COLORS['BLACK'])
            self.screen.blit(txt, txt.get_rect(center=info['rect'].center))

        sx = self.board_size * self.cell_size + self.margin + 20
        self.screen.blit(self.font_medium.render("AI Selection:", True, COLORS['BLACK']), (sx, 25))

        instructions = [
            "Controls:",
            "• Arrow keys / WASD to turn",
            "• Eat green food to grow",
            "• Avoid walls & snakes",
            "• Blue: You, Red: AI"
        ]
        for i, ins in enumerate(instructions):
            self.screen.blit(self.font_small.render(ins, True, COLORS['DARK_GRAY']),
                             (sx, 320 + i * 20))

    def _draw_game_status(self):
        sx = self.board_size * self.cell_size + self.margin + 20
        y = 450

        if self.paused:
            text, color = "Paused", COLORS['ORANGE']
        elif self.game_over:
            if self.winner == 1:
                text, color = "You Win!", COLORS['GREEN']
            elif self.winner == 2:
                text, color = "AI Wins!", COLORS['RED']
            else:
                text, color = "Draw!", COLORS['ORANGE']
        else:
            text, color = "Running...", COLORS['BLUE']

        self.screen.blit(self.font_large.render(text, True, color), (sx, y))

        state = self.env.game.get_state()
        len1 = len(state['snake1']) if state['alive1'] else 0
        len2 = len(state['snake2']) if state['alive2'] else 0
        self.screen.blit(self.font_small.render(f"You: {len1}", True, COLORS['BLUE']), (sx, y + 40))
        self.screen.blit(self.font_small.render(f"AI : {len2}", True, COLORS['RED']), (sx, y + 60))

    # ---------------- 主循环 ----------------
    def run(self):
        while True:
            if not self.handle_events():
                break
            self.draw()
            self.clock.tick(60)
        pygame.quit()
        sys.exit()


# -------------------------------------------------
# ✅ 5. 需要在 SnakeEnv 中新增 step_player 方法
# -------------------------------------------------
# 在 SnakeEnv 类中添加：
#
# def step_player(self, player_id: int, action):
#     if player_id == 1:
#         self.game.direction1 = action
#         self.game.move_snake1()
#     elif player_id == 2:
#         self.game.direction2 = action
#         self.game.move_snake2()
# -------------------------------------------------

if __name__ == "__main__":
    print("Starting Real-time Snake AI Battle...")
    SnakeGUI().run()