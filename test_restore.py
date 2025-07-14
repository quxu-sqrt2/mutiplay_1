#!/usr/bin/env python3
"""
测试还原是否成功
"""

print("=== 测试还原结果 ===")

try:
    # 测试导入
    from games.snake import SnakeGame, SnakeEnv
    from agents import HumanAgent, SnakeAI
    print("✅ 导入测试通过")
    
    # 测试环境创建
    env = SnakeEnv(board_size=10)
    state = env.reset()
    print("✅ 环境创建测试通过")
    
    # 测试智能体创建
    human = HumanAgent(name="Human", player_id=1)
    ai = SnakeAI(name="AI", player_id=2)
    print("✅ 智能体创建测试通过")
    
    print("\n🎉 所有测试通过！文件已成功还原。")
    print("现在可以尝试运行: python snake_gui.py")
    
except Exception as e:
    print(f"❌ 测试失败: {e}")
    import traceback
    traceback.print_exc() 