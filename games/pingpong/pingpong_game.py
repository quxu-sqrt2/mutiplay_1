from games.base_game import BaseGame
import sys

PADDLE_SPEED = 10
BALL_INITIAL_SPEED = 0.25  # 初始速度更慢（降为原来一半）
WIN_SCORE = 11

class PingPongGame(BaseGame):
    def __init__(self, **kwargs):
        super().__init__(kwargs)
        self.reset()
        self.spin_timer = 0
        self.spin_direction = 0
        self.left_force_charge = 0  # 新增：左挡板蓄力
        self.right_force_charge = 0  # 新增：右挡板蓄力

    def reset(self):
        self.score_left = 0
        self.score_right = 0
        self.ball_pos = [0.5, 0.5]  # x, y
        self.ball_vx = BALL_INITIAL_SPEED
        self.ball_vy = 0.0
        self.left_paddle_x = 0.05
        self.left_paddle_y = 0.5
        self.right_paddle_x = 0.95
        self.right_paddle_y = 0.5
        self.last_scorer = None
        self.serve_dir = 1  # 1=右发球，-1=左发球
        self.left_force = False
        self.right_force = False
        self.spin_timer = 0
        self.spin_direction = 0
        self.left_force_charge = 0  # 新增
        self.right_force_charge = 0  # 新增
        print(f"[DEBUG] reset: score_left={self.score_left}, score_right={self.score_right}")
        return self.get_state()

    def step(self, action):
        print(f"[DEBUG] step: before, score_left={self.score_left}, score_right={self.score_right}, action={action}")
        reward = 0
        done = False
        info = {}
        # 记录本帧是否用力/旋转
        left_force = action.get("left_force", False)
        right_force = action.get("right_force", False)
        left_spin = action.get("left_spin", False)
        right_spin = action.get("right_spin", False)
        move_left_x = action.get("move_left_x", 0)
        move_left_y = action.get("move_left_y", 0)
        move_right_x = action.get("move_right_x", 0)
        move_right_y = action.get("move_right_y", 0)
        # 蓄力逻辑
        if left_force:
            self.left_force_charge = min(self.left_force_charge + 1, 20)  # 最多蓄20帧
        else:
            pass  # 松开不清零，击球后才清零
        if right_force:
            self.right_force_charge = min(self.right_force_charge + 1, 20)
        else:
            pass
        # 左挡板移动
        if move_left_x == 1:
            self.left_paddle_x = min(0.2, self.left_paddle_x + PADDLE_SPEED/100)
        elif move_left_x == -1:
            self.left_paddle_x = max(0.0, self.left_paddle_x - PADDLE_SPEED/100)
        if move_left_y == 1:
            self.left_paddle_y = min(1.0, self.left_paddle_y + PADDLE_SPEED/100)
        elif move_left_y == -1:
            self.left_paddle_y = max(0.0, self.left_paddle_y - PADDLE_SPEED/100)
        # 右挡板移动
        if move_right_x == 1:
            self.right_paddle_x = min(1.0, self.right_paddle_x + PADDLE_SPEED/100)
        elif move_right_x == -1:
            self.right_paddle_x = max(0.8, self.right_paddle_x - PADDLE_SPEED/100)
        if move_right_y == 1:
            self.right_paddle_y = min(1.0, self.right_paddle_y + PADDLE_SPEED/100)
        elif move_right_y == -1:
            self.right_paddle_y = max(0.0, self.right_paddle_y - PADDLE_SPEED/100)
        # 香蕉球曲线spin效果
        if self.spin_timer > 0:
            self.ball_vy += 0.08 * self.spin_direction  # 持续弯曲更明显
            self.spin_timer -= 1
            if self.spin_timer == 0:
                self.spin_direction = 0
        # 球运动
        self.ball_pos[0] += self.ball_vx/100
        self.ball_pos[1] += self.ball_vy/100
        # 碰撞检测（上下边界）
        if self.ball_pos[1] <= 0 or self.ball_pos[1] >= 1:
            self.ball_vy = -self.ball_vy
        # 左挡板碰撞
        if self.ball_pos[0] <= self.left_paddle_x + 0.02:
            if abs(self.ball_pos[1] - self.left_paddle_y) < 0.1:
                # 蓄力倍数：1.0~3.0
                mult = 1.0 + 0.3 * self.left_force_charge
                mult = min(mult, 3.0)
                self.ball_vx = abs(self.ball_vx) * mult
                # 旋转：香蕉球，持续影响vy
                spin_effect = 0.0
                if left_spin:
                    spin_effect = 0.3 * (move_left_y if move_left_y != 0 else 1)
                    self.spin_timer = 50  # 持续50帧
                    self.spin_direction = -move_left_y if move_left_y != 0 else 1  # 没动默认向上
                self.ball_vy = self.ball_vy * mult + (self.ball_pos[1] - self.left_paddle_y) * 2 + spin_effect
                self.left_force_charge = 0  # 击球后清零
            else:
                self.score_right += 1
                self.last_scorer = 2
                self._serve()
        # 右挡板碰撞
        elif self.ball_pos[0] >= self.right_paddle_x - 0.02:
            if abs(self.ball_pos[1] - self.right_paddle_y) < 0.1:
                mult = 1.0 + 0.3 * self.right_force_charge
                mult = min(mult, 3.0)
                self.ball_vx = -abs(self.ball_vx) * mult
                # 旋转：香蕉球，持续影响vy
                spin_effect = 0.0
                if right_spin:
                    spin_effect = 0.3 * (move_right_y if move_right_y != 0 else 1)
                    self.spin_timer = 50
                    self.spin_direction = -move_right_y if move_right_y != 0 else 1
                self.ball_vy = self.ball_vy * mult + (self.ball_pos[1] - self.right_paddle_y) * 2 + spin_effect
                self.right_force_charge = 0  # 击球后清零
            else:
                self.score_left += 1
                self.last_scorer = 1
                self._serve()
        # 终局
        if self.score_left >= WIN_SCORE or self.score_right >= WIN_SCORE:
            done = True
            reward = 1 if self.score_left > self.score_right else -1
        print(f"[DEBUG] step: after, score_left={self.score_left}, score_right={self.score_right}, done={done}")
        return self.get_state(), reward, done, info

    def is_terminal(self):
        result = self.score_left >= WIN_SCORE or self.score_right >= WIN_SCORE
        print(f"[DEBUG] is_terminal: score_left={self.score_left}, score_right={self.score_right}, result={result}")
        return result

    def get_winner(self):
        print(f"[DEBUG] get_winner: score_left={self.score_left}, score_right={self.score_right}")
        if self.score_left >= WIN_SCORE:
            return 1
        elif self.score_right >= WIN_SCORE:
            return 2
        return None

    def get_state(self):
        return {
            "score_left": self.score_left,
            "score_right": self.score_right,
            "ball_pos": self.ball_pos[:],
            "ball_vx": self.ball_vx,
            "ball_vy": self.ball_vy,
            "left_paddle_x": self.left_paddle_x,
            "left_paddle_y": self.left_paddle_y,
            "right_paddle_x": self.right_paddle_x,
            "right_paddle_y": self.right_paddle_y,
            "last_scorer": self.last_scorer
        }

    def get_valid_actions(self, player=None):
        # 所有方向都可用，force字段可为True/False
        return [
            {"move_left_x": dx, "move_left_y": dy, "move_right_x": rx, "move_right_y": ry, "left_force": lf, "right_force": rf}
            for dx in [-1, 0, 1]
            for dy in [-1, 0, 1]
            for rx in [-1, 0, 1]
            for ry in [-1, 0, 1]
            for lf in [False, True]
            for rf in [False, True]
        ]

    def _serve(self):
        self.ball_pos = [0.5, 0.5]
        self.ball_vx = self.serve_dir * BALL_INITIAL_SPEED
        self.ball_vy = 0.0
        self.serve_dir *= -1

    def render(self):
        print(f"Score: {self.score_left} - {self.score_right}")
        print(f"Ball pos: {self.ball_pos}, Ball vx: {self.ball_vx:.2f}, vy: {self.ball_vy:.2f}")
        print(f"Left paddle: ({self.left_paddle_x:.2f}, {self.left_paddle_y:.2f}), Right paddle: ({self.right_paddle_x:.2f}, {self.right_paddle_y:.2f})") 