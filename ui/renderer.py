from __future__ import annotations

import pygame

from gomoku.config import (
    BOARD_SIZE,
    BOARD_PADDING,
    CELL_SIZE,
    STONE_RADIUS,
    LAST_MOVE_RADIUS,
    SIDEBAR_X,
    COLOR_BG,
    COLOR_GRID,
    COLOR_BLACK,
    COLOR_WHITE,
    COLOR_LAST_MOVE,
    COLOR_TEXT,
    COLOR_PANEL,
)
from gomoku.game import Game


def board_to_screen(row: int, col: int) -> tuple[int, int]:
    x = BOARD_PADDING + col * CELL_SIZE
    y = BOARD_PADDING + row * CELL_SIZE
    return x, y


def screen_to_board(mouse_x: int, mouse_y: int) -> tuple[int | None, int | None]:
    col = round((mouse_x - BOARD_PADDING) / CELL_SIZE)
    row = round((mouse_y - BOARD_PADDING) / CELL_SIZE)

    if 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE:
        x, y = board_to_screen(row, col)

        if abs(mouse_x - x) <= CELL_SIZE // 2 and abs(mouse_y - y) <= CELL_SIZE // 2:
            return row, col

    return None, None


def draw_background(screen: pygame.Surface) -> None:
    screen.fill(COLOR_BG)


def draw_board_grid(screen: pygame.Surface) -> None:
    start = BOARD_PADDING
    end = BOARD_PADDING + CELL_SIZE * (BOARD_SIZE - 1)

    for i in range(BOARD_SIZE):
        x = BOARD_PADDING + i * CELL_SIZE
        pygame.draw.line(screen, COLOR_GRID, (x, start), (x, end), 1)

    for i in range(BOARD_SIZE):
        y = BOARD_PADDING + i * CELL_SIZE
        pygame.draw.line(screen, COLOR_GRID, (start, y), (end, y), 1)


def draw_star_points(screen: pygame.Surface) -> None:
    star_points = [
        (3, 3), (3, 7), (3, 11),
        (7, 3), (7, 7), (7, 11),
        (11, 3), (11, 7), (11, 11),
    ]

    for row, col in star_points:
        x, y = board_to_screen(row, col)
        pygame.draw.circle(screen, COLOR_GRID, (x, y), 4)


def draw_stones(screen: pygame.Surface, game: Game) -> None:
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            cell = game.board[row, col]
            if cell == 0:
                continue

            x, y = board_to_screen(row, col)

            if cell == 1:
                pygame.draw.circle(screen, COLOR_BLACK, (x, y), STONE_RADIUS)
            else:
                pygame.draw.circle(screen, COLOR_WHITE, (x, y), STONE_RADIUS)
                pygame.draw.circle(screen, COLOR_GRID, (x, y), STONE_RADIUS, 1)


def draw_last_move_marker(screen: pygame.Surface, game: Game) -> None:
    if game.last_move is None:
        return

    row, col = game.last_move
    x, y = board_to_screen(row, col)
    pygame.draw.circle(screen, COLOR_LAST_MOVE, (x, y), LAST_MOVE_RADIUS)


def draw_sidebar_panel(screen: pygame.Surface) -> None:
    panel_rect = pygame.Rect(SIDEBAR_X, 20, 200, 780)
    pygame.draw.rect(screen, COLOR_PANEL, panel_rect, border_radius=12)


def draw_text(screen: pygame.Surface, text: str, font: pygame.font.Font, x: int, y: int, color=COLOR_TEXT) -> None:
    surface = font.render(text, True, color)
    screen.blit(surface, (x, y))


def draw_game_status(
    screen: pygame.Surface,
    game: Game,
    mode_text: str,
    difficulty_text: str,
    thinking: bool,
    black_undo_left: int,
    white_undo_left: int,
    font: pygame.font.Font,
    small_font: pygame.font.Font,
) -> None:
    draw_sidebar_panel(screen)

    draw_text(screen, "GOMOKU 15x15", font, SIDEBAR_X + 20, 40)
    draw_text(screen, f"Mode: {mode_text}", small_font, SIDEBAR_X + 20, 110)
    draw_text(screen, f"Difficulty: {difficulty_text}", small_font, SIDEBAR_X + 20, 140)

    if game.winner == 1:
        status = "Winner: Black"
    elif game.winner == -1:
        status = "Winner: White"
    elif game.is_draw():
        status = "Draw"
    else:
        status = "Turn: Black" if game.current_player == 1 else "Turn: White"

    draw_text(screen, status, small_font, SIDEBAR_X + 20, 190)

    if thinking and not game.is_terminal():
        draw_text(screen, "AI is thinking...", small_font, SIDEBAR_X + 20, 230)

    draw_text(screen, f"Moves: {game.move_count}", small_font, SIDEBAR_X + 20, 280)
    draw_text(screen, f"Black undo left: {black_undo_left}", small_font, SIDEBAR_X + 20, 320)
    draw_text(screen, f"White undo left: {white_undo_left}", small_font, SIDEBAR_X + 20, 350)


def draw_full_board(
    screen: pygame.Surface,
    game: Game,
    mode_text: str,
    difficulty_text: str,
    thinking: bool,
    black_undo_left: int,
    white_undo_left: int,
    font: pygame.font.Font,
    small_font: pygame.font.Font,
) -> None:
    draw_background(screen)
    draw_board_grid(screen)
    draw_star_points(screen)
    draw_stones(screen, game)
    draw_last_move_marker(screen, game)

    draw_game_status(
        screen=screen,
        game=game,
        mode_text=mode_text,
        difficulty_text=difficulty_text,
        thinking=thinking,
        black_undo_left=black_undo_left,
        white_undo_left=white_undo_left,
        font=font,
        small_font=small_font,
    )