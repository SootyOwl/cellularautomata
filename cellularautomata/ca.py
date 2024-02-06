from functools import partial
import numpy as np

class CellularAutomata:
    def __init__(self, rows, cols, rules, init_mode="gradient-diag2"):
        self.rows = rows
        self.cols = cols
        self.rules = rules
        self.seed = self.rules.seed
        # seed the grid
        if init_mode == "random":
            self.seed_random_grid()
        elif init_mode == "solid":
            self.grid = np.zeros((self.rows, self.cols), dtype=int)
        elif init_mode == "gradient-diag1":
            self.create_gradient_diag(1)
        elif init_mode == "gradient-diag2":
            self.create_gradient_diag(2)
        elif init_mode == "gradient-vert":
            self.grid = np.zeros((self.rows, self.cols), dtype=int)
            for i in range(self.rows):
                self.grid[i, :] = int(i / self.rows * self.rules.num_states)
        elif init_mode == "gradient-horiz":
            self.grid = np.zeros((self.rows, self.cols), dtype=int)
            for j in range(self.cols):
                self.grid[:, j] = int(j / self.cols * self.rules.num_states)
        else:
            raise ValueError(f"init_mode {init_mode} not recognized")

    def seed_random_grid(self):
        np.random.seed(self.seed)
        self.grid = np.random.choice(self.rules.possible_states, size=(self.rows, self.cols))

    def create_gradient_diag(self, mode: int):
        """Create a gradient grid with smooth transitions between states.
        mode 1: gradient from top-left to bottom-right
        mode 2: gradient from top-right to bottom-left
        mode 3: gradient from bottom-left to top-right
        mode 4: gradient from bottom-right to top-left
        """
        self.grid = np.zeros((self.rows, self.cols), dtype=int)
        for i in range(self.rows):
            for j in range(self.cols):
                if mode == 1:
                    self.grid[i, j] = int((i + j) / (self.rows + self.cols) * self.rules.num_states)
                elif mode == 2:
                    self.grid[i, j] = int((i + self.cols - j) / (self.rows + self.cols) * self.rules.num_states)
                elif mode == 3:
                    self.grid[i, j] = int((self.rows - i + j) / (self.rows + self.cols) * self.rules.num_states)
                elif mode == 4:
                    self.grid[i, j] = int((self.rows - i + self.cols - j) / (self.rows + self.cols) * self.rules.num_states)

    def update(self):
        new_grid = self.grid.copy()
        for i in range(self.rows):
            for j in range(self.cols):
                new_grid[i, j] = self.rules.apply(self.grid, (i, j))
        # check if the grid has changed
        if not np.array_equal(new_grid, self.grid):
            self.grid = new_grid
            return True
        # if the grid has not changed, stop the simulation
        else:
            return False


from multiprocessing import Pool
import itertools
import os

class CellularAutomataMP(CellularAutomata):

    def __init__(self, *args, processes=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.positions = list(itertools.product(range(self.rows), range(self.cols)))
        if not processes:
            processes = os.cpu_count() - 1  # leave one core for the OS and other processes
        self.pool = Pool(processes=processes)


    def update(self):
        """Use multiprocessing.Pool to create the new grid."""
        new_grid = self.grid.copy()
        apply = partial(self.rules.apply, self.grid)
        new_grid = np.array(self.pool.map(apply, self.positions)).reshape(self.rows, self.cols)
        # check if the grid has changed
        if not np.array_equal(new_grid, self.grid):
            self.grid = new_grid
            return True
        # if the grid has not changed, stop the simulation
        else:
            return False
        

if __name__ == "__main__":
    # tell speed of MP vs non-MP
    from cellularautomata.rules2 import RainbowLife2
    import time

    rules = RainbowLife2(seed=0, num_states=50, pastel=True, scroll=False, equality_threshold=0)
    # non-MP
    start = time.time()
    ca = CellularAutomata(100, 100, rules)
    for _ in range(100):
        assert ca.update(), "Grid did not change after update"
    time_elapsed = time.time() - start
    print("Non-MP:", time_elapsed)

    rules2 = RainbowLife2(seed=0, num_states=50, pastel=True, scroll=False, equality_threshold=0)
    # MP
    start = time.time()
    ca2 = CellularAutomataMP(100, 100, rules, processes=15)
    for _ in range(100):
        assert ca2.update(), "Grid did not change after update"
    time_elapsed2 = time.time() - start
    print("MP:", time_elapsed2)
    print(f"MP is {time_elapsed / time_elapsed2:.2f} times faster")

    assert np.array_equal(ca.grid, ca2.grid), "Grids are not equal"