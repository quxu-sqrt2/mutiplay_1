import numpy as np
from games.base_env import BaseEnv
from games.pingpong.pingpong_game import PingPongGame

class PingPongEnv(BaseEnv):
    def __init__(self, **kwargs):
        self.game = PingPongGame(**kwargs)
        super().__init__(self.game)

    def _setup_spaces(self):
        self.observation_space = np.zeros(10, dtype=np.float32)
        self.action_space = np.zeros(4, dtype=np.float32)

    def _get_observation(self):
        state = self.game.get_state()
        obs = [
            state['score_left'],
            state['score_right'],
            state['ball_pos'][0],
            state['ball_pos'][1],
            state['ball_vx'],
            state['ball_vy'],
            state['left_paddle_x'],
            state['left_paddle_y'],
            state['right_paddle_x'],
            state['right_paddle_y'],
        ]
        return np.array(obs, dtype=np.float32)

    def _get_action_mask(self):
        return np.ones(1, dtype=bool)

    def is_terminal(self):
        return self.game.is_terminal()

    def get_winner(self):
        return self.game.get_winner() 