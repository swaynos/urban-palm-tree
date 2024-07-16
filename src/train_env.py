import os
from stable_baselines3 import PPO
from stable_baselines3.common.env_util import make_vec_env
from fc24_env import EAFC24Env  # Ensure the class is imported correctly

# Create the vectorized environment
env = make_vec_env(EAFC24Env, n_envs=4)

# Define the model
model = PPO('MlpPolicy', env, verbose=1)

# Train the model
model.learn(total_timesteps=10000)

# Save the model
model.save("ppo_eafc24")

# Load the model (for inference)
model = PPO.load("ppo_eafc24")

# Test the trained agent
obs = env.reset()
for i in range(1000):
    action, _states = model.predict(obs)
    obs, rewards, dones, info = env.step(action)
    env.render()
