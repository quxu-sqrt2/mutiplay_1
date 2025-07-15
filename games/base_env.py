"""
环境基类
实现gym风格的游戏环境接口
"""

import time
from abc import ABC, abstractmethod
from typing import Dict, List, Tuple, Any, Optional
import numpy as np
import config
from games.base_game import BaseGame

class BaseEnv(ABC):
    """环境基类，实现gym风格接口"""
    
    def __init__(self, game: BaseGame):
        self.game = game
        self.observation_space = None
        self.action_space = None
        self._setup_spaces()
    
    @abstractmethod
    def _setup_spaces(self) -> None:
        """设置观察空间和动作空间"""
        pass
    
    @abstractmethod
    def _get_observation(self) -> np.ndarray:
        """获取观察"""
        pass
    
    @abstractmethod
    def _get_action_mask(self) -> np.ndarray:
        """获取动作掩码"""
        pass
    
    def reset(self) -> Tuple[np.ndarray, Dict[str, Any]]:
        """重置环境"""
        self.game.reset()
        observation = self._get_observation()
        info = self.game.get_game_info()
        return observation, info
    
    def step(self, action: Any) -> Tuple[np.ndarray, float, bool, bool, Dict[str, Any]]:
        """执行动作"""
        # 宽松动作校验
        def is_valid_action(a):
            if not isinstance(a, dict):
                return False
            for k, v in a.items():
                if k.startswith('move_') and v not in [-1, 0, 1]:
                    return False
                if k.endswith('_force') or k.endswith('_spin'):
                    if v not in [False, True]:
                        return False
            return True
        if not is_valid_action(action):
            return self._get_observation(), -1000, True, False, {'error': 'Invalid action'}
        # 执行动作
        observation, reward, done, info = self.game.step(action)
        # 更新游戏状态
        self.game.update_game_state()
        # 检查是否超时
        truncated = self.game.is_timeout()
        # 如果observation是字典，提取board
        if isinstance(observation, dict) and 'board' in observation:
            observation = observation['board']
        elif isinstance(observation, dict):
            # 如果没有board，使用_get_observation
            observation = self._get_observation()
        return observation, reward, done, truncated, info
    
    def render(self, mode='human') -> Optional[np.ndarray]:
        """渲染环境"""
        if mode == 'human':
            return self.game.render()
        elif mode == 'rgb_array':
            return self._get_observation()
        return None
    
    def close(self) -> None:
        """关闭环境"""
        pass
    
    def get_valid_actions(self) -> List[Any]:
        """获取有效动作"""
        return self.game.get_valid_actions(self.game.current_player)
    
    def get_action_mask(self) -> np.ndarray:
        """获取动作掩码"""
        return self._get_action_mask() 