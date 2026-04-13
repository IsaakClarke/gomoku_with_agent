from __future__ import annotations

import random
import pygame

from gomoku.config import (
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    FPS,
    BLACK,
    WHITE,
    MAX_UNDOS_PER_HUMAN,
)
from gomoku.game import Game
from gomoku.agent import AIPlayer
from ui.renderer import draw_full_board, screen_to_board
from ui.menu import MainMenu, SetupMenu, InGameButtons


class GomokuApp:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Gomoku 15x15")

        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()

        self.title_font = pygame.font.SysFont("arial", 40, bold=True)
        self.font = pygame.font.SysFont("arial", 26)
        self.small_font = pygame.font.SysFont("arial", 22)

        self.main_menu = MainMenu(self.title_font, self.font)
        self.setup_menu = SetupMenu(self.title_font, self.font)
        self.in_game_buttons = InGameButtons(self.small_font)

        self.state = "main_menu"   # main_menu / setup_menu / game
        self.game_mode = None      # hvh / hvai / aivai

        self.game = Game()

        self.ai_black: AIPlayer | None = None
        self.ai_white: AIPlayer | None = None

        self.human_black = True
        self.human_white = True

        self.difficulty = "medium"

        self.ai_thinking = False
        self.running = True

        self.best_checkpoint_path = "checkpoints/best.pt"

    def run(self):
        while self.running:
            if self.state == "main_menu":
                self._run_main_menu()
            elif self.state == "setup_menu":
                self._run_setup_menu()
            elif self.state == "game":
                self._run_game()

        pygame.quit()

    # --------------------------------------------------
    # MAIN MENU
    # --------------------------------------------------

    def _run_main_menu(self):
        while self.running and self.state == "main_menu":
            mouse_pos = pygame.mouse.get_pos()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return

                action = self.main_menu.handle_event(event)
                if action == "quit":
                    self.running = False
                    return
                elif action == "hvh":
                    self._start_hvh()
                    return
                elif action == "hvai":
                    self.state = "setup_menu"
                    return
                elif action == "aivai":
                    self._start_aivai()
                    return

            self.main_menu.draw(self.screen, mouse_pos)
            pygame.display.flip()
            self.clock.tick(FPS)

    # --------------------------------------------------
    # SETUP MENU
    # --------------------------------------------------

    def _run_setup_menu(self):
        while self.running and self.state == "setup_menu":
            mouse_pos = pygame.mouse.get_pos()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return

                action, payload = self.setup_menu.handle_event(event)

                if action == "back":
                    self.state = "main_menu"
                    return

                if action == "start":
                    self._start_hvai(payload["difficulty"], payload["human_color"])
                    return

            self.setup_menu.draw(self.screen, mouse_pos)
            pygame.display.flip()
            self.clock.tick(FPS)

    # --------------------------------------------------
    # GAME LOOP
    # --------------------------------------------------

    def _run_game(self):
        while self.running and self.state == "game":
            mouse_pos = pygame.mouse.get_pos()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.state = "main_menu"
                        return

                # sidebar buttons
                button_action = self.in_game_buttons.handle_event(event)
                if button_action is not None:
                    if button_action == "restart":
                        self._restart_current_game()
                    elif button_action == "undo":
                        self._handle_undo()
                    elif button_action == "redo":
                        self._handle_redo()
                    elif button_action == "menu":
                        self.state = "main_menu"
                        return

                # board click for human move
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self._current_player_is_human() and not self.game.is_terminal():
                        row, col = screen_to_board(*event.pos)
                        if row is not None and col is not None:
                            self.game.play_move(row, col)

            # AI move
            if not self.game.is_terminal() and not self._current_player_is_human():
                self.ai_thinking = True
                self._draw_game_screen(mouse_pos)
                pygame.display.flip()

                ai_player = self._get_current_ai_player()
                if ai_player is not None:
                    decision = ai_player.choose_move(self.game)
                    if decision is not None:
                        row, col = divmod(decision.action, 15)
                        self.game.play_move(row, col)

                self.ai_thinking = False

            self._draw_game_screen(mouse_pos)
            pygame.display.flip()
            self.clock.tick(FPS)

    # --------------------------------------------------
    # START MODES
    # --------------------------------------------------

    def _start_hvh(self):
        self.state = "game"
        self.game_mode = "hvh"
        self.game.reset()

        self.human_black = True
        self.human_white = True

        self.ai_black = None
        self.ai_white = None

        self.difficulty = "-"

    def _start_hvai(self, difficulty: str, human_color: str):
        self.state = "game"
        self.game_mode = "hvai"
        self.game.reset()

        self.difficulty = difficulty

        if human_color == "black":
            self.human_black = True
            self.human_white = False
            self.ai_black = None
            self.ai_white = AIPlayer(self.best_checkpoint_path, difficulty=difficulty, device=self._get_device())
        else:
            self.human_black = False
            self.human_white = True
            self.ai_black = AIPlayer(self.best_checkpoint_path, difficulty=difficulty, device=self._get_device())
            self.ai_white = None

    def _start_aivai(self):
        self.state = "game"
        self.game_mode = "aivai"
        self.game.reset()

        self.difficulty = "hard"

        self.human_black = False
        self.human_white = False

        self.ai_black = AIPlayer(self.best_checkpoint_path, difficulty="medium", device=self._get_device())
        self.ai_white = AIPlayer(self.best_checkpoint_path, difficulty="hard", device=self._get_device())

    # --------------------------------------------------
    # HELPERS
    # --------------------------------------------------

    def _get_device(self) -> str:
        try:
            import torch
            return "cuda" if torch.cuda.is_available() else "cpu"
        except Exception:
            return "cpu"

    def _current_player_is_human(self) -> bool:
        if self.game.current_player == BLACK:
            return self.human_black
        return self.human_white

    def _get_current_ai_player(self) -> AIPlayer | None:
        if self.game.current_player == BLACK:
            return self.ai_black
        return self.ai_white

    def _restart_current_game(self):
        if self.game_mode == "hvh":
            self._start_hvh()
        elif self.game_mode == "hvai":
            # сохраняем текущий setup hvai
            if self.human_black:
                self._start_hvai(self.difficulty, "black")
            else:
                self._start_hvai(self.difficulty, "white")
        elif self.game_mode == "aivai":
            self._start_aivai()

    def _handle_undo(self):
        if self.game_mode == "aivai":
            return

        if self.game_mode == "hvh":
            self.game.undo(MAX_UNDOS_PER_HUMAN)
            return

        # hvai:
        # в human vs ai обычно удобнее откатывать 2 хода:
        # свой и AI, чтобы снова был ход человека
        if self.game_mode == "hvai":
            undone = self.game.undo(MAX_UNDOS_PER_HUMAN)
            if undone and len(self.game.move_history) > 0 and not self._current_player_is_human():
                self.game.undo(MAX_UNDOS_PER_HUMAN)

    def _handle_redo(self):
        if self.game_mode == "aivai":
            return

        if self.game_mode == "hvh":
            self.game.redo()
            return

        # hvai:
        # redo тоже возвращаем 2 хода, если есть
        if self.game_mode == "hvai":
            did_redo = self.game.redo()
            if did_redo and self.game.can_redo() and not self._current_player_is_human():
                self.game.redo()

    def _draw_game_screen(self, mouse_pos: tuple[int, int]):
        black_undo_left = MAX_UNDOS_PER_HUMAN - self.game.black_undos_used
        white_undo_left = MAX_UNDOS_PER_HUMAN - self.game.white_undos_used

        mode_text = {
            "hvh": "Human vs Human",
            "hvai": "Human vs AI",
            "aivai": "AI vs AI",
        }.get(self.game_mode, "-")

        draw_full_board(
            screen=self.screen,
            game=self.game,
            mode_text=mode_text,
            difficulty_text=self.difficulty,
            thinking=self.ai_thinking,
            black_undo_left=max(0, black_undo_left),
            white_undo_left=max(0, white_undo_left),
            font=self.font,
            small_font=self.small_font,
        )

        self.in_game_buttons.draw(self.screen, mouse_pos)