import numpy as np

class CellularAutomata:
    def __init__(self, rows, cols, rules):
        self.rows = rows
        self.cols = cols
        self.rules = rules
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
