import pygame
from cellularautomata.ca import CellularAutomata
from cellularautomata.rules2 import RainbowLife
import cv2
import numpy as np

# render to pygame window
class PygameRenderer:
    def __init__(self, cell_size, width, height):
        self.cell_size = cell_size
        self.cell_positions = [(j * self.cell_size, i * self.cell_size) for i in range(height) for j in range(width)]

    def draw(self, win, ca):
        # state_colors = [ca.rules.get_state_color(ca.grid[i, j]) for i in range(ca.rows) for j in range(ca.cols)]
        # cells = [(pos, color) for pos, color in zip(self.cell_positions, state_colors)]
        # for pos, color in cells:
        #     pygame.draw.rect(win, color, (pos[0], pos[1], self.cell_size, self.cell_size))
        state_colors = np.array([ca.rules.get_state_color(ca.grid[i, j]) for i in range(ca.rows) for j in range(ca.cols)])
        # account for cell size 
        state_colors = state_colors.reshape((ca.rows, ca.cols, 3))
        state_colors = np.repeat(state_colors, self.cell_size, axis=0)
        state_colors = np.repeat(state_colors, self.cell_size, axis=1)
        pygame.surfarray.blit_array(win, state_colors)

# render to mp4 file using opencv
class MP4Renderer(PygameRenderer):
    def __init__(self, cell_size, frame_size, fps):
        self.fps = fps
        self.filename = "output.mp4"
        self.fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        self.out = cv2.VideoWriter(self.filename, self.fourcc, fps, frame_size)
        super().__init__(cell_size, frame_size[0]//cell_size, frame_size[1]//cell_size)

    def draw(self, win, ca):
        frame = pygame.surfarray.array3d(win)
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        self.out.write(frame)
        super().draw(win, ca)

    def close(self):
        self.out.release()



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
        self.renderer = PygameRenderer(cell_size, rows, cols)

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


class GameMP4(Game):
    def __init__(self, width=800, height=600, cell_size=10, rules=RainbowLife(), fps=10, run_seconds=10):
        super().__init__(width, height, cell_size, rules, fps)
        self.run_seconds = run_seconds
        self.renderer = MP4Renderer(cell_size, (width, height), fps)

    def run(self):
        try:
            self._run()
        except Exception as e:
            print(e)
            self.renderer.close()
            pygame.quit()
        finally:
            self.renderer.close()
            pygame.quit()
        
    def _run(self):
        running = True
        total_frames = self.run_seconds * self.fps
        while running and total_frames > 0:
            running, total_frames = self._run_one(total_frames)

    def _run_one(self, total_frames, draw=True):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False, total_frames
        self.ca.update()
        if draw:
            self.renderer.draw(self.screen, self.ca)
            pygame.display.flip()
            pygame.time.delay(1000 // self.fps)
        total_frames -= 1
        return True, total_frames

def main():
    rules = RainbowLife(num_states=10, pastel=False, scroll=False)
    game = Game(width=1500, height=1500, cell_size=15, rules=rules, fps=60)
    input("Press Enter to start the game.")
    game.run()


if __name__ == "__main__":
    width, height = 1000, 1000  # pixels
    cell_size = 5  # pixels
    num_states = 8
    fps = 24

    rules = RainbowLife(
        num_states=num_states, 
        pastel=True, 
        scroll=False
    )
    game = GameMP4(
        width=width, 
        height=height, 
        cell_size=cell_size, 
        rules=rules, 
        fps=fps, 
        run_seconds=60
    )
    game.run()
    # generate a filename from configuration
    filename = f"rainbowlife_{num_states}_{width}x{height}_{cell_size}px.mp4"
    # rename the output file
    import os
    os.rename("output.mp4", filename)
    print(f"Output file: {filename}")

    # main()

    # from cProfile import Profile
    # from pstats import Stats
    # rules = RainbowLife(num_states=10, pastel=True, scroll=False)
    # game = GameMP4(width=1500, height=1500, cell_size=15, rules=rules, fps=2, run_seconds=1)
    # profiler = Profile()
    # profiler.runcall(game.run)
    # stats = Stats(profiler)
    # stats.strip_dirs()
    # stats.sort_stats('cumulative')
    # stats.print_stats()
    