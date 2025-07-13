from agents.base_agent import BaseAgent
import copy
import time

class MinimaxBot(BaseAgent):
    def __init__(self, name="MinimaxBot", player_id=1, max_depth=2):
        super().__init__(name, player_id)
        self.max_depth = max_depth
        self.timeout = 5.0  # 5秒超时

    def get_action(self, observation, env):
        # 获取所有有效动作
        all_valid_actions = env.get_valid_actions()
        if not all_valid_actions:
            return None
        
        # 只考虑已有棋子周围3格半径的区域
        valid_actions = self.get_nearby_actions(all_valid_actions, env)
        
        # 对动作进行排序，优先搜索更有希望的动作
        valid_actions = self.sort_actions(valid_actions, env)
        
        best_score = float('-inf')
        best_action = valid_actions[0] if valid_actions else all_valid_actions[0]
        
        for action in valid_actions:
            # 克隆游戏状态
            game_copy = env.game.clone()
            # 执行动作
            game_copy.step(action)
            # 计算分数（使用 alpha-beta 剪枝）
            score = self.minimax(game_copy, self.max_depth - 1, False, float('-inf'), float('inf'))
            
            if score > best_score:
                best_score = score
                best_action = action
                
        return best_action
    
    def get_nearby_actions(self, all_actions, env):
        """只返回已有棋子周围3格半径内的空位"""
        if not hasattr(env, 'board_size'):
            return all_actions
        
        board = env.game.board
        nearby_actions = set()
        
        # 遍历棋盘，找到所有已有棋子的位置
        for i in range(env.board_size):
            for j in range(env.board_size):
                if board[i][j] != 0:  # 有棋子的位置
                    # 添加周围3格半径内的空位
                    for di in range(-3, 4):
                        for dj in range(-3, 4):
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
        
        if maximizing:
            max_score = float('-inf')
            for action in valid_actions:
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
        
       