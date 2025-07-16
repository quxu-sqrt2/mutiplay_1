import random
from agents.base_agent import BaseAgent
 
class RandomBot(BaseAgent):
    def get_action(self, observation, env):
        valid_actions = env.get_valid_actions()
        return random.choice(valid_actions) 