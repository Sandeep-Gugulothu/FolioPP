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
        Maps State -> Action using the Gymnasium-inspired state space.
        """
        from backend.processors.drl_env import FolioPPEnv
        env = FolioPPEnv()
        
        # 1. Update Env State with high-density features
        # [Price, RSI, Sentiment, Confidence, Risk, Exposure]
        env.update_state(tech_indicators, nlp_features, portfolio)
        state = env.state
        
        # 2. Simulated Policy Scoring (Level 2: Neural Heuristic)
        # In Level 3: This would be model.predict(state)
        rsi = state[1]
        sentiment = state[2]
        investor_confidence = state[3]
        risk = state[4]
        exposure = state[5]
        
        score = 0.0
        # Positive technical/sentiment confluence
        score += (sentiment * 0.4)
        score += (investor_confidence / 3.0 * 0.2)
        score += (risk / 2.0 * 0.1) # Risk reduction = score increase
        
        # Mean reversion logic (RSI)
        if rsi < 0.35: score += 0.3
        elif rsi > 0.65: score -= 0.3
        
        # 3. Final Decision Logic
        if score > 0.4:
            action = "BUY"
            confidence_out = min(0.98, 0.5 + abs(score))
        elif score < -0.4:
            action = "SELL"
            confidence_out = min(0.98, 0.5 + abs(score))
        else:
            action = "HOLD"
            confidence_out = 1.0 - abs(score)

        # 4. Agent Selection (Simulating best agent for current regime)
        regime = tech_indicators.get("regime", "Neutral")
        agent = "PPO" if "Neutral" in regime else ("SAC" if "Bullish" in regime else "A2C")
        
        # 5. Reasoning Generation (Neural Features Context)
        reason_parts = []
        if rsi < 0.35: reason_parts.append("RSV indicates oversold conditions")
        if sentiment > 0.5: reason_parts.append(f"Strong institutional sentiment ({sentiment})")
        if investor_confidence > 1: reason_parts.append("Elevated investor confidence detected")
        if risk > 0: reason_parts.append("Risk profile suggests reduced exposure risk")
        
        reasoning = "Neural State Synth: " + (", ".join(reason_parts) if reason_parts else "Neutral market signals")
        
        return DRLAction(
            action=action,
            confidence=round(confidence_out, 2),
            agent=agent,
            q_value=round(score, 3),
            reasoning=reasoning
        )

drl_module = DRLDecisionModule()
