from __future__ import annotations

import pygame

from gomoku.config import COLOR_BUTTON, COLOR_BUTTON_HOVER, COLOR_TEXT


class Button:
    def __init__(self, x: int, y: int, width: int, height: int, text: str, font: pygame.font.Font):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font

    def draw(self, screen: pygame.Surface, mouse_pos: tuple[int, int]) -> None:
        color = COLOR_BUTTON_HOVER if self.rect.collidepoint(mouse_pos) else COLOR_BUTTON
        pygame.draw.rect(screen, color, self.rect, border_radius=10)

        text_surface = self.font.render(self.text, True, COLOR_TEXT)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def is_clicked(self, event: pygame.event.Event) -> bool:
        return (
            event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
            and self.rect.collidepoint(event.pos)
        )