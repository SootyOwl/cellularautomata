import random
import time
import pygame
from cellularautomata.ca import CellularAutomata
from cellularautomata.rules2 import RainbowLife, RainbowLife2
import cv2
import numpy as np

# render to pygame window
class PygameRenderer:
    def __init__(self, cell_size, width, height):
        self.cell_size = cell_size
        self.cell_positions = [(j * self.cell_size, i * self.cell_size) for i in range(height) for j in range(width)]

    def draw(self, win, ca):
        grid: np.ndarray = ca.grid
        state_colors = ca.rules.get_state_colors(grid)
        state_colors = np.repeat(state_colors, self.cell_size, axis=0)
        state_colors = np.repeat(state_colors, self.cell_size, axis=1)
        # draw the grid
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
    def __init__(self, width=800, height=600, cell_size=10, rules=RainbowLife(), fps=10, ca=None):
        pygame.init()
        self.width = width
        self.height = height
        self.cell_size = cell_size
        self.fps = fps
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Cellular Automata")
        rows, cols = self.height // cell_size, self.width // cell_size
        if ca is None:
            self.ca = CellularAutomata(rows, cols, rules)
        else:
            self.ca = ca
        self.renderer = PygameRenderer(cell_size, rows, cols)

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            if not self.ca.update():
                # if the grid has not changed, stop the simulation early to save time
                running = False
            self.renderer.draw(self.screen, self.ca)
            pygame.display.flip()
            pygame.time.delay(1000 // self.fps)
        pygame.quit()


class GameMP4(Game):
    def __init__(self, run_seconds=60, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.run_seconds = run_seconds
        self.renderer = MP4Renderer(self.cell_size, (self.width, self.height), self.fps)

    def run(self):
        try:
            self._run()
        finally:
            self.renderer.close()
            pygame.quit()
        
    def _run(self):
        running = True
        total_frames = self.run_seconds * self.fps
        print(f"Running for {self.run_seconds} seconds, {total_frames} frames")
        while running and total_frames > 0:
            running, total_frames = self._run_one(total_frames)
            # log the progress every 1% of the total frames
            if total_frames % (self.fps * self.run_seconds // 100) == 0:
                print(f"{total_frames / (self.fps * self.run_seconds) * 100:.0f}% done")

    def _run_one(self, total_frames):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False, total_frames
        if not self.ca.update():
            return False, total_frames
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
    seed = random.randint(0, 1000000)
    print(f"Seed: {seed}")
    random.seed(seed)
    # configuration
    width, height = 1000, 1000  # pixels
    # cells per row and column
    num_cells = width // 10  # pixels per cell
    cell_size = width // num_cells
    num_states = 1000
    # % of the number of states that are considered equal to current state
    percentage = 0.02
    equality_threshold = int(num_states * percentage)
    fps = 30
    run_seconds = 60

    config = {
        "seed": seed,
        "width": width,
        "height": height,
        "cell_size": cell_size,
        "num_states": num_states,
        "fps": fps,
        "run_seconds": run_seconds,

        "equality_threshold": equality_threshold,
    }

    rules = RainbowLife2(
        seed=seed,
        num_states=num_states, 
        pastel=True, 
        scroll=False,
        equality_threshold=equality_threshold
    )
    game = GameMP4(
        width=width, 
        height=height, 
        cell_size=cell_size, 
        rules=rules, 
        fps=fps, 
        run_seconds=run_seconds
    )
    game.run()

    # pop up a little save y/n dialog box
    import os
    if input("Save the video? (y/n): ").lower() != "y":
        os.remove("output.mp4")
        exit()

    # generate a filename from configuration and rules class name
    class_name = rules.__class__.__name__
    filename = f"{class_name}_{num_states}_{width}x{height}_{cell_size}px__{time.time()}.mp4"
    # rename the output file
    import os
    import json
    # make a directory if it doesn't exist
    os.makedirs("videos", exist_ok=True)
    filename = os.path.join("videos", filename)
    os.rename("output.mp4", filename)
    # add a summary message
    summary = f"""{str(rules)}

Configuration dict:
{json.dumps(config, indent=2)}

Video saved as {filename}
"""
    print(summary)
    summary_filename = filename.replace(".mp4", ".txt")
    with open(summary_filename, "w") as f:
        f.write(summary)
    # main()

    # from cProfile import Profile
    # from pstats import Stats
    # rules = RainbowLife(num_states=5, pastel=True, scroll=False)
    # game = GameMP4(width=800, height=800, cell_size=4, rules=rules, fps=10, run_seconds=1)
    # profiler = Profile()
    # profiler.runcall(game.run)
    # stats = Stats(profiler)
    # stats.strip_dirs()
    # stats.sort_stats('cumulative')
    # stats.print_stats()
    