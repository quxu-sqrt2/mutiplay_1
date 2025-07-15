import random
from agents.base_agent import BaseAgent
 
class RandomBot(BaseAgent):
    def get_action(self, observation, env):
        # 针对PingPong游戏，挡板自动向球靠近
        if hasattr(env, 'game') and hasattr(env.game, 'get_state'):
            state = env.game.get_state()
            # 判断自己是左挡板还是右挡板
            if self.player_id == 1:
                # 左挡板，球在左半场时主动移动
                if state['ball_pos'][0] < 0.5:
                    if state['ball_pos'][1] > state['left_paddle'] + 0.02:
                        move = 1
                    elif state['ball_pos'][1] < state['left_paddle'] - 0.02:
                        move = -1
                    else:
                        move = 0
                    action = {"move_left": move, "move_right": 0, "left_force": False, "right_force": False, "plus": False, "minus": False}
                    return action
            elif self.player_id == 2:
                # 右挡板，球在右半场时主动移动
                if state['ball_pos'][0] > 0.5:
                    if state['ball_pos'][1] > state['right_paddle'] + 0.02:
                        move = 1
                    elif state['ball_pos'][1] < state['right_paddle'] - 0.02:
                        move = -1
                    else:
                        move = 0
                    action = {"move_left": 0, "move_right": move, "left_force": False, "right_force": False, "plus": False, "minus": False}
                    return action
        # 其它情况随机
        valid_actions = env.get_valid_actions()
        return random.choice(valid_actions) 