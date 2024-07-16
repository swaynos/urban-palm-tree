import gym
from gym import spaces
import numpy as np

class EAFC24Env(gym.Env):
    def __init__(self):
        super(EAFC24Env, self).__init__()
        
        # Define action and observation space
        self.action_space = spaces.Discrete(5)
        
        # Observations: 0 = In-Match, 1 = In-Menu, 2 = In-Squad-Selection
        self.observation_space = spaces.Discrete(3)
        
        # Initial state
        self.state = self._get_initial_state()
        
        # Episode length
        self.max_steps = 100
        self.current_step = 0

        # Random seed
        self.seed()

    def _get_initial_state(self):
        return np.random.choice([0, 1, 2])
    
    def step(self, action):
        self.current_step += 1
        
        if self.state == 0:  # In-Match
            if action == 0:  # Cross button to progress
                self.state = 1  # Move to In-Menu
                reward = 1  # Successful match end
            else:
                reward = -1  # Invalid action
        
        elif self.state == 1:  # In-Menu
            if action == 0:  # Cross button to queue match
                self.state = 0  # Back to In-Match
                reward = 1  # Successful queue
            else:
                reward = 0  # Neutral action
        
        elif self.state == 2:  # In-Squad-Selection
            if action in [1, 2, 3, 4]:  # D-pad directional inputs
                self.state = 1  # Move to In-Menu
                reward = 0  # Neutral, correct sub-action
            else:
                reward = -1  # Invalid action
        
        terminated = self.current_step >= self.max_steps
        truncated = False  # You can add logic to determine if the episode was truncated
        
        return self.state, reward, terminated, truncated, {}
    
    def reset(self, seed=None, options=None):
        if seed is not None:
            self.seed(seed)
        self.state = self._get_initial_state()
        self.current_step = 0
        return self.state, {}

    def seed(self, seed=None):
        self.np_random, seed = gym.utils.seeding.np_random(seed)
        return [seed]
    
    def render(self, mode='human'):
        pass
