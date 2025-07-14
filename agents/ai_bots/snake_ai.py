"""
贪吃蛇专用AI智能体
"""

import random
import numpy as np
from agents.base_agent import BaseAgent

class SnakeAI(BaseAgent):
    """贪吃蛇AI智能体"""
    
    def __init__(self, name="SnakeAI", player_id=1):
        super().__init__(name, player_id)
    
    def get_action(self, observation, env):
        """获取动作"""
        valid_actions = env.get_valid_actions()
        if not valid_actions:
            return None
        
        # 获取当前蛇的信息
        game = env.game
        if self.player_id == 1:
            snake = game.snake1
            current_direction = game.direction1
        else:
            snake = game.snake2
            current_direction = game.direction2
        
        if not snake:
            return random.choice(valid_actions)
        
        head = snake[0]
        
        # 寻找最近的食物
        if game.foods:
            target_food = self._find_nearest_food(head, game.foods)
            best_action = self._move_towards_target(head, target_food, current_direction, game)
            
            # 检查这个动作是否安全
            if self._is_safe_action(best_action, head, game):
                return best_action
        
        # 如果没有安全的路径到食物，寻找安全的移动
        safe_actions = []
        for action in valid_actions:
            if self._is_safe_action(action, head, game):
                safe_actions.append(action)
        
        if safe_actions:
            return random.choice(safe_actions)
        
        # 如果没有安全动作，随机选择
        return random.choice(valid_actions)
    
    def _find_nearest_food(self, head, foods):
        """找到最近的食物"""
        min_distance = float('inf')
        nearest_food = foods[0]
        
        for food in foods:
            distance = abs(head[0] - food[0]) + abs(head[1] - food[1])
            if distance < min_distance:
                min_distance = distance
                nearest_food = food
        
        return nearest_food
    
    def _move_towards_target(self, head, target, current_direction, game):
        """向目标移动"""
        head_x, head_y = head
        target_x, target_y = target
        
        # 计算到目标的方向
        dx = target_x - head_x
        dy = target_y - head_y
        
        # 优先级：距离较远的轴优先
        if abs(dx) > abs(dy):
            if dx > 0:
                return (1, 0)  # 下
            elif dx < 0:
                return (-1, 0)  # 上
        
        if dy > 0:
            return (0, 1)  # 右
        elif dy < 0:
            return (0, -1)  # 左
        
        # 如果已经在目标位置，保持当前方向
        return current_direction
    
    def _is_safe_action(self, action, head, game):
        """检查动作是否安全"""
        # action已经是方向元组 (dx, dy)
        direction = action
        new_head = (head[0] + direction[0], head[1] + direction[1])
        
        # 检查边界
        if (new_head[0] < 0 or new_head[0] >= game.board_size or
            new_head[1] < 0 or new_head[1] >= game.board_size):
            return False
        
        # 检查是否撞到蛇身
        if new_head in game.snake1[:-1] or new_head in game.snake2[:-1]:
            return False
        
        return True


class SmartSnakeAI(BaseAgent):
    """更智能的贪吃蛇AI"""
    
    def __init__(self, name="SmartSnakeAI", player_id=1):
        super().__init__(name, player_id)
    
    def get_action(self, observation, env):
        """使用A*算法寻路的贪吃蛇AI"""
        valid_actions = env.get_valid_actions()
        if not valid_actions:
            return None
        
        game = env.game
        if self.player_id == 1:
            snake = game.snake1
            current_direction = game.direction1
        else:
            snake = game.snake2
            current_direction = game.direction2
        
        if not snake:
            return random.choice(valid_actions)
        
        head = snake[0]
        
        # 使用A*算法寻找到最近食物的路径
        if game.foods:
            target_food = self._find_nearest_food(head, game.foods)
            path = self._a_star_pathfinding(head, target_food, game)
            
            if path and len(path) > 1:
                next_pos = path[1]  # path[0]是当前位置
                action = self._pos_to_action(head, next_pos)
                if action in valid_actions:
                    return action
        
        # 如果A*失败，使用安全策略
        return self._get_safe_action(head, game, valid_actions)
    
    def _find_nearest_food(self, head, foods):
        """找到最近的食物"""
        min_distance = float('inf')
        nearest_food = foods[0]
        
        for food in foods:
            distance = abs(head[0] - food[0]) + abs(head[1] - food[1])
            if distance < min_distance:
                min_distance = distance
                nearest_food = food
        
        return nearest_food
    
    def _a_star_pathfinding(self, start, goal, game):
        """A*寻路算法（简化版，避免卡住）"""
        from heapq import heappush, heappop
        import time
        
        start_time = time.time()
        max_iterations = 100  # 限制最大迭代次数
        
        def heuristic(a, b):
            return abs(a[0] - b[0]) + abs(a[1] - b[1])
        
        def get_neighbors(pos):
            x, y = pos
            neighbors = []
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = x + dx, y + dy
                if (0 <= nx < game.board_size and 0 <= ny < game.board_size):
                    # 检查是否撞到蛇身（但允许撞到尾部，因为尾部会移动）
                    if ((nx, ny) not in game.snake1[:-1] and 
                        (nx, ny) not in game.snake2[:-1]):
                        neighbors.append((nx, ny))
            return neighbors
        
        open_set = [(0, start)]
        came_from = {}
        g_score = {start: 0}
        f_score = {start: heuristic(start, goal)}
        iterations = 0
        
        while open_set and iterations < max_iterations:
            iterations += 1
            
            # 检查超时
            if time.time() - start_time > 0.5:  # 500ms超时
                break
                
            current = heappop(open_set)[1]
            
            if current == goal:
                # 重构路径
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                path.append(start)
                return path[::-1]
            
            for neighbor in get_neighbors(current):
                tentative_g = g_score[current] + 1
                
                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f_score[neighbor] = tentative_g + heuristic(neighbor, goal)
                    heappush(open_set, (f_score[neighbor], neighbor))
        
        return None  # 没有找到路径
    
    def _pos_to_action(self, current_pos, next_pos):
        """将位置转换为动作"""
        dx = next_pos[0] - current_pos[0]
        dy = next_pos[1] - current_pos[1]
        
        return (dx, dy)
    
    def _get_safe_action(self, head, game, valid_actions):
        """获取安全的动作"""
        safe_actions = []
        
        for action in valid_actions:
            # action已经是方向元组
            new_head = (head[0] + action[0], head[1] + action[1])
            
            # 检查是否安全
            if (0 <= new_head[0] < game.board_size and 
                0 <= new_head[1] < game.board_size and
                new_head not in game.snake1[:-1] and 
                new_head not in game.snake2[:-1]):
                safe_actions.append(action)
        
        if safe_actions:
            return random.choice(safe_actions)
        
        return random.choice(valid_actions) 