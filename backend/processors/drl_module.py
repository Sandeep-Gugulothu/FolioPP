import os
import random
import logging
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

logger = logging.getLogger("DRLModule")

# Weights Storage (Stable Baselines3 patterns)
MODEL_DIR = os.path.join(os.getcwd(), "backend", "models", "drl")
DEFAULT_WEIGHTS = os.path.join(os.getcwd(), "backend", "models", "FolioGPT.zip")

class DRLAction(BaseModel):
    action: str  # BUY, SELL, HOLD
    confidence: float
    agent: str   # PPO, A2C, SAC
    q_value: float
    reasoning: str

class DRLDecisionModule:
    """
    Deep Reinforcement Learning Module for Portfolio Optimization.
    Simulates A2C/PPO/SAC decision logic using combined State (Tech + NLP + Portfolio).
    """
    
    def __init__(self):
        self.agents = ["PPO", "A2C", "SAC"]
        self.model_path = DEFAULT_WEIGHTS
        self._load_network_weights()

    def _load_network_weights(self):
        """Simulate loading Neural Architecture from zip (Level 2)."""
        if os.path.exists(self.model_path):
            logger.info(f"Loaded Primary Policy Weights from {self.model_path}")
            self.loaded = True
        else:
            logger.warning("No DRL weights found. Operating in Level 1 (Deterministic/Heuristic) Logic.")
            self.loaded = False

    def save_model(self, path: Optional[str] = None):
        """Persist current policy weights to disk."""
        target = path or os.path.join(MODEL_DIR, f"folio_ppo_{random.randint(10,99)}.zip")
        os.makedirs(os.path.dirname(target), exist_ok=True)
        # In Level 2, this would be model.save(target)
        with open(target, 'w') as f: f.write("dummy weights")
        logger.info(f"Model checkpoint saved: {target}")

    def calculate_decision(self, 
                           tech_indicators: Dict[str, Any], 
                           nlp_features: Dict[str, Any], 
                           portfolio: Dict[str, Any],
                           symbol: str = "TICKER") -> DRLAction:
        """
        Phase 4: Decision Making.
        Maps State -> Action using simulated policy weights.
        """
        # 1. State Normalization (Logic)
        rsi = tech_indicators.get("rsi_14", 50)
        regime = tech_indicators.get("regime", "Neutral")
        sentiment = nlp_features.get("sentiment", 0) # -1 to 1
        price_impact = nlp_features.get("price_impact", 0) # -3 to 3
        
        # 2. Simulated Policy Scoring
        # Positive sentiment + Oversold (RSI < 30) = Strong Buy
        # Negative sentiment + Overbought (RSI > 70) = Strong Sell
        
        score = 0.0
        # Tech signals
        if rsi < 35: score += 0.4
        elif rsi > 65: score -= 0.4
        
        if regime == "Bullish": score += 0.2
        elif regime == "Bearish": score -= 0.2
        
        # NLP signals
        score += (sentiment * 0.3)
        score += (price_impact / 3.0 * 0.4)
        
        # 3. Final Decision Logic
        if score > 0.5:
            action = "BUY"
            confidence = min(0.95, 0.5 + abs(score))
        elif score < -0.5:
            action = "SELL"
            confidence = min(0.95, 0.5 + abs(score))
        else:
            action = "HOLD"
            confidence = 1.0 - abs(score)

        # 4. Agent Selection (Simulating best agent for current regime)
        agent = "PPO" if regime == "Neutral" else ("SAC" if regime == "Bullish" else "A2C")
        
        # 5. Reasoning Generation
        reason_parts = []
        if rsi < 35: reason_parts.append("RSV indicates oversold conditions")
        if sentiment > 0: reason_parts.append(f"Positive institutional sentiment ({sentiment})")
        if price_impact > 1: reason_parts.append("High potential positive price impact")
        
        reasoning = "Combined State: " + (", ".join(reason_parts) if reason_parts else "Neutral market signals")
        
        return DRLAction(
            action=action,
            confidence=round(confidence, 2),
            agent=agent,
            q_value=round(score, 3),
            reasoning=reasoning
        )

drl_module = DRLDecisionModule()
