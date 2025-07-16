import pygame
import sys
import time
import traceback
from games.pingpong.pingpong_env import PingPongEnv
from agents.ai_bots.random_pingpong_ai import RandomPingPongAI
from agents.ai_bots.rule_based_pingpong_ai import RuleBasedPingPongAI
import random

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 128, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
LIGHT_GRAY = (211, 211, 211)

class PingPongGUI:
    def __init__(self):
        pygame.init()
        self.width, self.height = 1000, 600
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("PingPong Game")
        self.clock = pygame.time.Clock()
        self.env = PingPongEnv()
        self.font = pygame.font.SysFont(None, 32)
        self.ai_types = ["Human", "RandomPingPongAI", "RuleBasedPingPongAI"]
        self.left_ai = "Human"
        self.right_ai = "RuleBasedPingPongAI"
        self._create_agents()
        self._create_buttons()
        self.mode = "human_vs_ai"  # 可选: human_vs_ai, human_vs_human, ai_vs_ai
        self.reset()
        self.paused = False  # 新增：暂停状态

    def _create_agents(self):
        # 左挡板
        if self.left_ai == "Human":
            self.left_agent = None
        elif self.left_ai == "RandomPingPongAI":
            self.left_agent = RandomPingPongAI(name="Random AI L", player_id=1)
        elif self.left_ai == "RuleBasedPingPongAI":
            self.left_agent = RuleBasedPingPongAI(name="Smart AI L", player_id=1)
        # 右挡板
        if self.right_ai == "Human":
            self.right_agent = None
        elif self.right_ai == "RandomPingPongAI":
            self.right_agent = RandomPingPongAI(name="Random AI R", player_id=2)
        elif self.right_ai == "RuleBasedPingPongAI":
            self.right_agent = RuleBasedPingPongAI(name="Smart AI R", player_id=2)

    def _create_buttons(self):
        button_width = 120
        button_height = 40
        margin = 20  # 距离右下边缘的边距
        start_x = self.width - button_width - margin
        start_y = self.height - len(self.ai_types) * (button_height + 10) - margin

        self.ai_buttons = {}
        for i, ai_name in enumerate(self.ai_types):
            rect_l = pygame.Rect(start_x - button_width - 10, start_y + i * (button_height + 10), button_width, button_height)
            rect_r = pygame.Rect(start_x, start_y + i * (button_height + 10), button_width, button_height)
            self.ai_buttons[("left", ai_name)] = rect_l
            self.ai_buttons[("right", ai_name)] = rect_r

        # 模式按钮也上移，避免重叠
        self.mode_buttons = {
            "human_vs_ai": pygame.Rect(self.width - 180, 10, 120, 36),
            "human_vs_human": pygame.Rect(self.width - 320, 10, 120, 36),
            "ai_vs_ai": pygame.Rect(self.width - 460, 10, 120, 36)
        }

        # 暂停按钮也上移
        self.pause_button = pygame.Rect(40, 10, 100, 36)

    def reset(self):
        self.env.reset()
        self.done = False
        self._create_agents()

    def draw(self, state, spin_flag=None):
        self.screen.fill(WHITE)
        # Draw ball
        bx = int(state['ball_pos'][0] * (self.width - 40)) + 20
        by = int(state['ball_pos'][1] * (self.height - 40)) + 20
        pygame.draw.circle(self.screen, RED, (bx, by), 10)
        # Draw paddles (as rectangles)
        lpx = int(state['left_paddle_x'] * (self.width - 40)) + 20
        lpy = int(state['left_paddle_y'] * (self.height - 80)) + 40
        rpx = int(state['right_paddle_x'] * (self.width - 40)) + 20
        rpy = int(state['right_paddle_y'] * (self.height - 80)) + 40
        pygame.draw.rect(self.screen, BLUE, (lpx - 5, lpy - 40, 10, 80))
        pygame.draw.rect(self.screen, GREEN, (rpx - 5, rpy - 40, 10, 80))
        # Draw score (下移到画面中间偏上)
        score_text = self.font.render(f"{state['score_left']} : {state['score_right']}", True, BLACK)
        self.screen.blit(score_text, (self.width // 2 - 40, 80))
        # Draw pause button
        pygame.draw.rect(self.screen, YELLOW if self.paused else LIGHT_GRAY, self.pause_button)
        pygame.draw.rect(self.screen, BLACK, self.pause_button, 2)
        pause_text = self.font.render("Resume" if self.paused else "Pause", True, BLACK)
        self.screen.blit(pause_text, self.pause_button.move(10, 0))
        # Draw AI selection buttons
        for (side, ai_name), rect in self.ai_buttons.items():
            color = YELLOW if (side == "left" and self.left_ai == ai_name) or (side == "right" and self.right_ai == ai_name) else LIGHT_GRAY
            pygame.draw.rect(self.screen, color, rect)
            pygame.draw.rect(self.screen, BLACK, rect, 2)
            short_name = "Human" if ai_name == "Human" else ("Smart AI" if ai_name == "RuleBasedPingPongAI" else "Random AI")
            text = self.font.render(short_name, True, BLACK)
            text_rect = text.get_rect(center=rect.center)
            self.screen.blit(text, text_rect)
        # Draw mode switch buttons
        for mode, rect in self.mode_buttons.items():
            color = YELLOW if self.mode == mode else LIGHT_GRAY
            pygame.draw.rect(self.screen, color, rect)
            pygame.draw.rect(self.screen, BLACK, rect, 2)
            mode_text = {"human_vs_ai": "1P vs AI", "human_vs_human": "1P vs 2P", "ai_vs_ai": "AI vs AI"}[mode]
            text = self.font.render(mode_text, True, BLACK)
            self.screen.blit(text, rect.move(10, 0))
        # 操作提示
        if self.mode == "human_vs_human":
            op_lines = [
                "Controls:",
                "Left paddle: W/S/A/D move, Q power shot, E spin",
                "Right paddle: Up/Down/Left/Right move, 1 power shot, 2 spin",
                "R: Restart, P: Pause/Resume, Close window to exit"
            ]
        elif self.mode == "human_vs_ai":
            op_lines = [
                "Controls:",
                "Left paddle: W/S/A/D move, Q power shot, E spin",
                "Right paddle: AI",
                "R: Restart, P: Pause/Resume, Close window to exit"
            ]
        else:
            op_lines = [
                "Controls:",
                "Left paddle: AI",
                "Right paddle: AI",
                "R: Restart, P: Pause/Resume, Close window to exit"
            ]
        for i, line in enumerate(op_lines):
            color = (80,80,80)
            tip = self.font.render(line, True, color)
            self.screen.blit(tip, (30, self.height - 120 + i*28))
        # Spin提示
        if spin_flag:
            spin_text = self.font.render("Spin!", True, (255, 100, 0))
            self.screen.blit(spin_text, (self.width // 2 - 30, by - 40))
        # 暂停遮罩
        if self.paused:
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill((200, 200, 200, 120))
            self.screen.blit(overlay, (0, 0))
            pause_tip = self.font.render("Paused", True, (255, 100, 0))
            self.screen.blit(pause_tip, (self.width // 2 - 50, self.height // 2 - 30))
        pygame.display.flip()

    def run(self):
        try:
            state, _ = self.env.reset()
            ai_speed_factor = 0.8
            spin_flag = None

            while not self.done:
                # ---------- 统一动作字典 ----------
                action = {
                    "move_left_x": 0,  "move_left_y": 0,
                    "move_right_x": 0, "move_right_y": 0,
                    "left_force": False, "right_force": False,
                    "left_spin": False, "right_spin": False
                }

                # ---------- 事件处理 ----------
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        print("[LOG] Received pygame.QUIT event, exiting.")
                        pygame.quit()
                        sys.exit()

                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_p:
                            self.paused = not self.paused
                            continue
                        if event.key == pygame.K_r:
                            print("[LOG] Restarting game.")
                            self.reset()
                            state, _ = self.env.reset()
                            spin_flag = None
                            continue

                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        mouse_pos = pygame.mouse.get_pos()
                        # 暂停按钮
                        if self.pause_button.collidepoint(mouse_pos):
                            self.paused = not self.paused
                            continue
                        # AI 选择按钮
                        for (side, ai_name), rect in self.ai_buttons.items():
                            if rect.collidepoint(mouse_pos):
                                if side == "left":
                                    self.left_ai = ai_name
                                else:
                                    self.right_ai = ai_name
                                self._create_agents()
                        # 模式按钮
                        for mode, rect in self.mode_buttons.items():
                            if rect.collidepoint(mouse_pos):
                                self.mode = mode
                                self.reset()
                                self._create_agents()

                # ---------- 键盘实时检测 ----------
                keys = pygame.key.get_pressed()

                # 左挡板（WASD + Q/E）
                if keys[pygame.K_w]:
                    action["move_left_y"] = -1
                elif keys[pygame.K_s]:
                    action["move_left_y"] = 1
                if keys[pygame.K_a]:
                    action["move_left_x"] = -1
                elif keys[pygame.K_d]:
                    action["move_left_x"] = 1
                action["left_force"] = keys[pygame.K_q]
                action["left_spin"]   = keys[pygame.K_e]

                # 右挡板（↑↓←→ + 1/2）
                if keys[pygame.K_UP]:
                    action["move_right_y"] = -1
                elif keys[pygame.K_DOWN]:
                    action["move_right_y"] = 1
                if keys[pygame.K_LEFT]:
                    action["move_right_x"] = -1
                elif keys[pygame.K_RIGHT]:
                    action["move_right_x"] = 1
                action["right_force"] = keys[pygame.K_1]
                action["right_spin"]  = keys[pygame.K_2]

                # ---------- AI 接管 ----------
                if self.left_ai != "Human" and self.left_agent:
                    ai_l = self.left_agent.get_action(self.env.game.get_state(), self.env)
                    action.update({
                        "move_left_x": ai_l.get("move_left_x", 0),
                        "move_left_y": ai_l.get("move_left_y", 0),
                        "left_force": ai_l.get("left_force", False),
                        "left_spin": ai_l.get("left_spin", False)
                    })

                if self.right_ai != "Human" and self.right_agent:
                    ai_r = self.right_agent.get_action(self.env.game.get_state(), self.env)
                    action.update({
                        "move_right_x": ai_r.get("move_right_x", 0),
                        "move_right_y": ai_r.get("move_right_y", 0),
                        "right_force": ai_r.get("right_force", False),
                        "right_spin": ai_r.get("right_spin", False)
                    })

                # ---------- 暂停 ----------
                if self.paused:
                    self.draw(self.env.game.get_state(), spin_flag=spin_flag)
                    self.clock.tick(60)
                    continue

                # ---------- 游戏步进 ----------
                state, _, self.done, _, _ = self.env.step(action)
                spin_flag = action.get("left_spin") or action.get("right_spin")
                self.draw(self.env.game.get_state(), spin_flag=spin_flag)
                self.clock.tick(60)

        except Exception as e:
            print("[FATAL]", e)
            import traceback
            traceback.print_exc()
            pygame.quit()
            sys.exit()

if __name__ == "__main__":
    gui = PingPongGUI()
    gui.run() 