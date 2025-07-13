#!/usr/bin/env python3
"""
测试MinimaxBot性能优化效果
"""

import time
from games.gomoku import GomokuEnv
from agents.ai_bots.minimax_bot import MinimaxBot

def test_minimax_performance():
    """测试MinimaxBot性能"""
    print("=== MinimaxBot 性能测试 ===\n")
    
    # 创建环境
    env = GomokuEnv(board_size=15, win_length=5)
    
    # 测试不同深度和场景
    test_cases = [
        {"name": "开局测试", "moves": 5, "depth": 2},
        {"name": "中局测试", "moves": 20, "depth": 2},
        {"name": "残局测试", "moves": 50, "depth": 2},
    ]
    
    for test_case in test_cases:
        print(f"--- {test_case['name']} ---")
        
        # 重置环境
        observation, info = env.reset()
        
        # 模拟一些移动
        for i in range(test_case['moves']):
            if i % 2 == 0:
                # 玩家1移动
                action = (7, 7 + i//2)  # 简单的移动模式
            else:
                # 玩家2移动
                action = (8, 8 + i//2)
            
            if action in env.get_valid_actions():
                env.step(action)
        
        # 创建MinimaxBot
        bot = MinimaxBot(name="TestBot", player_id=1, max_depth=test_case['depth'])
        
        # 测试性能
        start_time = time.time()
        action = bot.get_action(observation, env)
        end_time = time.time()
        
        print(f"思考时间: {end_time - start_time:.3f}秒")
        print(f"评估节点数: {bot.nodes_evaluated}")
        print(f"选择的动作: {action}")
        print()

if __name__ == "__main__":
    test_minimax_performance() 