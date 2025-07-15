from agents.base_agent import BaseAgent
import random

class RandomPingPongAI(BaseAgent):
    def get_action(self, observation, env):
        return {
            "move_left_x": random.choice([-1, 0, 1]),
            "move_left_y": random.choice([-1, 0, 1]),
            "move_right_x": random.choice([-1, 0, 1]),
            "move_right_y": random.choice([-1, 0, 1]),
        } 