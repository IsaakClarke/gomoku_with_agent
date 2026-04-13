from __future__ import annotations

import random
import pygame

from gomoku.config import WINDOW_WIDTH, WINDOW_HEIGHT, COLOR_BG, COLOR_TEXT
from ui.widgets import Button


class MainMenu:
    def __init__(self, title_font: pygame.font.Font, button_font: pygame.font.Font):
        center_x = WINDOW_WIDTH // 2 - 140

        self.title_font = title_font
        self.button_font = button_font

        self.btn_hvh = Button(center_x, 220, 280, 55, "Human vs Human", button_font)
        self.btn_hvai = Button(center_x, 300, 280, 55, "Human vs AI", button_font)
        self.btn_aivai = Button(center_x, 380, 280, 55, "AI vs AI", button_font)
        self.btn_quit = Button(center_x, 500, 280, 55, "Quit", button_font)

    def draw(self, screen: pygame.Surface, mouse_pos: tuple[int, int]) -> None:
        screen.fill(COLOR_BG)

        title_surface = self.title_font.render("GOMOKU 15x15", True, COLOR_TEXT)
        title_rect = title_surface.get_rect(center=(WINDOW_WIDTH // 2, 120))
        screen.blit(title_surface, title_rect)

        self.btn_hvh.draw(screen, mouse_pos)
        self.btn_hvai.draw(screen, mouse_pos)
        self.btn_aivai.draw(screen, mouse_pos)
        self.btn_quit.draw(screen, mouse_pos)

    def handle_event(self, event: pygame.event.Event) -> str | None:
        if self.btn_hvh.is_clicked(event):
            return "hvh"
        if self.btn_hvai.is_clicked(event):
            return "hvai"
        if self.btn_aivai.is_clicked(event):
            return "aivai"
        if self.btn_quit.is_clicked(event):
            return "quit"
        return None


class SetupMenu:
    def __init__(self, title_font: pygame.font.Font, button_font: pygame.font.Font):
        center_x = WINDOW_WIDTH // 2 - 140

        self.title_font = title_font
        self.button_font = button_font

        # difficulty
        self.btn_easy = Button(center_x, 180, 280, 50, "Difficulty: Easy", button_font)
        self.btn_medium = Button(center_x, 240, 280, 50, "Difficulty: Medium", button_font)
        self.btn_hard = Button(center_x, 300, 280, 50, "Difficulty: Hard", button_font)

        # color
        self.btn_black = Button(center_x, 390, 280, 50, "Play as Black", button_font)
        self.btn_white = Button(center_x, 450, 280, 50, "Play as White", button_font)
        self.btn_random = Button(center_x, 510, 280, 50, "Random Color", button_font)

        self.btn_start = Button(center_x, 610, 280, 55, "Start Game", button_font)
        self.btn_back = Button(center_x, 680, 280, 55, "Back", button_font)

        self.selected_difficulty = "medium"
        self.selected_color = "random"

    def draw(self, screen: pygame.Surface, mouse_pos: tuple[int, int]) -> None:
        screen.fill(COLOR_BG)

        title_surface = self.title_font.render("SETUP HUMAN VS AI", True, COLOR_TEXT)
        title_rect = title_surface.get_rect(center=(WINDOW_WIDTH // 2, 100))
        screen.blit(title_surface, title_rect)

        self.btn_easy.draw(screen, mouse_pos)
        self.btn_medium.draw(screen, mouse_pos)
        self.btn_hard.draw(screen, mouse_pos)

        self.btn_black.draw(screen, mouse_pos)
        self.btn_white.draw(screen, mouse_pos)
        self.btn_random.draw(screen, mouse_pos)

        self.btn_start.draw(screen, mouse_pos)
        self.btn_back.draw(screen, mouse_pos)

        info1 = self.button_font.render(f"Selected difficulty: {self.selected_difficulty}", True, COLOR_TEXT)
        screen.blit(info1, (WINDOW_WIDTH // 2 - 120, 130))

        info2 = self.button_font.render(f"Selected color: {self.selected_color}", True, COLOR_TEXT)
        screen.blit(info2, (WINDOW_WIDTH // 2 - 120, 350))

    def handle_event(self, event: pygame.event.Event) -> tuple[str | None, dict | None]:
        if self.btn_easy.is_clicked(event):
            self.selected_difficulty = "easy"
        elif self.btn_medium.is_clicked(event):
            self.selected_difficulty = "medium"
        elif self.btn_hard.is_clicked(event):
            self.selected_difficulty = "hard"
        elif self.btn_black.is_clicked(event):
            self.selected_color = "black"
        elif self.btn_white.is_clicked(event):
            self.selected_color = "white"
        elif self.btn_random.is_clicked(event):
            self.selected_color = "random"
        elif self.btn_start.is_clicked(event):
            color = self.selected_color
            if color == "random":
                color = random.choice(["black", "white"])

            return "start", {
                "difficulty": self.selected_difficulty,
                "human_color": color,
            }
        elif self.btn_back.is_clicked(event):
            return "back", None

        return None, None


class InGameButtons:
    def __init__(self, button_font: pygame.font.Font):
        self.btn_restart = Button(800, 430, 160, 45, "Restart", button_font)
        self.btn_undo = Button(800, 490, 160, 45, "Undo", button_font)
        self.btn_redo = Button(800, 550, 160, 45, "Redo", button_font)
        self.btn_menu = Button(800, 610, 160, 45, "Main Menu", button_font)

    def draw(self, screen: pygame.Surface, mouse_pos: tuple[int, int]) -> None:
        self.btn_restart.draw(screen, mouse_pos)
        self.btn_undo.draw(screen, mouse_pos)
        self.btn_redo.draw(screen, mouse_pos)
        self.btn_menu.draw(screen, mouse_pos)

    def handle_event(self, event: pygame.event.Event) -> str | None:
        if self.btn_restart.is_clicked(event):
            return "restart"
        if self.btn_undo.is_clicked(event):
            return "undo"
        if self.btn_redo.is_clicked(event):
            return "redo"
        if self.btn_menu.is_clicked(event):
            return "menu"
        return None