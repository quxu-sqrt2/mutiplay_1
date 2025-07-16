"""
多游戏图形界面
支持五子棋和贪吃蛇的人机对战，修复中文显示问题
"""

import pygame
import sys
import time
import os
from typing import Optional, Tuple, Dict, Any
from games.gomoku import GomokuGame, GomokuEnv
from games.snake import SnakeGame, SnakeEnv
from agents import RandomBot, MinimaxBot, MCTSBot, HumanAgent, SnakeAI, SmartSnakeAI
import config

# 颜色定义
COLORS = {
    "WHITE": (255, 255, 255),
    "BLACK": (0, 0, 0),
    "BROWN": (139, 69, 19),
    "LIGHT_BROWN": (205, 133, 63),
    "RED": (255, 0, 0),
    "BLUE": (0, 0, 255),
    "GREEN": (0, 255, 0),
    "GRAY": (128, 128, 128),
    "LIGHT_GRAY": (211, 211, 211),
    "DARK_GRAY": (64, 64, 64),
    "YELLOW": (255, 255, 0),
    "ORANGE": (255, 165, 0),
    "PURPLE": (128, 0, 128),
    "CYAN": (0, 255, 255),
}

# 🐍 -------------------------------------------------
# 实时人类 agent（直接复制自 snake_gui）
class RealTimeHumanAgent:
    def __init__(self, player_id: int):
        self.player_id = player_id
        self.next_dir = (0, 1)  # 默认右

    def set_next_dir(self, direction: Tuple[int, int]):
        self.next_dir = direction

    def get_action(self, obs, env):
        env.game.set_next_direction(self.player_id, self.next_dir)
        return self.next_dir
# 🐍 -------------------------------------------------


