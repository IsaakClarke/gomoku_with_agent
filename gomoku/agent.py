from __future__ import annotations

import random
from dataclasses import dataclass

from gomoku.config import AI_CONFIGS, AIConfig
from gomoku.game import Game, action_to_row_col
from gomoku.model import load_model, PolicyValueNet
from gomoku.tactics import (
    find_immediate_win,
    find_immediate_block,
    find_open_four_move,
    find_block_open_four_move,
)
from gomoku.mcts import MCTS, select_action_from_policy


@dataclass
class MoveDecision:
    action: int
    source: str


class AIPlayer:
    def __init__(self, checkpoint_path: str, difficulty: str = "medium", device: str = "cpu"):
        if difficulty not in AI_CONFIGS:
            raise ValueError(f"Unknown difficulty: {difficulty}")

        self.device = device
        self.checkpoint_path = checkpoint_path
        self.model: PolicyValueNet = load_model(checkpoint_path, device=device)

        self.set_difficulty(difficulty)

    def set_difficulty(self, difficulty: str) -> None:
        if difficulty not in AI_CONFIGS:
            raise ValueError(f"Unknown difficulty: {difficulty}")

        self.config: AIConfig = AI_CONFIGS[difficulty]

        self.mcts = MCTS(
            model=self.model,
            device=self.device,
            simulations=self.config.simulations,
            cpuct=self.config.cpuct,
            radius=2,
        )

    def choose_move(self, game: Game) -> MoveDecision | None:
        if game.is_terminal():
            return None

        if self.config.use_tactics:
            decision = self._try_tactical_move(game)
            if decision is not None:
                return decision

        root, policy = self.mcts.run(game)

        action = select_action_from_policy(
            policy=policy,
            use_temperature=self.config.use_temperature,
        )

        if action is None:
            legal_actions = game.get_candidate_actions(radius=2)
            if len(legal_actions) == 0:
                return None
            action = random.choice(legal_actions)

        return MoveDecision(action=action, source="mcts")

    def _try_tactical_move(self, game: Game) -> MoveDecision | None:
        player = game.current_player

        win_action = find_immediate_win(game, player, radius=2)
        if win_action is not None:
            return MoveDecision(action=win_action, source="win_in_1")

        block_action = find_immediate_block(game, player, radius=2)
        if block_action is not None:
            return MoveDecision(action=block_action, source="block_in_1")

        open_four_action = find_open_four_move(game, player, radius=2)
        if open_four_action is not None:
            return MoveDecision(action=open_four_action, source="create_open_four")

        block_open_four_action = find_block_open_four_move(game, player, radius=2)
        if block_open_four_action is not None:
            return MoveDecision(action=block_open_four_action, source="block_open_four")

        return None