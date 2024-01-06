import pygame, json
from dataclasses import dataclass

from icecream import ic

# class GameConfig:

#     DIMENSION = 8
#     TILE_WIDTH = 60
#     LIGHT = '#EEEEEE'
#     DARK = '#48a1d9'
#     ANIMATE = True
#     CAPTION = 'DL Chess'
#     FPS = 15
#     ASSETS_FOLDER = 'app/assets/'
#     PLAYER_WHITE = True
#     PLAYER_BLACK = False


#     BOARD_WIDTH = TILE_WIDTH * DIMENSION
#     WIN = pygame.display.set_mode((BOARD_WIDTH, BOARD_WIDTH))
#     pygame.display.set_caption(CAPTION)
#     CLOCK = pygame.time.Clock()
#     PIECES = ['bB', 'bK', 'bN', 'bP', 'bQ', 'bR', 'wB', 'wK', 'wN', 'wP', 'wQ', 'wR']
#     IMAGES = {}
#     for piece in PIECES:
#         IMAGES[piece] = pygame.image.load(ASSETS_FOLDER + piece + '.png')



#     @classmethod
#     def reset_clock(cls):
#         cls.CLOCK = pygame.time.Clock()



@dataclass
class GameConfig:
    DIMENSION: int
    TILE_WIDTH: int
    LIGHT: str
    DARK: str
    ANIMATE: bool
    CAPTION: str
    FPS: int
    ASSETS_FOLDER: str
    PLAYER_WHITE: bool
    PLAYER_BLACK: bool

    def __post_init__(self):
        self.BOARD_WIDTH = self.TILE_WIDTH * self.DIMENSION
        self.WIN = pygame.display.set_mode((self.BOARD_WIDTH, self.BOARD_WIDTH))
        pygame.display.set_caption(self.CAPTION)
        self.CLOCK = pygame.time.Clock()
        self.PIECES = ['bB', 'bK', 'bN', 'bP', 'bQ', 'bR', 'wB', 'wK', 'wN', 'wP', 'wQ', 'wR']
        self.IMAGES = {}
        for piece in self.PIECES:
            self.IMAGES[piece] = pygame.image.load(self.ASSETS_FOLDER + piece + '.png')

    def reset_clock(self):
        self.CLOCK = pygame.time.Clock()


json_file_path = 'app/config.json'
with open(json_file_path, 'r') as json_file:
    config_data = json.load(json_file)
GAME_CONFIG = GameConfig(**config_data)
