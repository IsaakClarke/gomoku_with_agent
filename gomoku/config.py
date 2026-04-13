from dataclasses import dataclass


BOARD_SIZE = 15
ACTION_SIZE = BOARD_SIZE * BOARD_SIZE

EMPTY = 0
BLACK = 1
WHITE = -1


WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 820
FPS = 60

BOARD_PADDING = 60
CELL_SIZE = 46

STONE_RADIUS = 18
LAST_MOVE_RADIUS = 6

SIDEBAR_X = 780
SIDEBAR_WIDTH = 200


COLOR_BG = (240, 217, 181)
COLOR_GRID = (60, 40, 20)
COLOR_BLACK = (30, 30, 30)
COLOR_WHITE = (245, 245, 245)
COLOR_LAST_MOVE = (220, 60, 60)
COLOR_TEXT = (20, 20, 20)
COLOR_BUTTON = (180, 150, 100)
COLOR_BUTTON_HOVER = (200, 170, 120)
COLOR_PANEL = (225, 205, 170)


MAX_UNDOS_PER_HUMAN = 3


@dataclass
class AIConfig:
    name: str
    simulations: int
    cpuct: float
    use_temperature: bool
    use_tactics: bool = True


AI_CONFIGS = {
    "easy": AIConfig(
        name="easy",
        simulations=50,
        cpuct=1.5,
        use_temperature=True,
        use_tactics=True,
    ),
    "medium": AIConfig(
        name="medium",
        simulations=120,
        cpuct=1.5,
        use_temperature=False,
        use_tactics=True,
    ),
    "hard": AIConfig(
        name="hard",
        simulations=250,
        cpuct=1.5,
        use_temperature=False,
        use_tactics=True,
    ),
}