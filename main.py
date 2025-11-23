import pygame
import sys

# 初期化
pygame.init()

from game import Game


if __name__ == "__main__":
    game = Game()
    game.run()
    sys.exit()
