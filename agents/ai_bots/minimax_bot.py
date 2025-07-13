from agents.base_agent import BaseAgent
import copy
import time
import numpy as np

class MinimaxBot(BaseAgent):
    def __init__(self, name="MinimaxBot", player_id=1, max_depth=2):
        super().__init__(name, player_id)
        self.max_depth = max_depth
        self.timeout = 2.0  # 减少到2秒超时
        self.start_time = None
        self.nodes_evaluated = 0

    def get_action(self, observation, env):
        self.start_time = time.time()
        self.nodes_evaluated = 0
        
        # 获取所有有效动作
        all_valid_actions = env.get_valid_actions()
        if not all_valid_actions:
            return None
        
        # 快速处理：如果棋盘为空，直接返回中心位置
        if hasattr(env, 'board_size') and self._is_empty_board(env.game.board):
            center = env.board_size // 2
            return (center, center)
        
        # 如果max_depth=0，直接评估所有动作，不递归
        if self.max_depth == 0:
            return self._get_best_action_direct(all_valid_actions, env)
        
        # 动态调整搜索深度
        dynamic_depth = self._calculate_dynamic_depth(env)
        
        # 只考虑已有棋子周围2格半径的区域（减少搜索空间）
        valid_actions = self.get_nearby_actions(all_valid_actions, env, radius=2)
        
        # 限制搜索的动作数量
        if len(valid_actions) > 20:
            valid_actions = self.sort_actions(valid_actions, env)[:20]
        
        # 对动作进行排序，优先搜索更有希望的动作
        valid_actions = self.sort_actions(valid_actions, env)
        
        best_score = float('-inf')
        best_action = valid_actions[0] if valid_actions else all_valid_actions[0]
        
        # 迭代加深搜索
        for depth in range(1, dynamic_depth + 1):
            if self._is_timeout():
                break
                
            current_best_action = best_action
            
            for action in valid_actions:
                if self._is_timeout():
                    break
                    
                # 克隆游戏状态
                game_copy = env.game.clone()
                # 执行动作
                game_copy.step(action)
                # 计算分数（使用 alpha-beta 剪枝）
                score = self.minimax(game_copy, depth - 1, False, float('-inf'), float('inf'))
                
                if score > best_score:
                    best_score = score
                    best_action = action
            
            # 如果找到明显好的动作，提前停止
            if best_score >= 500:
                break
                
        return best_action
    
    def _calculate_dynamic_depth(self, env):
        """动态计算搜索深度"""
        if not hasattr(env, 'board_size'):
            return self.max_depth
            
        board = env.game.board
        move_count = np.sum(board != 0)
        
        # 根据游戏阶段调整深度
        if move_count < 10:
            return min(1, self.max_depth)  # 开局浅搜索
        elif move_count < 50:
            return min(2, self.max_depth)  # 中局中等深度
        else:
            return min(3, self.max_depth)  # 残局深搜索
    
    def _is_timeout(self):
        """检查是否超时"""
        if self.start_time is None:
            return False
        return time.time() - self.start_time > self.timeout
    
    def _get_best_action_direct(self, actions, env):
        """直接评估所有动作，不递归"""
        best_score = float('-inf')
        best_action = actions[0]
        
        for action in actions:
            if self._is_timeout():
                break
                
            # 克隆游戏状态
            game_copy = env.game.clone()
            # 执行动作
            game_copy.step(action)
            # 直接评估，不递归
            score = self.evaluate_position(game_copy)
            
            if score > best_score:
                best_score = score
                best_action = action
                
        return best_action
    
    def get_nearby_actions(self, all_actions, env, radius=2):
        """只返回已有棋子周围指定半径内的空位"""
        if not hasattr(env, 'board_size'):
            return all_actions
        
        board = env.game.board
        nearby_actions = set()
        
        # 遍历棋盘，找到所有已有棋子的位置
        for i in range(env.board_size):
            for j in range(env.board_size):
                if board[i][j] != 0:  # 有棋子的位置
                    # 添加周围指定半径内的空位
                    for di in range(-radius, radius + 1):
                        for dj in range(-radius, radius + 1):
                            ni, nj = i + di, j + dj
                            # 检查边界和是否为空位
                            if (0 <= ni < env.board_size and 
                                0 <= nj < env.board_size and 
                                board[ni][nj] == 0):
                                nearby_actions.add((ni, nj))
        
        # 如果附近没有空位，返回所有动作
        if not nearby_actions:
            return all_actions
        
        return list(nearby_actions)

    def sort_actions(self, actions, env):
        """对动作进行排序，优先搜索更有希望的动作"""
        if not hasattr(env, 'board_size'):
            return actions
        
        # 对于五子棋，优先选择中心位置和已有棋子周围的位置
        board = env.game.board
        center = env.board_size // 2
        
        def action_score(action):
            row, col = action
            score = 0
            
            # 中心位置得分高
            center_dist = abs(row - center) + abs(col - center)
            score += (env.board_size - center_dist) * 10
            
            # 已有棋子周围得分高
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    r, c = row + dr, col + dc
                    if (0 <= r < env.board_size and 0 <= c < env.board_size and 
                        board[r][c] != 0):
                        score += 5
            
            return score
        
        return sorted(actions, key=action_score, reverse=True)

    def minimax(self, game, depth, maximizing, alpha, beta):
        self.nodes_evaluated += 1
        
        # 检查超时
        if self._is_timeout():
            return 0
        
        # 终止条件：达到最大深度或游戏结束
        if depth == 0 or game.is_terminal():
            return self.evaluate_position(game)
        
        # 极端局面提前终止
        eval_score = self.evaluate_position(game)
        if eval_score >= 1000 or eval_score <= -1000:
            return eval_score
        
        valid_actions = game.get_valid_actions()
        if not valid_actions:
            return 0
        
        # 限制每层的动作数量
        if len(valid_actions) > 15:
            valid_actions = valid_actions[:15]
        
        if maximizing:
            max_score = float('-inf')
            for action in valid_actions:
                if self._is_timeout():
                    break
                    
                game_copy = game.clone()
                game_copy.step(action)
                score = self.minimax(game_copy, depth - 1, False, alpha, beta)
                max_score = max(max_score, score)
                alpha = max(alpha, score)
                if alpha >= beta:
                    break
            return max_score
        else:
            min_score = float('inf')
            for action in valid_actions:
                if self._is_timeout():
                    break
                    
                game_copy = game.clone()
                game_copy.step(action)
                score = self.minimax(game_copy, depth - 1, True, alpha, beta)
                min_score = min(min_score, score)
                beta = min(beta, score)
                if beta <= alpha:
                    break
            return min_score
    
    def evaluate_position(self, game):
        """评估函数"""
        if game.is_terminal():
            winner = game.get_winner()
            if winner == self.player_id:
                return 1000  # 获胜
            elif winner is not None:
                return -1000  # 失败
            else:
                return 0  # 平局
        
        # 简单评估：计算连子数
        if hasattr(game, 'board'):
            return self.evaluate_gomoku_position(game)
        else:
            return 0
    
    def evaluate_gomoku_position(self, game):
        # 只评估最近一步
        if hasattr(game, 'last_move') and game.last_move is not None:
            row, col = game.last_move
            player = game.board[row][col]
            if player == self.player_id:
                return self.quick_evaluate(game.board, row, col)
            else:
                return -self.quick_evaluate(game.board, row, col)
        return 0

    def quick_evaluate(self, board, row, col):
        """快速评估单个位置"""
        player = board[row][col]
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        max_count = 0
        
        for dr, dc in directions:
            count = 1
            # 只检查一个方向，避免重复
            r, c = row + dr, col + dc
            while (0 <= r < len(board) and 0 <= c < len(board[0]) and 
                   board[r][c] == player):
                count += 1
                r += dr
                c += dc
            
            max_count = max(max_count, count)
        
        # 简化评分，减少计算量
        if max_count >= 5:
            return 1000
        elif max_count == 4:
            return 50
        elif max_count == 3:
            return 5
        else:
            return max_count
    
    def _is_empty_board(self, board):
        """检查棋盘是否为空"""
        return not np.any(board != 0)
        
       