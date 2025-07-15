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
        self.width, self.height = 800, 400
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
        start_x = self.width - button_width - 40
        start_y = 100
        self.ai_buttons = {}
        for i, ai_name in enumerate(self.ai_types):
            rect_l = pygame.Rect(start_x, start_y + i * (button_height + 10), button_width, button_height)
            rect_r = pygame.Rect(start_x + button_width + 20, start_y + i * (button_height + 10), button_width, button_height)
            self.ai_buttons[("left", ai_name)] = rect_l
            self.ai_buttons[("right", ai_name)] = rect_r
        # 模式切换按钮
        self.mode_buttons = {
            "human_vs_ai": pygame.Rect(self.width - 180, 30, 120, 36),
            "human_vs_human": pygame.Rect(self.width - 320, 30, 120, 36),
            "ai_vs_ai": pygame.Rect(self.width - 460, 30, 120, 36)
        }
        # 新增：暂停按钮
        self.pause_button = pygame.Rect(40, 30, 100, 36)

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
            ai_speed_factor = 0.8  # AI移动速度下降20%
            spin_flag = None
            while not self.done:
                try:
                    action = {"move_left_x": 0, "move_left_y": 0, "move_right_x": 0, "move_right_y": 0, "left_force": False, "right_force": False, "left_spin": False, "right_spin": False}
                    action2 = {"move_left_x": 0, "move_left_y": 0, "move_right_x": 0, "move_right_y": 0, "left_force": False, "right_force": False, "left_spin": False, "right_spin": False}
                    # 新增：追踪Q/1是否按下
                    left_force_pressed = False
                    right_force_pressed = False
                    # 新增：追踪E/2是否按下（防止连发）
                    left_spin_pressed = False
                    right_spin_pressed = False
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            print("[LOG] Received pygame.QUIT event, exiting.")
                            pygame.quit()
                            sys.exit()
                        elif event.type == pygame.KEYDOWN:
                            print(f"[LOG] KEYDOWN: {event.key}")
                            if event.key == pygame.K_p:
                                self.paused = not self.paused
                                continue
                            if self.mode in ["human_vs_ai", "human_vs_human"]:
                                # Left paddle: W/S/A/D
                                if event.key == pygame.K_w:
                                    action["move_left_y"] = -1
                                elif event.key == pygame.K_s:
                                    action["move_left_y"] = 1
                                elif event.key == pygame.K_a:
                                    action["move_left_x"] = -1
                                elif event.key == pygame.K_d:
                                    action["move_left_x"] = 1
                                elif event.key == pygame.K_q:
                                    left_force_pressed = True
                                elif event.key == pygame.K_e:
                                    left_spin_pressed = True
                            if self.mode == "human_vs_human":
                                # 2P mode: Right paddle: arrows
                                if event.key == pygame.K_UP:
                                    action2["move_right_y"] = -1
                                elif event.key == pygame.K_DOWN:
                                    action2["move_right_y"] = 1
                                elif event.key == pygame.K_LEFT:
                                    action2["move_right_x"] = -1
                                elif event.key == pygame.K_RIGHT:
                                    action2["move_right_x"] = 1
                                elif event.key == pygame.K_1:
                                    right_force_pressed = True
                                elif event.key == pygame.K_2:
                                    right_spin_pressed = True
                            elif self.mode == "human_vs_ai":
                                pass
                            elif self.mode == "ai_vs_ai":
                                pass
                            if event.key == pygame.K_r:
                                print("[LOG] Restarting game.")
                                self.reset()
                                state, _ = self.env.reset()
                                spin_flag = None
                                continue
                        elif event.type == pygame.KEYUP:
                            if event.key == pygame.K_q:
                                left_force_pressed = False
                            if event.key == pygame.K_1:
                                right_force_pressed = False
                            if event.key == pygame.K_e:
                                left_spin_pressed = False
                            if event.key == pygame.K_2:
                                right_spin_pressed = False
                        elif event.type == pygame.MOUSEBUTTONDOWN:
                            mouse_pos = pygame.mouse.get_pos()
                            # 暂停按钮
                            if self.pause_button.collidepoint(mouse_pos):
                                self.paused = not self.paused
                                continue
                            # AI选择按钮
                            for (side, ai_name), rect in self.ai_buttons.items():
                                if rect.collidepoint(mouse_pos):
                                    if side == "left":
                                        self.left_ai = ai_name
                                        self._create_agents()
                                    else:
                                        self.right_ai = ai_name
                                        self._create_agents()
                            # 模式切换按钮
                            for mode, rect in self.mode_buttons.items():
                                if rect.collidepoint(mouse_pos):
                                    self.mode = mode
                                    self.reset()
                                    self._create_agents()
                    # 按住Q/1持续加力
                    if left_force_pressed:
                        action["left_force"] = True
                    if right_force_pressed:
                        action2["right_force"] = True
                    if left_spin_pressed:
                        action["left_spin"] = True
                    if right_spin_pressed:
                        action2["right_spin"] = True
                    allowed_keys = ['move_left_x', 'move_left_y', 'move_right_x', 'move_right_y', 'left_force', 'right_force', 'left_spin', 'right_spin']
                    merged_action = {k: v for k, v in action.items() if k in allowed_keys}
                    merged_action2 = {k: v for k, v in action2.items() if k in allowed_keys}
                    # AI paddle
                    if self.left_ai != "Human" and self.left_agent:
                        ai_action_l = self.left_agent.get_action(self.env.game.get_state(), self.env)
                        action["move_left_x"] = ai_action_l.get("move_left_x", 0)
                        action["move_left_y"] = ai_action_l.get("move_left_y", 0)
                        action["left_force"] = ai_action_l.get("left_force", False)
                        action["left_spin"] = ai_action_l.get("left_spin", False)
                    if self.right_ai != "Human" and self.right_agent:
                        ai_action_r = self.right_agent.get_action(self.env.game.get_state(), self.env)
                        action["move_right_x"] = ai_action_r.get("move_right_x", 0)
                        action["move_right_y"] = ai_action_r.get("move_right_y", 0)
                        action["right_force"] = ai_action_r.get("right_force", False)
                        action["right_spin"] = ai_action_r.get("right_spin", False)
                    allowed_keys = ['move_left_x', 'move_left_y', 'move_right_x', 'move_right_y', 'left_force', 'right_force', 'left_spin', 'right_spin']
                    merged_action = {k: v for k, v in action.items() if k in allowed_keys}
                    merged_action2 = {k: v for k, v in action2.items() if k in allowed_keys}
                    # 合并动作
                    if self.mode == "human_vs_human":
                        merged_action.update(merged_action2)
                    # 暂停时跳过step
                    if self.paused:
                        self.draw(self.env.game.get_state(), spin_flag=spin_flag)
                        self.clock.tick(60)
                        continue
                    # step
                    step_result = self.env.step(merged_action)
                    state = step_result[0]
                    self.done = step_result[2]
                    spin_flag = merged_action.get("left_spin") or merged_action.get("right_spin")
                    self.draw(self.env.game.get_state(), spin_flag=spin_flag)
                    self.clock.tick(60)
                except Exception as e:
                    print("[EXCEPTION]", e)
                    traceback.print_exc()
                    self.clock.tick(60)
        except Exception as e:
            print("[FATAL]", e)
            traceback.print_exc()
            pygame.quit()
            sys.exit()

if __name__ == "__main__":
    gui = PingPongGUI()
    gui.run() 