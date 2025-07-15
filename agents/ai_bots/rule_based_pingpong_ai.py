from agents.base_agent import BaseAgent

class RuleBasedPingPongAI(BaseAgent):
    def get_action(self, observation, env):
        state = env.game.get_state()
        action = {"move_left_x": 0, "move_left_y": 0, "move_right_x": 0, "move_right_y": 0}
        # 右挡板追球
        if state['ball_pos'][0] > state['right_paddle_x'] + 0.01:
            action["move_right_x"] = 1
        elif state['ball_pos'][0] < state['right_paddle_x'] - 0.01:
            action["move_right_x"] = -1
        if state['ball_pos'][1] > state['right_paddle_y'] + 0.01:
            action["move_right_y"] = 1
        elif state['ball_pos'][1] < state['right_paddle_y'] - 0.01:
            action["move_right_y"] = -1
        return action 