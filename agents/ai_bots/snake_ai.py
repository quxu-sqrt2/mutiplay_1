"""
贪吃蛇专用AI智能体
"""

import random
from heapq import heappush, heappop
from agents.base_agent import BaseAgent

# ---------------- 方向常量 ----------------
UP, DOWN, LEFT, RIGHT = (-1, 0), (1, 0), (0, -1), (0, 1)
DIRS = [UP, DOWN, LEFT, RIGHT]
DIR_NAME = {UP: "UP", DOWN: "DOWN", LEFT: "LEFT", RIGHT: "RIGHT"}


# =======================================================================
# 1. 简单贪心版 SnakeAI  （修复方向 + 障碍物判断）
# =======================================================================
class SnakeAI(BaseAgent):
    def __init__(self, name="SnakeAI", player_id=1):
        super().__init__(name, player_id)

    def get_action(self, obs, env):
        valid = env.get_valid_actions()
        if not valid:
            return None

        game = env.game
        snake = game.snake1 if self.player_id == 1 else game.snake2
        if not snake:
            return random.choice(valid)

        head = snake[0]
        foods = game.foods
        if foods:
            food = min(foods, key=lambda f: self._manhattan(head, f))
            for d in self._toward(head, food):      # 按优先级试探
                if d in valid and self._safe(head, d, game):
                    return d

        # 没有好吃的，先保命
        safe = [d for d in valid if self._safe(head, d, game)]
        return random.choice(safe or valid)

    # ---------- 工具 ----------
    @staticmethod
    def _manhattan(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def _toward(self, cur, tgt):
        """按 dx/dy 绝对值大小给出优先方向序列"""
        cx, cy = cur
        tx, ty = tgt
        dx, dy = tx - cx, ty - cy
        if abs(dx) > abs(dy):
            return [(1, 0) if dx > 0 else (-1, 0),
                    (0, 1) if dy > 0 else (0, -1)]
        else:
            return [(0, 1) if dy > 0 else (0, -1),
                    (1, 0) if dx > 0 else (-1, 0)]

    def _safe(self, head, direction, game):
        nx, ny = head[0] + direction[0], head[1] + direction[1]
        if nx < 0 or nx >= game.board_size or ny < 0 or ny >= game.board_size:
            return False
        # 把自己尾巴视为空地（下一回合会移动）
        my_snake = game.snake1 if self.player_id == 1 else game.snake2
        other_snake = game.snake2 if self.player_id == 1 else game.snake1
        obstacles = set(game.snake1[:-1]) | set(game.snake2[:-1])
        return (nx, ny) not in obstacles


# =======================================================================
# 2. A* + 生存策略版 SmartSnakeAI   （精简版）
# =======================================================================
class SmartSnakeAI(BaseAgent):
    def __init__(self, name="SmartSnakeAI", player_id=1):
        super().__init__(name, player_id)

    def get_action(self, obs, env):
        valid = env.get_valid_actions()
        if not valid:
            return None

        game = env.game
        snake = game.snake1 if self.player_id == 1 else game.snake2
        if not snake:
            return random.choice(valid)

        head = snake[0]
        foods = game.foods

        # 1. 最近食物 + A*
        if foods:
            food = min(foods, key=lambda f: self._manhattan(head, f))
            path = self._astar(head, food, game)
            if path and len(path) > 1:
                action = self._to_action(head, path[1])
                if action in valid:
                    return action

        # 2. 最长生存步
        return self._survival(head, game, valid)

    # ---------- A* ----------
    def _astar(self, start, goal, game):
        obstacles = set(game.snake1[:-1]) | set(game.snake2[:-1])
        g = {start: 0}
        pq = [(self._manhattan(start, goal), start, [start])]

        while pq:
            _, cur, path = heappop(pq)
            if cur == goal:
                return path
            for nxt in self._neighbors(cur, game.board_size, obstacles):
                if nxt in g and g[cur] + 1 >= g.get(nxt, 1e9):
                    continue
                g[nxt] = g[cur] + 1
                heappush(pq, (g[nxt] + self._manhattan(nxt, goal), nxt, path + [nxt]))
        return None

    # ---------- 生存 BFS ----------
    def _survival(self, head, game, valid):
        obstacles = set(game.snake1[:-1]) | set(game.snake2[:-1])
        best = random.choice(valid)
        best_len = -1
        for d in valid:
            nxt = (head[0] + d[0], head[1] + d[1])
            if nxt in obstacles:
                continue
            if not (0 <= nxt[0] < game.board_size and 0 <= nxt[1] < game.board_size):
                continue
            length = self._max_steps(nxt, obstacles, game.board_size)
            if length > best_len:
                best_len, best = length, d
        return best

    def _max_steps(self, start, obstacles, board_size):
        q, seen = [start], {start}
        steps = 0
        while q:
            nq = []
            for p in q:
                for nb in self._neighbors(p, board_size, obstacles):
                    if nb not in seen:
                        seen.add(nb)
                        nq.append(nb)
            q = nq
            steps += 1
        return steps

    # ---------- 工具 ----------
    @staticmethod
    def _manhattan(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def _neighbors(self, pos, size, obstacles):
        x, y = pos
        for dx, dy in DIRS:
            nx, ny = x + dx, y + dy
            if 0 <= nx < size and 0 <= ny < size and (nx, ny) not in obstacles:
                yield (nx, ny)

    def _to_action(self, cur, nxt):
        return (nxt[0] - cur[0], nxt[1] - cur[1])