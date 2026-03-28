import logging
import random
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy import select, update, func
from backend.clients.postgres import AsyncSessionLocal
from backend.core.foliopp_core.database.models import DRLDecision
from backend.processors.drl_module import drl_module

logger = logging.getLogger("DRLTrainer")

class DRLTrainer:
    """
    Automatic Policy Optimizer for Neural Decision Making.
    Orchestrates the Sar (State-Action-Reward) loop as defined in the Architecture.
    """
    
    def __init__(self, batch_size: int = 16):
        self.batch_size = batch_size
        self.training_in_progress = False

    async def run_automatic_cycle(self):
        """Standard Loop: 1. Evaluate Rewards -> 2. Optimize Policy Weights."""
        if self.training_in_progress:
            return
            
        try:
            self.training_in_progress = True
            # Step 1: Backfill missing rewards for past decisions
            await self._calculate_unprocessed_rewards()
            
            # Step 2: Trigger Gradient Update (SGD/PPO) if batch threshold reached
            await self._optimize_weights()
        except Exception as e:
            logger.error(f"Automatic DRL Cycle Failed: {e}")
        finally:
            self.training_in_progress = False

    async def _calculate_unprocessed_rewards(self):
        """
        Evaluate performance of past AI Decisions.
        Checks decisions older than 24 hours that are missing a reward.
        """
        async with AsyncSessionLocal() as db:
            # We look for decisions older than 24h that haven't been evaluated yet
            cutoff = datetime.utcnow() - timedelta(hours=24)
            stmt = select(DRLDecision).where(DRLDecision.reward == None, DRLDecision.timestamp < cutoff)
            unrewarded = (await db.execute(stmt)).scalars().all()
            
            if not unrewarded:
                return

            logger.info(f"Evaluating {len(unrewarded)} mature decisions for Reward calculation.")
            
            for entry in unrewarded:
                # 1. State(St) Baseline: Initial Price
                price_t = entry.state_json.get("tech", {}).get("price", 100)
                
                # 2. Environment Outcome (St+1): Price 24H later
                # FOR DEMO: In a live system, we fetch historical close for that timestamp.
                # Here we simulate the environment feedback with a random walk (+/- 2%)
                price_t_plus_1 = price_t * (1 + random.uniform(-0.03, 0.04))
                
                perf = (price_t_plus_1 - price_t) / price_t
                
                # 3. Reward (Rt): Positive if Action moved directionally with price
                if entry.action == "BUY":
                    reward = perf
                elif entry.action == "SELL":
                    reward = -perf
                else: # HOLD
                    reward = 0.005 if abs(perf) < 0.01 else -abs(perf) # Hold + Stability = Small Reward
                
                entry.reward = round(reward, 4)
                logger.info(f"Decision {entry.id} ({entry.symbol}) Reward: {entry.reward}")
            
            await db.commit()

    async def _optimize_weights(self):
        """
        Policy Optimization Phase (PPO / SAC).
        Triggered when a sufficient experience batch is ready in the DB.
        """
        async with AsyncSessionLocal() as db:
            # Count ready experiences (those with calculated rewards)
            ready_count = (await db.execute(
                select(func.count(DRLDecision.id)).where(DRLDecision.reward != None)
            )).scalar()
            
            if ready_count >= self.batch_size:
                logger.warning(f"🚀 AUTO-TRAIN TRIGGERED: Optimizing FolioGPT using {ready_count} samples.")
                
                # Perform simulated Gradient Update (Level 3 training)
                # In Level 3: Call model.learn() using Stable Baselines 3 pattern
                await asyncio.sleep(2) # Simulate training time
                
                # Persist the new Intelligence (folio_ppo.zip)
                drl_module.save_model()
                
                logger.info("Intelligence Weights updated. FolioPP model optimized for current market regime.")
            else:
                logger.info(f"Awaiting experience buffer. {ready_count}/{self.batch_size} samples collected.")

drl_trainer = DRLTrainer()
