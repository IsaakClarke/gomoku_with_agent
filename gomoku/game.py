from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Tuple
import numpy as np

from gomoku.config import BOARD_SIZE, ACTION_SIZE, EMPTY, BLACK, WHITE


Move = Tuple[int, int, int]  # (row, col, player)


def action_to_row_col(action: int) -> Tuple[int, int]:
    row = action // BOARD_SIZE
    col = action % BOARD_SIZE
    return row, col


def row_col_to_action(row: int, col: int) -> int:
    return row * BOARD_SIZE + col


def is_inside(row: int, col: int) -> bool:
    return 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE


def create_board() -> np.ndarray:
    return np.zeros((BOARD_SIZE, BOARD_SIZE), dtype=np.int8)


@dataclass
class Game:
    board: np.ndarray = field(default_factory=create_board)
    current_player: int = BLACK
    last_move: Optional[Tuple[int, int]] = None
    move_count: int = 0
    winner: int = EMPTY

    move_history: List[Move] = field(default_factory=list)
    redo_stack: List[Move] = field(default_factory=list)

    black_undos_used: int = 0
    white_undos_used: int = 0

    def reset(self) -> None:
        self.board = create_board()
        self.current_player = BLACK
        self.last_move = None
        self.move_count = 0
        self.winner = EMPTY
        self.move_history.clear()
        self.redo_stack.clear()
        self.black_undos_used = 0
        self.white_undos_used = 0

    def copy(self) -> "Game":
        copied = Game()
        copied.board = self.board.copy()
        copied.current_player = self.current_player
        copied.last_move = self.last_move
        copied.move_count = self.move_count
        copied.winner = self.winner
        copied.move_history = self.move_history.copy()
        copied.redo_stack = self.redo_stack.copy()
        copied.black_undos_used = self.black_undos_used
        copied.white_undos_used = self.white_undos_used
        return copied

    def is_terminal(self) -> bool:
        return self.winner != EMPTY or self.move_count >= ACTION_SIZE

    def is_draw(self) -> bool:
        return self.winner == EMPTY and self.move_count >= ACTION_SIZE

    def is_legal_move(self, row: int, col: int) -> bool:
        if not is_inside(row, col):
            return False
        if self.board[row, col] != EMPTY:
            return False
        if self.is_terminal():
            return False
        return True

    def play_move(self, row: int, col: int) -> bool:
        if not self.is_legal_move(row, col):
            return False

        player = self.current_player
        self.board[row, col] = player

        self.last_move = (row, col)
        self.move_count += 1
        self.move_history.append((row, col, player))

        self.redo_stack.clear()

        self.winner = self._check_winner_from_last_move()

        self.current_player *= -1
        return True

    def play_action(self, action: int) -> bool:
        row, col = action_to_row_col(action)
        return self.play_move(row, col)

    def can_undo(self, player: int, max_undos: int) -> bool:
        if len(self.move_history) == 0:
            return False

        if player == BLACK:
            return self.black_undos_used < max_undos
        else:
            return self.white_undos_used < max_undos

    def undo(self, max_undos: int) -> bool:
        """
        Undo last move.
        Считаем попытку undo за игроком, который сейчас должен ходить,
        потому что именно он просит откатить позицию.
        """
        if len(self.move_history) == 0:
            return False

        requester = self.current_player

        if not self.can_undo(requester, max_undos):
            return False

        row, col, player = self.move_history.pop()
        self.board[row, col] = EMPTY
        self.redo_stack.append((row, col, player))

        self.move_count -= 1
        self.current_player = player
        self.winner = EMPTY

        if len(self.move_history) > 0:
            last_row, last_col, _ = self.move_history[-1]
            self.last_move = (last_row, last_col)
            self.winner = self._recompute_winner()
        else:
            self.last_move = None

        if requester == BLACK:
            self.black_undos_used += 1
        else:
            self.white_undos_used += 1

        return True

    def can_redo(self) -> bool:
        return len(self.redo_stack) > 0 and not self.is_terminal()

    def redo(self) -> bool:
        if not self.can_redo():
            return False

        row, col, player = self.redo_stack.pop()

        if self.board[row, col] != EMPTY:
            return False

        self.board[row, col] = player
        self.move_history.append((row, col, player))
        self.last_move = (row, col)
        self.move_count += 1

        self.winner = self._check_winner_from_last_move()
        self.current_player = -player

        return True

    def get_all_legal_actions(self) -> List[int]:
        actions = []
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                if self.board[row, col] == EMPTY:
                    actions.append(row_col_to_action(row, col))
        return actions

    def get_candidate_actions(self, radius: int = 2) -> List[int]:
        if self.move_count == 0:
            center = BOARD_SIZE // 2
            actions = []
            for row in range(center - 1, center + 2):
                for col in range(center - 1, center + 2):
                    actions.append(row_col_to_action(row, col))
            return actions

        candidates = set()
        occupied_positions = np.argwhere(self.board != EMPTY)

        for base_row, base_col in occupied_positions:
            for dr in range(-radius, radius + 1):
                for dc in range(-radius, radius + 1):
                    row = base_row + dr
                    col = base_col + dc

                    if is_inside(row, col) and self.board[row, col] == EMPTY:
                        candidates.add(row_col_to_action(row, col))

        if len(candidates) == 0:
            return self.get_all_legal_actions()

        return list(candidates)

    def encode(self) -> np.ndarray:
        """
        Relative encoding from current player perspective:
        channel 0: current player's stones
        channel 1: opponent stones
        channel 2: last move
        channel 3: ones plane
        """
        x = np.zeros((4, BOARD_SIZE, BOARD_SIZE), dtype=np.float32)

        x[0] = (self.board == self.current_player).astype(np.float32)
        x[1] = (self.board == -self.current_player).astype(np.float32)

        if self.last_move is not None:
            row, col = self.last_move
            x[2, row, col] = 1.0

        x[3].fill(1.0)

        return x

    def _count_one_direction(self, row: int, col: int, dr: int, dc: int, player: int) -> int:
        count = 0
        r = row + dr
        c = col + dc

        while is_inside(r, c) and self.board[r, c] == player:
            count += 1
            r += dr
            c += dc

        return count

    def _check_winner_from_last_move(self) -> int:
        if self.last_move is None:
            return EMPTY

        row, col = self.last_move
        player = self.board[row, col]

        if player == EMPTY:
            return EMPTY

        directions = [
            (1, 0),
            (0, 1),
            (1, 1),
            (1, -1),
        ]

        for dr, dc in directions:
            total = 1
            total += self._count_one_direction(row, col, dr, dc, player)
            total += self._count_one_direction(row, col, -dr, -dc, player)

            if total >= 5:
                return player

        return EMPTY

    def _recompute_winner(self) -> int:
        """
        Полный пересчет победителя после undo.
        """
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                player = self.board[row, col]
                if player == EMPTY:
                    continue

                directions = [
                    (1, 0),
                    (0, 1),
                    (1, 1),
                    (1, -1),
                ]

                for dr, dc in directions:
                    total = 1
                    total += self._count_one_direction(row, col, dr, dc, player)
                    total += self._count_one_direction(row, col, -dr, -dc, player)

                    if total >= 5:
                        return player

        return EMPTY