import math
import functools
import numpy as np
from agents.base_agent import BaseAgent


class MinimaxBot(BaseAgent):
    def __init__(self, name="GomokuMinimax", player_id=1, max_depth=2):
        super().__init__(name, player_id)
        self.max_depth = max_depth

    # ----------------------------------------------------------

    def get_action(self, obs, env):
        board = env.game.board
        total_stones = np.count_nonzero(board)
        board_size = env.game.board_size

        # 1) 早期阶段（≤ 225 子）：只搜“邻域 + 降深度”
        if total_stones <= 225:
            radius = 2
            candidates = set()
            for r, c in zip(*np.where(board != 0)):
                for dr in range(-radius, radius + 1):
                    for dc in range(-radius, radius + 1):
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < board_size and 0 <= nc < board_size and board[nr, nc] == 0:
                            candidates.add((nr, nc))
            valid = list(candidates) or env.get_valid_actions()[:8]
            depth = 1
        else:
            valid = env.get_valid_actions()
            valid = self._opening_moves(valid, board, board_size)
            depth = self.max_depth

        key = self._encode(env.game)
        _, best = self._alphabeta(key, depth,
                                  alpha=-math.inf, beta=math.inf,
                                  maximizing=True)
        return best if best in valid else valid[0]

    # ----------------------------------------------------------
    def _point_score(self, board, r, c, who, attack=True):
        lines = [(1, 0), (0, 1), (1, 1), (1, -1)]
        total = 0
        for dx, dy in lines:
            cnt = 1
            open_left = open_right = False

            # 正方向
            for k in range(1, 5):
                x, y = r + dx * k, c + dy * k
                if not (0 <= x < 15 and 0 <= y < 15):
                    break
                if board[x, y] == who:
                    cnt += 1
                elif board[x, y] == 0:
                    open_right = True
                    break
                else:
                    break

            # 反方向
            for k in range(1, 5):
                x, y = r - dx * k, c - dy * k
                if not (0 <= x < 15 and 0 <= y < 15):
                    break
                if board[x, y] == who:
                    cnt += 1
                elif board[x, y] == 0:
                    open_left = True
                    break
                else:
                    break

            # 打分表
            if cnt >= 5:
                total += 5000
            elif cnt == 4 and open_left and open_right:   # 活 4
                total += 2000
            elif cnt == 4 and (open_left or open_right):  # 冲 4
                total += 500 if attack else 1000
            elif cnt == 3 and open_left and open_right:   # 活 3
                total += 200 if attack else 600
            elif cnt == 3 and (open_left or open_right):  # 冲 3
                total += 50 if attack else 150
            elif cnt == 2 and open_left and open_right:   # 活 2
                total += 10 if attack else 30
        return total

    def _opening_moves(self, valid, board, board_size):
        """只保留已有棋子的 1 格邻域，上限 5 点"""
        if np.count_nonzero(board) < 16:
            neighbors = set()
            for r in range(board_size):
                for c in range(board_size):
                    if board[r, c] == 0:
                        continue
                    for dr, dc in [(-1, -1), (-1, 0), (-1, 1),
                                   (0, -1), (0, 1),
                                   (1, -1), (1, 0), (1, 1)]:
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < board_size and 0 <= nc < board_size and board[nr, nc] == 0:
                            neighbors.add((nr, nc))
            return list(neighbors)[:5] or valid[:5]
        return valid

    def _find_threats(self, board, opp):
        threats = set()
        size = board.shape[0]
        for r in range(size):
            for c in range(size):
                if board[r, c] != 0:
                    continue
                score = self._point_score(board, r, c, opp, attack=True)
                if score >= 500:  # 活4/冲4/活3
                    for dr, dc in [(-1, -1), (-1, 0), (-1, 1),
                                   (0, -1), (0, 1),
                                   (1, -1), (1, 0), (1, 1)]:
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < size and 0 <= nc < size and board[nr, nc] == 0:
                            threats.add((nr, nc))
        return list(threats) if threats else None

    # ----------------------------------------------------------
    def _is_immediate_win(self, board, r, c, player):
        """检查在(r,c)落子后是否形成五子连珠"""
        directions = [(1, 0), (0, 1), (1, 1), (1, -1)]
        for dx, dy in directions:
            count = 1  # 当前落子
            # 正方向
            for k in range(1, 5):
                x, y = r + dx * k, c + dy * k
                if 0 <= x < 15 and 0 <= y < 15 and board[x, y] == player:
                    count += 1
                else:
                    break
            # 反方向
            for k in range(1, 5):
                x, y = r - dx * k, c - dy * k
                if 0 <= x < 15 and 0 <= y < 15 and board[x, y] == player:
                    count += 1
                else:
                    break
            if count >= 5:
                return True
        return False

    # ----------------------------------------------------------
    @functools.lru_cache(maxsize=200_000)
    def _alphabeta(self, key, depth, alpha, beta, maximizing):
        board, move_cnt, cur_player = self._decode(key)
        shadow = _ShadowGomoku(board, move_cnt, cur_player)

        # 己方回合：检查是否可立即获胜
        if cur_player == self.player_id:
            for r, c in shadow.get_valid_actions():
                if self._is_immediate_win(board, r, c, cur_player):
                    return math.inf, (r, c)

        if depth == 0 or shadow.is_terminal():
            return self._evaluate(shadow), None

        opp = 3 - self.player_id
        threats = None
        if cur_player != self.player_id:
            threats = self._find_threats(board, opp)

        valid = threats if threats else shadow.get_valid_actions()

        best_action = None
        for r, c in valid:
            new_board = board.copy()
            new_board[r, c] = cur_player
            new_key = self._encode_tuple(new_board, move_cnt + 1, 3 - cur_player)
            score, _ = self._alphabeta(new_key, depth - 1, alpha, beta, not maximizing)

            if maximizing:
                if score > alpha:
                    alpha, best_action = score, (r, c)
                if alpha >= beta:
                    break
            else:
                if score < beta:
                    beta, best_action = score, (r, c)
                if beta <= alpha:
                    break
        return (alpha if maximizing else beta), best_action

    # ----------------------------------------------------------
    def _encode(self, game):
        return (game.board.astype(np.int8).tobytes(),
                game.move_count,
                game.current_player)

    def _encode_tuple(self, board, move_cnt, cur_player):
        return (board.astype(np.int8).tobytes(), move_cnt, cur_player)

    def _decode(self, key):
        board_bytes, move_cnt, cur_player = key
        size = int(math.sqrt(len(board_bytes)))
        board = np.frombuffer(board_bytes, dtype=np.int8).reshape(size, size)
        return board, move_cnt, cur_player

    # ----------------------------------------------------------
    def _evaluate(self, shadow):
        if shadow.get_winner() == self.player_id:
            return 10000
        if shadow.get_winner() == 3 - self.player_id:
            return -10000

        board = shadow.board
        size = shadow.board_size
        player = self.player_id
        opp = 3 - player

        score = 0

        # 1. 进攻
        for r in range(size):
            for c in range(size):
                if board[r, c] != 0:
                    continue
                score += self._point_score(board, r, c, player, attack=True)

        # 2. 防守（权重放大）
        DEFENSE_WEIGHT = 3.5
        for r in range(size):
            for c in range(size):
                if board[r, c] != 0:
                    continue
                score += DEFENSE_WEIGHT * self._point_score(board, r, c, opp, attack=False)

        return score


class _ShadowGomoku:
    def __init__(self, board, move_cnt, cur_player):
        self.board = board
        self.move_count = move_cnt
        self.current_player = cur_player
        self.board_size = board.shape[0]
        self.win_length = 5

    def get_valid_actions(self):
        return [(i, j) for i in range(self.board_size)
                for j in range(self.board_size) if self.board[i, j] == 0]

    def is_terminal(self):
        return self.get_winner() is not None or self.move_count >= self.board_size ** 2

    def get_winner(self):
        size, win = self.board_size, self.win_length
        for i in range(size):
            for j in range(size):
                p = self.board[i, j]
                if p == 0:
                    continue
                for dx, dy in [(1, 0), (0, 1), (1, 1), (1, -1)]:
                    cnt = 1
                    for k in range(1, win):
                        x, y = i + dx * k, j + dy * k
                        if 0 <= x < size and 0 <= y < size and self.board[x, y] == p:
                            cnt += 1
                        else:
                            break
                    if cnt >= win:
                        return int(p)
        return None