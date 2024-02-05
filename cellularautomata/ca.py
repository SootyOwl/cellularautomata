from functools import partial
import numpy as np

class CellularAutomata:
    def __init__(self, rows, cols, rules):
        self.rows = rows
        self.cols = cols
        self.rules = rules
        self.seed = self.rules.seed
        # seed the grid
        np.random.seed(self.seed)
        self.grid = np.random.choice(self.rules.possible_states, size=(rows, cols))

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

class CellularAutomataMP(CellularAutomata):

    def __init__(self, rows, cols, rules, processes=4):
        super().__init__(rows, cols, rules)
        self.positions = list(itertools.product(range(self.rows), range(self.cols)))
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