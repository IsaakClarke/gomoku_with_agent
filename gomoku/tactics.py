from __future__ import annotations

from typing import Optional

from gomoku.config import BOARD_SIZE, EMPTY
from gomoku.game import Game, action_to_row_col


def count_side(board, row: int, col: int, dr: int, dc: int, player: int) -> tuple[int, int]:
    count = 0
    r = row + dr
    c = col + dc

    while 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE and board[r, c] == player:
        count += 1
        r += dr
        c += dc

    open_end = 0
    if 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE and board[r, c] == EMPTY:
        open_end = 1

    return count, open_end


def analyze_lines_after_action(game: Game, action: int, player: int) -> list[dict]:
    row, col = action_to_row_col(action)

    if game.board[row, col] != EMPTY:
        return []

    temp_game = game.copy()
    temp_game.current_player = player

    success = temp_game.play_action(action)
    if not success:
        return []

    directions = [
        (1, 0),   # vertical
        (0, 1),   # horizontal
        (1, 1),   # diag \
        (1, -1),  # diag /
    ]

    lines = []

    for dr, dc in directions:
        c1, o1 = count_side(temp_game.board, row, col, dr, dc, player)
        c2, o2 = count_side(temp_game.board, row, col, -dr, -dc, player)

        length = 1 + c1 + c2
        open_ends = o1 + o2

        lines.append({
            "length": length,
            "open_ends": open_ends,
        })

    return lines


def creates_open_four(game: Game, action: int, player: int) -> bool:
    lines = analyze_lines_after_action(game, action, player)

    for line in lines:
        if line["length"] == 4 and line["open_ends"] == 2:
            return True

    return False


def find_immediate_win(game: Game, player: int, radius: int = 2) -> Optional[int]:
    candidate_actions = game.get_candidate_actions(radius=radius)

    for action in candidate_actions:
        temp_game = game.copy()
        temp_game.current_player = player

        success = temp_game.play_action(action)
        if not success:
            continue

        if temp_game.winner == player:
            return action

    return None


def find_immediate_block(game: Game, player: int, radius: int = 2) -> Optional[int]:
    opponent = -player
    return find_immediate_win(game, opponent, radius=radius)


def find_open_four_move(game: Game, player: int, radius: int = 2) -> Optional[int]:
    candidate_actions = game.get_candidate_actions(radius=radius)

    for action in candidate_actions:
        if creates_open_four(game, action, player):
            return action

    return None


def find_block_open_four_move(game: Game, player: int, radius: int = 2) -> Optional[int]:
    opponent = -player
    return find_open_four_move(game, opponent, radius=radius)