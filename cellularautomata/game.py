import pygame
from cellularautomata.ca import CellularAutomata
from cellularautomata.rules2 import RainbowLife

class Renderer:
    def __init__(self, cell_size):
        self.cell_size = cell_size

    def draw(self, win, ca):
        for i in range(ca.rows):
            for j in range(ca.cols):
                color = ca.rules.get_state_color(ca.grid[i, j])
                pygame.draw.rect(win, color, (j * self.cell_size, i * self.cell_size, self.cell_size, self.cell_size))

class Game:
    def __init__(self, width=800, height=600, cell_size=10, rules=RainbowLife(), fps=10):
        pygame.init()
        self.width = width
        self.height = height
        self.cell_size = cell_size
        self.fps = fps
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Cellular Automata")
        rows, cols = self.height // cell_size, self.width // cell_size
        self.ca = CellularAutomata(rows, cols, rules)
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
            pygame.time.delay(1000 // self.fps)
        pygame.quit()

def main():
    rules = RainbowLife(num_states=7, pastel=True, scroll=False)
    game = Game(width=1500, height=1500, cell_size=15, rules=rules, fps=60)
    # input("Press Enter to start the game.")
    game.run()


if __name__ == "__main__":
    main()