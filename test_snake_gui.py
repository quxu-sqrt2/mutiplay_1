#!/usr/bin/env python3
"""
测试贪吃蛇GUI启动
"""

def test_snake_gui_startup():
    """测试贪吃蛇GUI启动"""
    try:
        from snake_gui import SnakeGUI
        
        print("=== 贪吃蛇GUI启动测试 ===\n")
        
        # 创建GUI实例
        gui = SnakeGUI()
        print("✅ GUI实例创建成功")
        
        # 测试游戏重置
        gui.reset_game()
        print("✅ 游戏重置成功")
        
        # 测试AI代理创建
        gui._create_ai_agent()
        print("✅ AI代理创建成功")
        
        print("\n🎉 贪吃蛇GUI启动测试通过！")
        print("现在可以运行: python snake_gui.py")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_snake_gui_startup() 