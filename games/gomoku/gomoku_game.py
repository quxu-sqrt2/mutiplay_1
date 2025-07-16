"""
五子棋游戏逻辑
"""

import numpy as np
from typing import Dict, List, Tuple, Any, Optional
from games.base_game import BaseGame
import config


class GomokuGame(BaseGame):
    """五子棋游戏"""

    def __init__(self, board_size: int = 15, win_length: int = 5, **kwargs):
        
        self.board_size = board_size
        self.win_length = win_length
        super().__init__({"board_size": board_size, "win_length": win_length})
        self.reset()

    # ------------------------------------------------------------------
    # 基本接口
    # ------------------------------------------------------------------
    def reset(self) -> Dict[str, Any]:
        self.board = np.zeros((self.board_size, self.board_size), dtype=int)
        self.current_player = 1
        self.game_state = config.GameState.ONGOING
        self.move_count = 0
        self.history: List[Tuple[int, int]] = []  # 只记录坐标
        return self.get_state()

    def step(self, action: Tuple[int, int]) -> Tuple[Dict[str, Any], float, bool, Dict]:
        row, col = action
        if self.board[row, col] != 0:
            return self.get_state(), -1, True, {"error": "Invalid move"}

        self.board[row, col] = self.current_player
        self.history.append(action)
        self.move_count += 1
        done = self.is_terminal()
        reward = 1.0 if self.get_winner() == self.current_player else 0.0
        if done and self.get_winner() is None:  # 平局
            reward = 0.5
        self.switch_player()
        return self.get_state(), reward, done, {}

    def undo(self):
        if not self.history:
            return
        r, c = self.history.pop()
        self.board[r, c] = 0
        self.move_count -= 1
        self.switch_player()

    def to_bytes(self) -> bytes:
        # 棋盘展平成 uint8 数组，再拼当前玩家
        board_bytes = self.board.astype(np.uint8).tobytes()
        player_byte = np.uint8(self.current_player).tobytes()
        return board_bytes + player_byte

    def get_valid_actions(self, player: int = None) -> List[Tuple[int, int]]:
        """返回所有空位坐标"""
        return [
            (i, j)
            for i in range(self.board_size)
            for j in range(self.board_size)
            if self.board[i, j] == 0
        ]

    def is_terminal(self) -> bool:
        return self.get_winner() is not None or self.move_count >= self.board_size ** 2

    def get_winner(self) -> Optional[int]:
        """返回获胜玩家 1/2，平局或进行中返回 None"""
        for i in range(self.board_size):
            for j in range(self.board_size):
                if self.board[i, j] == 0:
                    continue
                player = self.board[i, j]
                for dx, dy in ((1, 0), (0, 1), (1, 1), (1, -1)):
                    count = 1
                    for k in (1, -1):
                        x, y = i + k * dx, j + k * dy
                        while (
                            0 <= x < self.board_size
                            and 0 <= y < self.board_size
                            and self.board[x, y] == player
                        ):
                            count += 1
                            x += k * dx
                            y += k * dy
                    if count >= self.win_length:
                        return player
        return None

    # ------------------------------------------------------------------
    # 观察与克隆
    # ------------------------------------------------------------------
    def get_state(self) -> Dict[str, Any]:
        return {
            "board": self.board.copy(),
            "current_player": self.current_player,
            "game_state": self.game_state,
            "move_count": self.move_count,
        }

    def render(self) -> np.ndarray:
        return self.board.copy()

    def clone(self) -> "GomokuGame":
        import copy

        new_game = GomokuGame(self.board_size, self.win_length)
        new_game.board = self.board.copy()
        new_game.current_player = self.current_player
        new_game.game_state = self.game_state
        new_game.move_count = self.move_count
        new_game.history = copy.deepcopy(self.history)
        return new_game

    # ------------------------------------------------------------------
    # 额外工具
    # ------------------------------------------------------------------
    def get_action_space(self):
        return [(i, j) for i in range(self.board_size) for j in range(self.board_size)]

    def get_observation_space(self):
        return {
            "board": (self.board_size, self.board_size),
            "current_player": 1,
            "valid_actions": self.get_valid_actions(),
        }

    def get_board_string(self) -> str:
        symbols = {0: ".", 1: "X", 2: "O"}
        out = "   " + " ".join(f"{i:2d}" for i in range(self.board_size)) + "\n"
        for i in range(self.board_size):
            out += f"{i:2d} "
            out += " ".join(symbols[self.board[i, j]] for j in range(self.board_size))
            out += "\n"
        return out

    def print_board(self):
        print(self.get_board_string())