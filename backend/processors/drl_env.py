import gymnasium as gym
import numpy as np
from gymnasium import spaces
from typing import Dict, Any

class FolioPPEnv(gym.Env):
    """
    Maps State(St) -> Action(At) -> Reward(Rt+1).
    
    State: [Price, RSI, Sentiment, InvestorConfidence, RiskProfile, PortfolioExposure]
    Action: 0 (Hold), 1 (Buy), 2 (Sell)
    """
    
    def __init__(self, metadata: Dict[str, Any] = None):
        super(FolioPPEnv, self).__init__()
        
        # Define Action Space: {0: Hold, 1: Buy, 2: Sell}
        self.action_space = spaces.Discrete(3)
        
        # Define Observation Space: 
        # [Price (norm), RSI (0-1), Sentiment (-1 to 1), Confidence (-3 to 3), Risk (-2 to 2), Exposure (0-1)]
        self.observation_space = spaces.Box(
            low=np.array([0, 0, -1, -3, -2, 0], dtype=np.float32),
            high=np.array([1, 1, 1, 3, 2, 1], dtype=np.float32),
            dtype=np.float32
        )
        
        self.state = np.zeros(6)
        self.metadata = metadata or {}

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.state = np.zeros(6)
        return self.state, {}

    def step(self, action):
        """
        Calculates the transition and reward for the intelligence loop.
        In the simulated environment, we use the probability of success.
        """
        # Simulate environment transition
        # action 1 (Buy) when sentiment is high and RSI is low = High Reward
        # action 2 (Sell) when sentiment is low and RSI is high = High Reward
        
        rsi = self.state[1]
        sentiment = self.state[2]
        
        reward = 0
        if action == 1: # BUY
            if sentiment > 0.5 and rsi < 0.4: reward = 1.0
            elif sentiment < 0 and rsi > 0.6: reward = -1.0
        elif action == 2: # SELL
            if sentiment < -0.5 and rsi > 0.6: reward = 1.0
            elif sentiment > 0 and rsi < 0.4: reward = -1.0
            
        # Terminal state - in our case, each decision is a step
        terminated = True
        truncated = False
        
        return self.state, reward, terminated, truncated, {}

    def update_state(self, tech_indicators: dict, nlp_features: dict, portfolio: dict):
        """Maps our high-density data context into the numerical State space."""
        # 1. RSI (0.0 to 1.0)
        rsi = float(tech_indicators.get("rsi_14", 50)) / 100.0
        
        # 2. Sentiment (-1.0 to 1.0)
        sentiment = float(nlp_features.get("sentiment", 0))
        
        # 3. Confidence (-3 to 3)
        confidence = float(nlp_features.get("investor_confidence", 0))
        
        # 4. Risk Profile (-2 to 2)
        risk = float(nlp_features.get("risk_profile", 0))
        
        # 5. Exposure (0.0 to 1.0)
        exposure = 1.0 if portfolio.get("is_held") else 0.0
        
        # 6. Price Baseline (mock normalization for the env)
        price_norm = 0.5 
        
        self.state = np.array([price_norm, rsi, sentiment, confidence, risk, exposure], dtype=np.float32)
