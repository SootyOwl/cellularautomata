import pygame
import numpy as np

from cellularautomata.rules import ConwayRules

class CellularAutomata:
    def __init__(self, rows, cols, rules):
        self.rows = rows
        self.cols = cols
        self.grid = np.random.choice([0, 1], size=(rows, cols))
        self.rules = rules

    def update(self):
        new_grid = self.grid.copy()
        for i in range(self.rows):
            for j in range(self.cols):
                state = self.grid[i][j]
                alive_neighbors = self.count_alive_neighbors(i, j)
                new_grid[i][j] = self.rules.apply(state, alive_neighbors)
        self.grid = new_grid

    def count_alive_neighbors(self, x, y):
        sum = 0
        for i in range(-1, 2):
            for j in range(-1, 2):
                if i == 0 and j == 0:
                    continue
                nx, ny = (x + i) % self.rows, (y + j) % self.cols
                sum += self.grid[nx][ny]
        return sum

class Renderer:
    def __init__(self, cell_size=10):
        self.cell_size = cell_size

    def draw(self, win, ca):
        win.fill((0, 0, 0))  # Fill background with black
        for i in range(ca.rows):
            for j in range(ca.cols):
                cell = ca.grid[i][j]
                color = ca.rules.get_state_color(cell)
                pygame.draw.rect(win, color, (j * self.cell_size, i * self.cell_size, self.cell_size, self.cell_size))

class Game:
    def __init__(self, width=800, height=600, cell_size=10):
        pygame.init()
        self.width = width
        self.height = height
        self.cell_size = cell_size
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Cellular Automata")

        rows, cols = self.height // cell_size, self.width // cell_size
        self.ca = CellularAutomata(rows, cols, ConwayRules())
        self.renderer = Renderer(cell_size)

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            self.ca.update()
            self.renderer.draw(self.screen, self.ca)
            pygame.display.flip()
            pygame.time.delay(100)

        pygame.quit()



def main():
    game = Game()
    game.run()
