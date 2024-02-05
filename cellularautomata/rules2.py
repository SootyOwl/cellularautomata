from functools import lru_cache
import itertools
from collections import Counter
import random
import colorsys
import numpy as np

class Rules:
    def __init__(self):
        self.seed = random.randint(0, 100000) # Seed for the random number generator
        random.seed(self.seed)
        np.random.seed(self.seed)
        self.default_state = 0
        self.rules = {}
        self.possible_states = [0]

    def add_rule(self, configuration: str, result_state):
        self.rules[configuration] = result_state

    def apply(self, grid, position: tuple):
        configuration = self.get_configuration(grid, position)
        return self.rules.get(configuration, self.default_state)

    def get_configuration(self, grid, position) -> str:
        raise NotImplementedError("This method should provide the encoded configuration for the current grid and position.")

    def get_state_color(self, state):
        raise NotImplementedError("This method should provide the color representation for a given state.")

class GameOfLifeRules(Rules):
    def __init__(self):
        super().__init__()
        self.color_map = {
            0: (0, 0, 0),  # Dead / Empty
            1: (0, 255, 0),  # Alive / State 1
            # Add more states as needed
        }
        self.possible_states = [0, 1]
        # Add specific rules here, for example (Game of Life):
        # a dead cell comes to life with 3 neighbors
        self.add_rule("011100000", 1)  
        # a living cell survives if it has 2 or 3 neighbors
        self.add_rule("111000000", 1)  
        self.add_rule("111100000", 1)

    def get_configuration(self, grid, position) -> int:
        """Game of Life configuration, counting the number of living cells in the 8
        positions around the cell."""
        i, j = position
        state = grid[i][j]
        alive_neighbors = self.count_alive_neighbors(grid, i, j)
        return f"{state}{'1' * alive_neighbors}".ljust(9, "0")

    @staticmethod
    def count_alive_neighbors(grid, x, y):
        rows = len(grid)
        cols = len(grid[0])
        sum = 0
        for i in range(-1, 2):
            for j in range(-1, 2):
                if i == 0 and j == 0:
                    continue
                nx, ny = (x + i) % rows, (y + j) % cols
                sum += grid[nx][ny]
        return sum

    def get_state_color(self, state):
        return self.color_map.get(state, (255, 255, 255))  # Default to white if state is undefined



class TripleLife(Rules):
    """3 state, 8 neigbors"""

    def __init__(self):
        super().__init__()
        self.possible_states = [0, 1, 2]
        """Possible states for the cells."""

        self.alive_states = [1, 2]
        """States that are considered alive."""

        self.placeholder = "*"
        """Placeholder for any alive state."""

        ## Add specific rules here
        # a dead cell comes to life with 3 neighbors of any state
        self.add_rule("000000***", 1, placeholder_alive_only=True)
        self.add_rule("00000****", 2, placeholder_alive_only=True)
        # a living cell survives if it has 2 or 3 neighbors of any alive state, favoring the current state
        self.add_rule("100000*11", 1, placeholder_alive_only=True)
        self.add_rule("100000011", 1, placeholder_alive_only=True)
        self.add_rule("200000*22", 2, placeholder_alive_only=True)
        self.add_rule("200000022", 2, placeholder_alive_only=True)


    def get_configuration(self, grid, position) -> str:
        i, j = position
        state = grid[i][j]
        neighbors = self.get_neighbors(grid, position)
        # sort the neighbors so that the configuration is consistent
        neighbors.sort()
        neighbors = "".join(map(str, neighbors)).ljust(8, self.placeholder)
        return f"{state}{neighbors}"
    

    def add_rule(self, configuration: str, result_state, placeholder_alive_only=False, placeholder_dead_only=False):
        """Override the add_rule method to allow placeholder '*' for any state."""
        if self.placeholder not in configuration:
            super().add_rule(configuration, result_state)
            return
        
        # get the number of placeholders
        n = configuration.count(self.placeholder)
        # generate all possible combinations of states for the placeholders
        # order does not matter as the configuration is sorted
        placeholder_states = (self.alive_states if placeholder_alive_only else self.possible_states) if not placeholder_dead_only else [0]
        combinations = itertools.combinations_with_replacement(placeholder_states, n)
        for combination in combinations:
            c = configuration
            # replace the placeholders with the states
            for s in combination:
                c = c.replace(self.placeholder, str(s), 1)
            # sort the configuration so that it is consistent
            c = c[:1] + "".join(sorted(c[1:]))
            super().add_rule(c, result_state)
        

    def get_neighbors(self, grid, position):
        rows = len(grid)
        cols = len(grid[0])
        i, j = position
        neighbors = []
        # iterate over the 8 neighbors accounting for the grid wrapping
        for x in range(-1, 2):
            for y in range(-1, 2):
                if x == 0 and y == 0:
                    continue
                nx, ny = (i + x) % rows, (j + y) % cols
                neighbors.append(grid[nx][ny])

        return neighbors
        
    def get_state_color(self, state):
        if state == 1:
            return (0, 255, 0)
        elif state == 2:
            return (0, 0, 255)
        else:
            return (0, 0, 0)



