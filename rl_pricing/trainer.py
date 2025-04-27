import os
import numpy as np
from stable_baselines3 import DQN, PPO
from stable_baselines3.common.callbacks import BaseCallback
from stable_baselines3.common.monitor import Monitor
from rl_pricing.environment import ProductPricingEnv
from products.models import Product

class TrainLoggerCallback(BaseCallback):
    def __init__(self, verbose=0):
        super(TrainLoggerCallback, self).__init__(verbose)
        self.rewards = []
    
    def _on_step(self) -> bool:
        reward = self.locals.get('rewards', [0])[0]
        self.rewards.append(reward)
        
        if self.num_timesteps % 1000 == 0:
            avg_reward = np.mean(self.rewards[-100:])
            print(f"Timestep: {self.num_timesteps}, Avg Reward: {avg_reward:.2f}")
        return True

class PricingModelTrainer:
    def __init__(self, product_id, algorithm='DQN'):
        self.product_id = product_id
        self.algorithm = algorithm
        self.model = None
        self.env = None
        self.model_path = f"rl_pricing/models/product_{product_id}"
        self.model_zip_path = f"{self.model_path}.zip"
        
        os.makedirs("rl_pricing/models", exist_ok=True)
    
    def create_env(self):
        env = ProductPricingEnv(self.product_id)
        env = Monitor(env)
        return env
    
    def model_exists(self):
        return os.path.exists(self.model_zip_path)
    
    def initialize_model(self):
        self.env = self.create_env()
        
        if self.algorithm == 'DQN':
            model = DQN('MlpPolicy', self.env, verbose=0,
                        learning_rate=1e-3,
                        buffer_size=10000,
                        learning_starts=1000,
                        batch_size=32)
        elif self.algorithm == 'PPO':
            model = PPO('MlpPolicy', self.env, verbose=0,
                        learning_rate=3e-4,
                        n_steps=2048,
                        batch_size=64)
        
        return model
    
    def load_or_create_model(self):
        if self.model_exists():
            return self.load_model()
        else:
            print(f"No existing model for product {self.product_id}, creating new model...")
            model = self.initialize_model()
            model.save(self.model_path)
            return model
    
    def train(self, total_timesteps=10000):
        self.env = self.create_env()
        
        if self.algorithm == 'DQN':
            model = DQN('MlpPolicy', self.env, verbose=1,
                        learning_rate=1e-3,
                        buffer_size=10000,
                        learning_starts=1000,
                        batch_size=32,
                        tau=1.0,
                        gamma=0.99,
                        train_freq=4,
                        gradient_steps=1,
                        target_update_interval=1000)
        elif self.algorithm == 'PPO':
            model = PPO('MlpPolicy', self.env, verbose=1,
                        learning_rate=3e-4,
                        n_steps=2048,
                        batch_size=64,
                        n_epochs=10,
                        gamma=0.99,
                        gae_lambda=0.95,
                        clip_range=0.2,
                        ent_coef=0.0)
        
        callback = TrainLoggerCallback()
        model.learn(total_timesteps=total_timesteps, callback=callback)
        model.save(self.model_path)
        self.model = model
        return model
    
    def load_model(self):
        if self.algorithm == 'DQN':
            self.model = DQN.load(self.model_path)
        elif self.algorithm == 'PPO':
            self.model = PPO.load(self.model_path)
        
        self.env = self.create_env()
        self.model.set_env(self.env)
        return self.model
    
    def predict_price_change(self, current_state=None):
        if self.model is None:
            self.load_or_create_model()
        
        if current_state is None:
            current_state, _ = self.env.reset()
        
        action, _ = self.model.predict(current_state, deterministic=True)
        return action
