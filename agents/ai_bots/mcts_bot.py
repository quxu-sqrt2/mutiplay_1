"""
MCTS Bot
使用蒙特卡洛树搜索算法
"""

import time
import random
import math
from typing import Dict, List, Tuple, Any, Optional
from agents.base_agent import BaseAgent
import config
import copy

class MCTSNode:
    def __init__(self, state, parent=None, action=None):
        self.state = state  # 游戏状态副本
        self.parent = parent
        self.action = action
        self.children = {}  # action: MCTSNode
        self.visits = 0
        self.wins = 0

    def is_fully_expanded(self, valid_actions):
        return set(self.children.keys()) == set(valid_actions)

    def best_child(self, c=math.sqrt(2)):
        # UCB1选择
        best_score = float('-inf')
        best = None
        for child in self.children.values():
            if child.visits == 0:
                score = float('inf')
            else:
                score = child.wins / child.visits + c * math.sqrt(math.log(self.visits) / child.visits)
            if score > best_score:
                best_score = score
                best = child
        return best

class MCTSBot(BaseAgent):
    def __init__(self, name: str = "MCTSBot", player_id: int = 1, simulation_count: int = 100, timeout: float = 5.0):
        super().__init__(name, player_id)
        ai_config = getattr(config, 'AI_CONFIGS', {}).get('mcts', {})
        self.simulation_count = ai_config.get('simulation_count', simulation_count)
        self.timeout = ai_config.get('timeout', timeout)

    def get_action(self, observation: Any, env: Any) -> Any:
        start_time = time.time()
        root = MCTSNode(env.game.clone())
        valid_actions = env.get_valid_actions()
        if not valid_actions:
            return None
        # 扩展根节点
        for action in valid_actions:
            if action not in root.children:
                next_state = root.state.clone()
                next_state.step(action)
                root.children[action] = MCTSNode(next_state, parent=root, action=action)
        simulations = 0
        while simulations < self.simulation_count and (time.time() - start_time) < self.timeout:
            node, path = self._select(root)
            reward = self._simulate(node.state)
            self._backpropagate(path, reward)
            simulations += 1
        # 选择访问次数最多的动作
        best_action = max(root.children.items(), key=lambda item: item[1].visits)[0]
        move_time = time.time() - start_time
        self.total_moves += 1
        self.total_time += move_time
        return best_action

    def _get_nearby_actions(self, board, all_actions, radius=2):
        # 剪枝：只返回已有棋子周围radius格内的空位
        size = board.shape[0]
        stones = [(i, j) for i in range(size) for j in range(size) if board[i, j] != 0]
        if not stones:
            return all_actions
        nearby = set()
        for i, j in stones:
            for di in range(-radius, radius+1):
                for dj in range(-radius, radius+1):
                    ni, nj = i+di, j+dj
                    if 0<=ni<size and 0<=nj<size and board[ni, nj]==0:
                        nearby.add((ni, nj))
        return list(nearby)

    def _has_n_in_row(self, board, player, n):
        size = board.shape[0]
        for i in range(size):
            for j in range(size):
                if board[i, j] != 0:
                    continue
                for dx, dy in [(1,0),(0,1),(1,1),(1,-1)]:
                    count = 1
                    for k in range(1, n):
                        x, y = i+dx*k, j+dy*k
                        if 0<=x<size and 0<=y<size and board[x, y]==player:
                            count += 1
                        else:
                            break
                    if count == n:
                        return (i, j)
        return None

    def _simulate(self, state):
        sim_state = state.clone()
        player = self.player_id
        opponent = 3 - player
        while not sim_state.is_terminal():
            # 剪枝：只考虑周围2格内的空位
            board = getattr(sim_state, 'board', None)
            if board is None and hasattr(sim_state, 'get_state'):
                state_dict = sim_state.get_state()
                board = state_dict.get('board', None)
            all_actions = sim_state.get_valid_actions()
            valid_actions = self._get_nearby_actions(board, all_actions, radius=2)
            if not valid_actions:
                break
            # 1. 能直接获胜
            for action in valid_actions:
                test_state = sim_state.clone()
                test_state.step(action)
                if test_state.get_winner() == player:
                    sim_state.step(action)
                    break
            else:
                # 2. 能直接防守
                for action in valid_actions:
                    test_state = sim_state.clone()
                    test_state.current_player = opponent
                    test_state.step(action)
                    if test_state.get_winner() == opponent:
                        sim_state.step(action)
                        break
                else:
                    # 3. 防对方三连
                    threat_action = self._has_n_in_row(board, opponent, 3)
                    if threat_action and threat_action in valid_actions:
                        sim_state.step(threat_action)
                    else:
                        # 4. 优先连子
                        best_action = None
                        max_neighbors = -1
                        for action in valid_actions:
                            row, col = action
                            neighbors = 0
                            for dr in [-1, 0, 1]:
                                for dc in [-1, 0, 1]:
                                    if dr == 0 and dc == 0:
                                        continue
                                    r, c = row + dr, col + dc
                                    if board is not None and 0 <= r < board.shape[0] and 0 <= c < board.shape[1]:
                                        if board[r, c] == player:
                                            neighbors += 1
                            if neighbors > max_neighbors:
                                max_neighbors = neighbors
                                best_action = action
                        if best_action:
                            sim_state.step(best_action)
                        else:
                            # 5. 实在没招，随机
                            sim_state.step(random.choice(valid_actions))
        winner = sim_state.get_winner()
        if winner == self.player_id:
            return 1
        elif winner is not None:
            return -1
        else:
            return 0

    def _select(self, node):
        path = [node]
        while node.children:
            node = node.best_child()
            path.append(node)
            # 剪枝：只扩展周围2格内的空位
            board = getattr(node.state, 'board', None)
            if board is None and hasattr(node.state, 'get_state'):
                state_dict = node.state.get_state()
                board = state_dict.get('board', None)
            all_actions = node.state.get_valid_actions()
            valid_actions = self._get_nearby_actions(board, all_actions, radius=2)
            if not node.is_fully_expanded(valid_actions):
                for action in valid_actions:
                    if action not in node.children:
                        next_state = node.state.clone()
                        next_state.step(action)
                        child = MCTSNode(next_state, parent=node, action=action)
                        node.children[action] = child
                        path.append(child)
                        return child, path
        return node, path

    def _backpropagate(self, path, reward):
        for node in reversed(path):
            node.visits += 1
            node.wins += reward

    def reset(self):
        super().reset()

    def get_info(self) -> Dict[str, Any]:
        info = super().get_info()
        info.update({
            'type': 'MCTS',
            'description': '树结构+UCB1+可插拔模拟策略的MCTSBot',
            'strategy': f'MCTS with {self.simulation_count} simulations',
            'timeout': self.timeout
        })
        return info 