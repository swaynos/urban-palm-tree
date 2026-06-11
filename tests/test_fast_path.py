import unittest
from unittest.mock import MagicMock, patch
import asyncio
from controllers.game_strategy_controller import GameStrategyController
from controllers.game_flow_controller import GameFlowController
from game_state.game_state import GameState

class TestFastPath(unittest.IsolatedAsyncioTestCase):
    async def test_chase_ball_logic(self):
        # 1. Setup Strategy Controller
        strategy = GameStrategyController()
        
        # Mock GameState to be IN_MATCH
        strategy.game_state_tracker.current_game_state = GameState.IN_MATCH
        
        # 2. Simulate Detections (Ball on Left)
        # Screen width 1280. Center 640. Tolerance 128 (10%).
        # Ball at 100 (Left)
        detections = [{
            "class_name": "ball",
            "points": {
                "x": 100,
                "width": 20,
                "height": 20
            }
        }]
        
        print(f"Simulating detections: {detections}")
        await strategy.update_strategy(detections, 1280)
        
        # 3. Verify Intent
        intent = strategy.get_strategic_intent()
        print(f"Detected Intent: {intent}")
        self.assertEqual(intent, "FAST_MOVE_LEFT")
        
        # 4. Setup Flow Controller with Mock IO
        with patch('controllers.game_flow_controller.PlaystationIO') as MockIO:
            flow = GameFlowController()
            
            # 5. Build Actions
            actions = await flow.build_actions_from_strategy(strategy)
            
            # 6. Verify Actions
            self.assertTrue(len(actions) > 0)
            print(f"Actions generated: {len(actions)}")
            
            # We expect 2 actions: Move Left + Sprint
            self.assertEqual(len(actions), 2)

if __name__ == '__main__':
    unittest.main()