class ElementaryCellularAutomata(Rules):
    def __init__(self, rule_number):
        super().__init__()
        self.rule_number = rule_number
        self.possible_states = [0, 1]
        self.rules = self.generate_rules(rule_number)
        self.color_map = {
            0: (0, 0, 0),
            1: (255, 255, 255)
        }

    def generate_rules(self, rule_number):
        rules = {}
        for i in range(7, -1, -1):
            rules[format(i, "03b")] = (rule_number >> i) & 1
        return rules

    def get_configuration(self, grid, position) -> str:
        i, j = position
        rows = len(grid)
        cols = len(grid[0])
        left = grid[i][(j - 1) % cols]
        center = grid[i][j]
        right = grid[i][(j + 1) % cols]
        return f"{left}{center}{right}"

    def get_state_color(self, state):
        return self.color_map.get(state, (255, 255, 255))  # Default to white if state is undefined
    

class Rainbow(Rules):
    """Ruleset that cycles through the colors of the rainbow."""
    def __init__(self):
        super().__init__()
        self.colors = [
            (255, 0, 0),  # Red
            (255, 127, 0),  # Orange
            (255, 255, 0),  # Yellow
            (0, 255, 0),  # Green
            (0, 0, 255),  # Blue
            (75, 0, 130),  # Indigo
            (143, 0, 255)  # Violet
        ]
        self.possible_states = [i for i in range(len(self.colors))]
        self.color_map = {i: self.colors[i] for i in range(len(self.colors))}
        self.rules = self.generate_rules()

    def generate_rules(self):
        """Define rules where red transitions to orange, orange to yellow, etc.
        and violet transitions to red."""
        rules = {}
        for i in range(len(self.colors)):
            rules[i] = (i + 1) % len(self.colors)
        return rules
        
    def get_configuration(self, grid, position) -> int:
        return grid[position[0]][position[1]]

    def get_state_color(self, state):
        return self.color_map.get(state, (255, 255, 255))  # Default to white if state is undefined
    

class RainbowLife(Rules):
    """Each color represents a different state, and the rules allow for transitions between the colors."""

    dx = np.array([-1, -1, -1, 0, 0, 1, 1, 1])
    dy = np.array([-1, 0, 1, -1, 1, -1, 0, 1])
    
    def __init__(self, num_states=7, pastel=False, scroll=False, seed=None):
        super().__init__()
        if seed is not None:
            self.seed = seed
            random.seed(self.seed)
            np.random.seed(self.seed)
        self.colors = self.generate_colors(num_states, pastel=pastel)
        self.num_states = num_states
        self.possible_states = [i for i in range(len(self.colors))]
        self.color_map = {i: self.colors[i] for i in range(len(self.colors))}
        self.rules = self.generate_rules(scroll=scroll)

    def __repr__(self):
        return f"RainbowLife(num_states={self.num_states})"
    
    def __str__(self):
        return f""""RainbowLife

Rules:
1. "Nonconformity is the only legitimate form of rebellion"
2. "When in Rome, do as the Romans do"
3. "Imitation is the sincerest form of flattery"

Explanation of the rules:
1. If a cell is the same as its 8 neighbors, it will change to the next colour in the list.
2. If a cell is different from all its neighbors, it will change to the most common colour among them.
3. Otherwise, the cell will choose a random neighbour and copy its colour, weighted by the number of neighbours with that colour.
"""

    def generate_colors(self, num_states, pastel=False, random_start=True):
        """Generate a list of colors that cycle through the color wheel.
        If pastel is True, the colors are desaturated.
        If random_start is True, the colors start at a random hue, otherwise they start at red."""
        if random_start:
            start_hue = random.random()
        else:
            start_hue = 0

        colors = []
        for i in range(num_states):
            h = (start_hue + i / num_states) % 1
            s = 0.4 if pastel else 1
            v = 1
            r, g, b = colorsys.hsv_to_rgb(h, s, v)
            colors.append((int(r * 255), int(g * 255), int(b * 255)))
        return colors

    def generate_rules(self, scroll=False):
        rules = {}
        for i in range(len(self.colors)):
            rules[i] = i if not scroll else (i + 1) % len(self.colors)
        return rules

    def get_configuration(self, grid: np.ndarray, position: tuple) -> int:
        neighbors = self.get_neighbors(grid, position)
        state = grid[position]
        return self.get_next_state(state, neighbors)
    
    def get_next_state(self, state: int, neighbors: tuple):
        # If I'm the same color as all my neighbors, I change color
        # "Nonconformity is the only legitimate form of rebellion."
        neighbor_states = set(neighbors)
        if neighbor_states == {state}:  # All neighbors are the same color as me
            return (state + 1) % self.num_states
        # If I'm different from all my neighbors, I change to the most common color among them
        # "When in Rome, do as the Romans do."
        if self._different_from_all(state, neighbors):
            return max(set(neighbors), key=neighbors.count)
        # otherwise, I choose an random neighbor to imitate
        # "Imitation is the sincerest form of flattery."
        # use set operations to get the unique neighbors and their weights
        unique_neighbors, weights = self._get_weights(neighbors)
        return random.choices(list(unique_neighbors), weights=weights)[0]

    @staticmethod
    @lru_cache(maxsize=None)
    def _get_weights(neighbors):
        unique_neighbors = set(neighbors)
        count = Counter(neighbors)
        weights = [count[n] for n in unique_neighbors]
        return unique_neighbors, weights
    
    @staticmethod
    @lru_cache(maxsize=None)
    def _different_from_all(state, neighbors):
        return set(neighbors) - {state} == set(neighbors)   
    
    @staticmethod
    @lru_cache(maxsize=None)
    def _get_neighbor_weights(neighbors):
        counter = Counter(neighbors)
        return [counter[n] for n in neighbors]
    
    def get_neighbors(self, grid: np.ndarray, position: tuple) -> tuple:
        """Extract the 8 neighbors of a cell."""
        rows, cols = grid.shape
        nx, ny = self.get_neighbor_positions(position, rows, cols)
        neighbors = grid[nx, ny]
        # sort the neighbors so that the configuration is consistent
        neighbors.sort()
        return tuple(neighbors)
    
    @staticmethod
    @lru_cache(maxsize=None)
    def get_neighbor_positions(position: tuple, rows, cols) -> tuple:
        """Get the positions of the 8 neighbors of a cell."""
        i, j = position
        return (i + RainbowLife.dx) % rows, (j + RainbowLife.dy) % cols
    
    def get_state_color(self, state):
        return self.color_map.get(state, (255, 255, 255))  # Default to white if state is undefined

    def get_state_colors(self, grid: np.ndarray):
        return np.array([[self.get_state_color(state) for state in row] for row in grid])