class MultiGameGUI:
    """多游戏图形界面"""

    def __init__(self):
        pygame.init()

        # 设置中文字体
        self.font_path = self._get_chinese_font()
        self.font_large = pygame.font.Font(self.font_path, 28)
        self.font_medium = pygame.font.Font(self.font_path, 20)
        self.font_small = pygame.font.Font(self.font_path, 16)

        self.window_width = 900
        self.window_height = 700
        self.screen = pygame.display.set_mode((self.window_width, self.window_height))
        pygame.display.set_caption("多游戏AI对战平台")
        self.clock = pygame.time.Clock()

        # 游戏状态
        self.current_game = "gomoku"  # "gomoku" 或 "snake"
        self.env = None
        self.human_agent = None
        self.ai_agent = None
        self.current_agent = None
        self.game_over = False
        self.winner = None
        self.last_move = None
        self.thinking = False
        self.selected_ai = "RandomBot"
        self.paused = False

        # UI元素
        self.buttons = self._create_buttons()
        self.cell_size = 25
        self.margin = 50

        # 游戏计时
        self.last_update = time.time()
        self.update_interval = 0.3  # 贪吃蛇更新间隔

        # 🐍 Snake 实时相关
        self.MOVE_EVENT = pygame.USEREVENT + 1
        pygame.time.set_timer(self.MOVE_EVENT, 0)  # 先关闭

        self._switch_game("gomoku")

    def _get_chinese_font(self):
        """获取中文字体路径"""
        font_paths = [
            "/System/Library/Fonts/PingFang.ttc",
            "/System/Library/Fonts/Helvetica.ttc",
            "/Library/Fonts/Arial Unicode.ttf",
            "C:/Windows/Fonts/simhei.ttf",
            "C:/Windows/Fonts/simsun.ttc",
            "C:/Windows/Fonts/msyh.ttc",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        ]
        for font_path in font_paths:
            if os.path.exists(font_path):
                return font_path
        return None

    def _create_buttons(self) -> Dict[str, Dict[str, Any]]:
        """创建UI按钮"""
        button_width = 120
        button_height = 30
        start_x = 650
        buttons = {
            "gomoku_game": {
                "rect": pygame.Rect(start_x, 50, button_width, button_height),
                "text": "Gomoku",
                "color": COLORS["YELLOW"],
            },
            "snake_game": {
                "rect": pygame.Rect(start_x, 90, button_width, button_height),
                "text": "Snake",
                "color": COLORS["LIGHT_GRAY"],
            },
            "random_ai": {
                "rect": pygame.Rect(start_x, 150, button_width, button_height),
                "text": "Random AI",
                "color": COLORS["YELLOW"],
            },
            "minimax_ai": {
                "rect": pygame.Rect(start_x, 190, button_width, button_height),
                "text": "Minimax AI",
                "color": COLORS["LIGHT_GRAY"],
            },
            "mcts_ai": {
                "rect": pygame.Rect(start_x, 230, button_width, button_height),
                "text": "MCTS AI",
                "color": COLORS["LIGHT_GRAY"],
            },
            "new_game": {
                "rect": pygame.Rect(start_x, 290, button_width, button_height),
                "text": "New Game",
                "color": COLORS["GREEN"],
            },
            "pause": {
                "rect": pygame.Rect(start_x, 330, button_width, button_height),
                "text": "Pause",
                "color": COLORS["ORANGE"],
            },
            "quit": {
                "rect": pygame.Rect(start_x, 370, button_width, button_height),
                "text": "Quit",
                "color": COLORS["RED"],
            },
        }
        return buttons

    # -------------------------------------------------
    # 🐍 下面是整合后的 _switch_game
    # -------------------------------------------------
    def _switch_game(self, game_type):
        """切换游戏类型"""
        self.current_game = game_type

        # 更新按钮颜色
        for btn_name in ["gomoku_game", "snake_game"]:
            self.buttons[btn_name]["color"] = COLORS["LIGHT_GRAY"]
        self.buttons[f"{game_type}_game"]["color"] = COLORS["YELLOW"]

        # 关闭旧计时器
        pygame.time.set_timer(self.MOVE_EVENT, 0)

        if game_type == "gomoku":
            self.env = GomokuEnv(board_size=15, win_length=5)
            self.cell_size = 30
            self.update_interval = 1.0
            self.human_agent = HumanAgent(name="Human Player", player_id=1)
            self._create_ai_agent()
            self.reset_game()

        elif game_type == "snake":
            self.env = SnakeEnv(board_size=20)
            self.cell_size = 25
            self.update_interval = 0.3
            # 实时人类代理
            self.human_agent = RealTimeHumanAgent(player_id=1)
            self._create_ai_agent()
            self.reset_game()
            # 启动 Snake 计时器
            pygame.time.set_timer(self.MOVE_EVENT, 300)

    # -------------------------------------------------
    def _create_ai_agent(self):
        """创建AI智能体"""
        if self.selected_ai == "RandomBot":
            if self.current_game == "snake":
                self.ai_agent = RandomBot(name="Random AI", player_id=2)
            else:
                self.ai_agent = RandomBot(name="Random AI", player_id=2)
        elif self.selected_ai == "MinimaxBot":
            if self.current_game == "gomoku":
                self.ai_agent = MinimaxBot(name="Minimax AI", player_id=2, max_depth=3)
            else:
                self.ai_agent = SnakeAI(name="Snake AI", player_id=2)
        elif self.selected_ai == "MCTSBot":
            if self.current_game == "gomoku":
                self.ai_agent = MCTSBot(name="MCTS AI", player_id=2, simulation_count=300)
            else:
                self.ai_agent = SmartSnakeAI(name="Smart AI", player_id=2)

    def reset_game(self):
        """重置游戏"""
        self.env.reset()
        self.game_over = False
        self.winner = None
        self.last_move = None
        self.thinking = False
        self.current_agent = self.human_agent
        self.last_update = time.time()
        self.paused = False
        self.buttons["pause"]["text"] = "Pause"

    # -------------------------------------------------
    # 🐍 重写 handle_events：加入 Snake 实时循环
    # -------------------------------------------------
    def handle_events(self) -> bool:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            # ===== Snake 实时事件 =====
            if self.current_game == "snake":
                if event.type == self.MOVE_EVENT and not (self.game_over or self.paused):
                    # 人类蛇
                    self.env.game.move_snake1()
                    # AI 蛇
                    obs = self.env._get_observation()
                    act2 = self.ai_agent.get_action(obs, self.env)
                    self.env.game.set_next_direction(2, act2)
                    self.env.game.move_snake2()
                    if self.env.game.is_game_over():
                        self.game_over = True
                        self.winner = self.env.game.get_winner()

                elif event.type == pygame.KEYDOWN and not (self.game_over or self.paused):
                    key_to_dir = {
                        pygame.K_UP: (-1, 0), pygame.K_w: (-1, 0),
                        pygame.K_DOWN: (1, 0),  pygame.K_s: (1, 0),
                        pygame.K_LEFT: (0, -1), pygame.K_a: (0, -1),
                        pygame.K_RIGHT: (0, 1), pygame.K_d: (0, 1),
                    }
                    if event.key in key_to_dir:
                        new_dir = key_to_dir[event.key]
                        self.human_agent.set_next_dir(new_dir)
                        self.env.game.set_next_direction(1, new_dir)

            # ===== 原五子棋鼠标/键盘事件 =====
            elif self.current_game == "gomoku":
                if event.type == pygame.KEYDOWN:
                    pass  # 五子棋无键盘操作
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mouse_pos = pygame.mouse.get_pos()
                    click_result = self._handle_button_click(mouse_pos)
                    if click_result is None:
                        return False
                    elif click_result is True:
                        self.reset_game()
                    if not self.game_over and isinstance(self.current_agent, HumanAgent) and not self.thinking:
                        self._handle_gomoku_click(mouse_pos)

            # ===== 按钮点击统一处理（两种模式共用） =====
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                click_result = self._handle_button_click(mouse_pos)
                if click_result is None:
                    return False
                elif click_result is True:
                    self.reset_game()

        return True

    # -------------------------------------------------
    def _handle_button_click(self, mouse_pos: Tuple[int, int]) -> bool:
        """处理按钮点击"""
        for button_name, button_info in self.buttons.items():
            if button_info["rect"].collidepoint(mouse_pos):
                if button_name == "new_game":
                    self.reset_game()
                elif button_name == "quit":
                    return None
                elif button_name == "pause":
                    self.paused = not self.paused
                    self.buttons["pause"]["text"] = "Resume" if self.paused else "Pause"
                elif button_name in ["gomoku_game", "snake_game"]:
                    game_type = button_name.split("_")[0]
                    self._switch_game(game_type)
                elif button_name.endswith("_ai"):
                    old_ai = f"{self.selected_ai.lower()}_ai"
                    if old_ai in self.buttons:
                        self.buttons[old_ai]["color"] = COLORS["LIGHT_GRAY"]
                    if button_name == "random_ai":
                        self.selected_ai = "RandomBot"
                    elif button_name == "minimax_ai":
                        self.selected_ai = "MinimaxBot"
                    elif button_name == "mcts_ai":
                        self.selected_ai = "MCTSBot"
                    self.buttons[button_name]["color"] = COLORS["YELLOW"]
                    self._create_ai_agent()
                    self.reset_game()
                return True
        return False

    # -------------------------------------------------
    def _handle_gomoku_click(self, mouse_pos: Tuple[int, int]):
        """处理五子棋棋盘点击"""
        x, y = mouse_pos
        board_x = x - self.margin
        board_y = y - self.margin
        if board_x < 0 or board_y < 0:
            return
        col = round(board_x / self.cell_size)
        row = round(board_y / self.cell_size)
        if 0 <= row < 15 and 0 <= col < 15:
            action = (row, col)
            if action in self.env.get_valid_actions():
                self._make_move(action)

    def _make_move(self, action):
        """执行移动（仅五子棋用）"""
        if self.game_over or self.paused or self.current_game != "gomoku":
            return
        try:
            observation, reward, terminated, truncated, info = self.env.step(action)
            self.last_move = action
            if terminated or truncated:
                self.game_over = True
                self.winner = self.env.get_winner()
            else:
                self._switch_player()
        except Exception as e:
            print(f"Move execution failed: {e}")

    def _switch_player(self):
        """仅在五子棋中切换玩家"""
        if self.current_game != "gomoku":
            return
        if isinstance(self.current_agent, HumanAgent):
            self.current_agent = self.ai_agent
            self.thinking = True
        else:
            self.current_agent = self.human_agent

    def update_game(self):
        """update_game 现在只负责五子棋 AI 的思考，贪吃蛇由事件驱动"""
        if self.game_over or self.paused or self.current_game != "gomoku":
            return
        current_time = time.time()
        if current_time - self.last_update < self.update_interval:
            return
        self.last_update = current_time
        if not isinstance(self.current_agent, HumanAgent) and self.thinking:
            try:
                observation = self.env._get_observation()
                action = self.current_agent.get_action(observation, self.env)
                if action:
                    self._make_move(action)
                self.thinking = False
            except Exception as e:
                print(f"AI thinking failed: {e}")
                self.thinking = False

    # -------------------------------------------------
    # 绘制部分：把 snake_gui 的绘制函数融合进来
    # -------------------------------------------------
    def draw(self):
        self.screen.fill(COLORS["WHITE"])
        if self.current_game == "gomoku":
            self._draw_gomoku()
        elif self.current_game == "snake":
            self._draw_snake_game_realtime()
        self._draw_ui()
        self._draw_game_status()
        pygame.display.flip()

    # === 五子棋绘制（原封不动） ===
    def _draw_gomoku(self):
        board_size = 15
        board_rect = pygame.Rect(
            self.margin - 20,
            self.margin - 20,
            board_size * self.cell_size + 40,
            board_size * self.cell_size + 40,
        )
        pygame.draw.rect(self.screen, COLORS["LIGHT_BROWN"], board_rect)
        for i in range(board_size):
            start_pos = (self.margin + i * self.cell_size, self.margin)
            end_pos = (self.margin + i * self.cell_size, self.margin + (board_size - 1) * self.cell_size)
            pygame.draw.line(self.screen, COLORS["BLACK"], start_pos, end_pos, 2)
            start_pos = (self.margin, self.margin + i * self.cell_size)
            end_pos = (self.margin + (board_size - 1) * self.cell_size, self.margin + i * self.cell_size)
            pygame.draw.line(self.screen, COLORS["BLACK"], start_pos, end_pos, 2)
        star_positions = [(3, 3), (3, 11), (11, 3), (11, 11), (7, 7)]
        for row, col in star_positions:
            center = (self.margin + col * self.cell_size, self.margin + row * self.cell_size)
            pygame.draw.circle(self.screen, COLORS["BLACK"], center, 4)
        board = self.env.game.board
        for row in range(board_size):
            for col in range(board_size):
                if board[row, col] != 0:
                    center = (self.margin + col * self.cell_size, self.margin + row * self.cell_size)
                    color = COLORS["BLACK"] if board[row, col] == 1 else COLORS["WHITE"]
                    border = COLORS["WHITE"] if board[row, col] == 1 else COLORS["BLACK"]
                    pygame.draw.circle(self.screen, color, center, 12)
                    pygame.draw.circle(self.screen, border, center, 12, 2)
        if self.last_move and isinstance(self.last_move, tuple) and len(self.last_move) == 2:
            row, col = self.last_move
            center = (self.margin + col * self.cell_size, self.margin + row * self.cell_size)
            pygame.draw.circle(self.screen, COLORS["RED"], center, 6, 3)

    # === Snake 实时绘制（复制自 snake_gui） ===
    def _draw_snake_game_realtime(self):
        board_size = 20
        rect = pygame.Rect(self.margin, self.margin,
                           board_size * self.cell_size,
                           board_size * self.cell_size)
        pygame.draw.rect(self.screen, COLORS["LIGHT_GRAY"], rect)
        pygame.draw.rect(self.screen, COLORS["BLACK"], rect, 2)

        for i in range(board_size + 1):
            x = self.margin + i * self.cell_size
            y = self.margin + i * self.cell_size
            pygame.draw.line(self.screen, COLORS["GRAY"],
                             (x, self.margin), (x, self.margin + board_size * self.cell_size))
            pygame.draw.line(self.screen, COLORS["GRAY"],
                             (self.margin, y), (self.margin + board_size * self.cell_size, y))

        state = self.env.game.get_state()
        board = state["board"]
        for r in range(board_size):
            for c in range(board_size):
                val = board[r, c]
                if val == 0:
                    continue
                x = self.margin + c * self.cell_size + 2
                y = self.margin + r * self.cell_size + 2
                cell = pygame.Rect(x, y, self.cell_size - 4, self.cell_size - 4)
                if val == 1:  # 蛇1头
                    pygame.draw.rect(self.screen, COLORS["BLUE"], cell)
                    # 添加白色眼睛
                    eye_size = max(2, self.cell_size // 6)
                    eye_offset = self.cell_size // 4
                    left_eye = (x + eye_offset, y + eye_offset)
                    right_eye = (x + self.cell_size - eye_offset - eye_size, y + eye_offset)
                    pygame.draw.circle(self.screen, COLORS["WHITE"], left_eye, eye_size)
                    pygame.draw.circle(self.screen, COLORS["WHITE"], right_eye, eye_size)
                elif val == 2:  # 蛇1身
                    pygame.draw.rect(self.screen, COLORS["CYAN"], cell)
                elif val == 3:  # 蛇2头
                    pygame.draw.rect(self.screen, COLORS["RED"], cell)
                    # 添加白色眼睛
                    eye_size = max(2, self.cell_size // 6)
                    eye_offset = self.cell_size // 4
                    left_eye = (x + eye_offset, y + eye_offset)
                    right_eye = (x + self.cell_size - eye_offset - eye_size, y + eye_offset)
                    pygame.draw.circle(self.screen, COLORS["WHITE"], left_eye, eye_size)
                    pygame.draw.circle(self.screen, COLORS["WHITE"], right_eye, eye_size)
                elif val == 4:  # 蛇2身
                    pygame.draw.rect(self.screen, COLORS["ORANGE"], cell)
                elif val == 5:  # 食物
                    pygame.draw.ellipse(self.screen, COLORS["GREEN"], cell)

    # === UI 绘制（原按钮不变，仅 Snake 时右侧文字变化） ===
    def _draw_ui(self):
        for button_name, button_info in self.buttons.items():
            pygame.draw.rect(self.screen, button_info["color"], button_info["rect"])
            pygame.draw.rect(self.screen, COLORS["BLACK"], button_info["rect"], 2)
            text_surface = self.font_medium.render(button_info["text"], True, COLORS["BLACK"])
            text_rect = text_surface.get_rect(center=button_info["rect"].center)
            self.screen.blit(text_surface, text_rect)

        start_x = self.buttons["gomoku_game"]["rect"].x
        self.screen.blit(self.font_medium.render("Game Selection:", True, COLORS["BLACK"]), (start_x, 25))
        self.screen.blit(self.font_medium.render("AI Selection:", True, COLORS["BLACK"]), (start_x, 125))

        # 操作说明随游戏变化
        if self.current_game == "gomoku":
            instructions = [
                "Gomoku Controls:",
                "• Click to place stone",
                "• Connect 5 to win",
            ]
        else:
            instructions = [
                "Snake Controls:",
                "• Arrow keys / WASD to turn",
                "• Eat green food to grow",
                "• Avoid walls & snakes",
            ]
        start_y = 420
        for i, instruction in enumerate(instructions):
            text = self.font_small.render(instruction, True, COLORS["DARK_GRAY"])
            self.screen.blit(text, (start_x, start_y + i * 20))

    # === 状态信息 ===
    def _draw_game_status(self):
        status_x = 20
        status_y = self.window_height - 100

        if self.paused:
            status_text = "Game Paused..."
            color = COLORS["ORANGE"]
        elif self.game_over:
            if self.winner == 1:
                status_text = "Congratulations! You Win!"
                color = COLORS["GREEN"]
            elif self.winner == 2:
                status_text = "AI Wins! Try Again!"
                color = COLORS["RED"]
            else:
                status_text = "Draw!"
                color = COLORS["ORANGE"]
        else:
            if self.current_game == "gomoku":
                if isinstance(self.current_agent, HumanAgent):
                    status_text = "Your Turn - Click to Place Stone"
                    color = COLORS["BLUE"]
                else:
                    status_text = f"{self.ai_agent.name}'s Turn"
                    color = COLORS["RED"]
            else:  # Snake 实时
                status_text = "Running..."
                color = COLORS["BLUE"]

        text_surface = self.font_large.render(status_text, True, color)
        self.screen.blit(text_surface, (status_x, status_y))

        info_y = status_y + 40
        if self.current_game == "gomoku":
            player_info = f"Black: Human Player  White: {self.ai_agent.name if self.ai_agent else 'AI'}"
        else:
            state = self.env.game.get_state()
            len1 = len(state["snake1"]) if state["alive1"] else 0
            len2 = len(state["snake2"]) if state["alive2"] else 0
            player_info = f"Blue Snake(You): {len1}  Red Snake(AI): {len2}"
        info_surface = self.font_small.render(player_info, True, COLORS["DARK_GRAY"])
        self.screen.blit(info_surface, (status_x, info_y))

    # -------------------------------------------------
    def run(self):
        running = True
        while running:
            running = self.handle_events()
            if self.current_game == "gomoku":
                self.update_game()  # 仅五子棋需要 AI 思考
            self.draw()
            self.clock.tick(60)
        pygame.quit()
        sys.exit()


def main():
    print("Starting Multi-Game AI Battle Platform...")
    print("Supported Games:")
    print("- Gomoku: Click to place stones")
    print("- Snake: Arrow keys/WASD to control")
    print("- Multiple AI difficulty levels")
    print("- Real-time human vs AI battles")
    try:
        game = MultiGameGUI()
        game.run()
    except Exception as e:
        print(f"Game error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()