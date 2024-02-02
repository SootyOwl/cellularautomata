class Rules:
    def apply(self, current_state, alive_neighbors):
        raise NotImplementedError("This method should be implemented by subclasses.")
    
    def get_state_color(self, state):
        raise NotImplementedError("This method should provide the color representation for a given state.")

class GenericRules(Rules):
    def __init__(self):
        self.color_map = {
            0: (0, 0, 0),       # Dead / Empty
            1: (0, 255, 0),     # Alive / State 1
            # Add more states as needed
        }
    
    def apply(self, current_state, alive_neighbors):
        # Implement the logic to update the state based on the current state and alive neighbors
        # This is a placeholder example; customize it as needed
        if current_state == 0 and alive_neighbors == 3:
            return 1  # Transition to alive state
        elif current_state == 1 and (alive_neighbors < 2 or alive_neighbors > 3):
            return 0  # Transition to dead state
        else:
            return current_state  # Remain in the current state

    def get_state_color(self, state):
        return self.color_map.get(state, (255, 255, 255))  # Default to white if state is undefined


class ConwayRules(GenericRules):
    def apply(self, current_state, alive_neighbors):
        if current_state == 1 and (alive_neighbors < 2 or alive_neighbors > 3):
            return 0
        elif current_state == 0 and alive_neighbors == 3:
            return 1
        else:
            return current_state


class HighLifeRules(GenericRules):
    def apply(self, current_state, alive_neighbors):
        if current_state == 1 and (alive_neighbors < 2 or alive_neighbors > 3):
            return 0
        elif current_state == 0 and (alive_neighbors == 3 or alive_neighbors == 6):
            return 1
        else:
            return current_state
