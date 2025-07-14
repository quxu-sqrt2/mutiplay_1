#!/usr/bin/env python3
"""
测试贪吃蛇游戏的玩家切换功能
"""

def test_snake_turn_switching():
    """测试贪吃蛇游戏的玩家切换"""
    try:
        from games.snake.snake_game import SnakeGame
        
        print("=== 贪吃蛇玩家切换测试 ===\n")
        
        # 创建游戏
        game = SnakeGame(board_size=10)
        game.reset()
        
        print(f"初始玩家: {game.current_player}")
        
        # 测试几个回合
        for i in range(5):
            print(f"\n--- 回合 {i+1} ---")
            print(f"当前玩家: {game.current_player}")
            
            # 获取有效动作
            valid_actions = game.get_valid_actions()
            print(f"有效动作: {valid_actions}")
            
            # 选择一个动作
            action = valid_actions[0]
            print(f"选择动作: {action}")
            
            # 执行动作
            observation, reward, done, info = game.step(action)
            
            print(f"执行后玩家: {game.current_player}")
            print(f"蛇1长度: {len(game.snake1)}, 蛇2长度: {len(game.snake2)}")
            print(f"蛇1存活: {game.alive1}, 蛇2存活: {game.alive2}")
            print(f"游戏结束: {done}")
            
            if done:
                print("游戏结束！")
                break
        
        print("\n✅ 玩家切换测试完成！")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_snake_turn_switching() 