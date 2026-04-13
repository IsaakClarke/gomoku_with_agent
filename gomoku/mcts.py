from __future__ import annotations

import math
import numpy as np
import torch

from gomoku.config import ACTION_SIZE
from gomoku.game import Game
from gomoku.model import PolicyValueNet


class MCTSNode:
    def __init__(self, game: Game, parent: "MCTSNode | None" = None, parent_action: int | None = None, prior: float = 1.0):
        self.game = game
        self.parent = parent
        self.parent_action = parent_action
        self.prior = float(prior)

        self.visit_count = 0
        self.value_sum = 0.0

        self.children: dict[int, MCTSNode] = {}

        self.is_expanded = False
        self.is_terminal = game.is_terminal()

    @property
    def value(self) -> float:
        if self.visit_count == 0:
            return 0.0
        return self.value_sum / self.visit_count


class MCTS:
    def __init__(
        self,
        model: PolicyValueNet,
        device: str = "cpu",
        simulations: int = 100,
        cpuct: float = 1.5,
        radius: int = 2,
    ):
        self.model = model
        self.device = device
        self.simulations = simulations
        self.cpuct = cpuct
        self.radius = radius

    def run(self, game: Game) -> tuple[MCTSNode, np.ndarray]:
        root = MCTSNode(game=game.copy())

        if root.is_terminal:
            policy = np.zeros(ACTION_SIZE, dtype=np.float32)
            return root, policy

        for _ in range(self.simulations):
            self._run_one_simulation(root)

        visit_counts = np.zeros(ACTION_SIZE, dtype=np.float32)

        for action, child in root.children.items():
            visit_counts[action] = child.visit_count

        total_visits = visit_counts.sum()

        if total_visits <= 0:
            legal_actions = game.get_candidate_actions(radius=self.radius)
            if len(legal_actions) > 0:
                visit_counts[legal_actions] = 1.0 / len(legal_actions)
            return root, visit_counts

        policy = visit_counts / total_visits
        return root, policy

    def _run_one_simulation(self, root: MCTSNode) -> None:
        node = root
        search_path = [node]

        # selection
        while node.is_expanded and not node.is_terminal:
            action, child = self._select_child(node)
            if child is None:
                break
            node = child
            search_path.append(node)

        # expansion / evaluation
        value = self._expand_and_evaluate(node)

        # backprop
        self._backpropagate(search_path, value)

    def _select_child(self, node: MCTSNode) -> tuple[int | None, MCTSNode | None]:
        best_score = -1e18
        best_action = None
        best_child = None

        parent_visits = max(1, node.visit_count)

        for action, child in node.children.items():
            q_value = -child.value
            u_value = self.cpuct * child.prior * math.sqrt(parent_visits) / (1 + child.visit_count)
            score = q_value + u_value

            if score > best_score:
                best_score = score
                best_action = action
                best_child = child

        return best_action, best_child

    def _expand_and_evaluate(self, node: MCTSNode) -> float:
        game = node.game

        if node.is_terminal:
            return self._get_terminal_value(game)

        legal_actions = game.get_candidate_actions(radius=self.radius)

        policy_logits, value = self._predict(game)
        policy_probs = self._masked_softmax(policy_logits, legal_actions)

        for action in legal_actions:
            child_game = game.copy()
            success = child_game.play_action(action)
            if not success:
                continue

            child_node = MCTSNode(
                game=child_game,
                parent=node,
                parent_action=action,
                prior=float(policy_probs[action]),
            )
            node.children[action] = child_node

        node.is_expanded = True
        return value

    def _backpropagate(self, search_path: list[MCTSNode], value: float) -> None:
        for node in reversed(search_path):
            node.visit_count += 1
            node.value_sum += value
            value = -value

    def _predict(self, game: Game) -> tuple[np.ndarray, float]:
        x = game.encode()
        x = torch.tensor(x, dtype=torch.float32).unsqueeze(0).to(self.device)

        with torch.no_grad():
            policy_logits, value = self.model(x)

        policy_logits = policy_logits[0].detach().cpu().numpy()
        value = float(value.item())

        return policy_logits, value

    def _masked_softmax(self, logits: np.ndarray, legal_actions: list[int]) -> np.ndarray:
        probs = np.zeros(ACTION_SIZE, dtype=np.float32)

        if len(legal_actions) == 0:
            return probs

        legal_logits = logits[legal_actions]
        legal_logits = legal_logits - np.max(legal_logits)

        exp_values = np.exp(legal_logits)
        total = np.sum(exp_values)

        if total <= 0 or not np.isfinite(total):
            probs[legal_actions] = 1.0 / len(legal_actions)
            return probs

        probs[legal_actions] = exp_values / total
        return probs

    def _get_terminal_value(self, game: Game) -> float:
        if game.winner == 0:
            return 0.0

        if game.winner == game.current_player:
            return 1.0
        return -1.0


def select_action_from_policy(policy: np.ndarray, use_temperature: bool = False) -> int | None:
    nonzero_actions = np.where(policy > 0)[0]

    if len(nonzero_actions) == 0:
        return None

    if use_temperature:
        probs = policy[nonzero_actions]
        probs = probs / probs.sum()
        action = np.random.choice(nonzero_actions, p=probs)
        return int(action)

    return int(np.argmax(policy))