class RainbowLife2(RainbowLife):
    """RainbowLife with a different set of principles than the first one.
    Notes:
    - The equality_threshold parameter allows for a more flexible definition of "sameness".
    """
    
    def __init__(self, equality_threshold=0, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.equality_threshold = equality_threshold

    def get_next_state(self, state: int, neighbors: tuple):
        # If I'm not the same color as any of my neighbors, I choose the least common color among them
        # "Ideas spread slowly, but they do spread."
        if not self._equal_to_any(state, neighbors, self.equality_threshold, self.num_states):
            return min(set(neighbors), key=neighbors.count)
        
        # If I'm the same color as all my neighbors, I change color
        # "Nonconformity is the only legitimate form of rebellion."
        if self._equal_to_all(state, neighbors, self.equality_threshold, self.num_states):
            return (state + self.equality_threshold) % self.num_states
        
        # Otherwise, I choose the average color of my neighbors
        # "The truth is in the middle."
        return self._average_state(neighbors) % self.num_states
        

    def __repr__(self):
        return f"RainbowLife2(num_states={self.num_states}, equality_threshold={self.equality_threshold})"
    
    def __str__(self):
        return """RainbowLife2
Rules:
1. "Ideas spread slowly, but they do spread."
2. "Nonconformity is the only legitimate form of rebellion."
3. "The truth is in the middle."
"""

    @staticmethod
    @lru_cache(maxsize=2**16)
    def _get_equals(state, equality_threshold, num_states):
        """Calculate the states considered equal to the current state based on the equality_threshold."""
        equals = []
        if equality_threshold == 0 or equality_threshold == 1:
            return [state]
        for i in range(-equality_threshold, equality_threshold + 1):
            # clamp the values to the range [0, num_states) but do not wrap around the range
            if 0 <= (state + i) < num_states:
                equals.append((state + i))
            else:
                continue  # skip the wrapping around the range
        return equals
    
    @staticmethod
    @lru_cache(maxsize=2**16)
    def _equal_to_any(state, neighbors, equality_threshold, num_states):
        equals = RainbowLife2._get_equals(state, equality_threshold, num_states)
        return any(n in equals for n in neighbors)
    
    @staticmethod
    @lru_cache(maxsize=2**16)
    def _equal_to_all(state, neighbors, equality_threshold, num_states):
        equals = RainbowLife2._get_equals(state, equality_threshold, num_states)
        return all(n in equals for n in neighbors)
    
    @staticmethod
    @lru_cache(maxsize=2**16)
    def _average_state(neighbors):
        """Calculate the average state of the neighbors."""
        return sum(neighbors) // len(neighbors)
    

class RainbowLife3(RainbowLife2):
    """RainbowLife3 with a different set of principles than the first one.
    Notes:
    - The equality_threshold parameter allows for a more flexible definition of "sameness".
    - No longer sort the neighbors so we can use their relative positions.
    """
    
    def __init__(self, equality_threshold=0, *args, **kwargs):
        super().__init__(equality_threshold, *args, **kwargs)

    def get_neighbors(self, grid: np.ndarray, position: tuple) -> tuple:
        """Extract the 8 neighbors of a cell."""
        rows, cols = grid.shape
        nx, ny = self.get_neighbor_positions(position, rows, cols)
        neighbors = grid[nx, ny]
        return tuple(neighbors)
    
    def get_next_state(self, state: int, neighbors: tuple):
        pass