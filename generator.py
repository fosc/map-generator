from copy import deepcopy
import random
from collections import Counter
import tcod as libtcod


class CellGrid:
    def __init__(self, width, height):
        self.height = height
        self.width = width
        self.cells = [[int(random.random() + 0.5) for x in range(width)] for y in range(height)]

    def get_cell(self, x, y):
        try:
            return self.cells[y][x]
        except IndexError as e:
            return None

    def set_cell(self, x, y, val):
        try:
            self.cells[y][x] = val
        except IndexError:
            raise Warning(f'index {x} {y} out of range')


class CellularAutomaton:
    def __init__(self, width, height, edge_default=1):
        self.edge_default = edge_default
        self.cells = CellGrid(width, height)

    def next_generation(self, neighbor_counts):
        raise NotImplementedError("Abstract method: subclass must implement.")

    def get_neighborhood(self, x, y):
        neighborhood = list()
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if not (dy == 0 and dx == 0):
                    nbr = self.cells.get_cell(x + dx, y + dy)
                    if nbr is not None:
                        neighborhood.append(nbr)
                    else:
                        neighborhood.append(self.edge_default)
        return neighborhood

    def neighbor_profile(self, x, y):
        return Counter(self.get_neighborhood(x, y))

    def next_state(self, x, y):
        return self.next_generation(self.neighbor_profile(x, y))

    def advance_state(self):
        next_state = deepcopy(self.cells)
        for x in range(self.cells.width):
            for y in range(self.cells.height):
                next_state.set_cell(x, y, self.next_state(x, y))
        self.cells = next_state


class AutomatonObserver:
    def __init__(self, state, mapping):
        self.mapping = mapping
        self.state = state
        self.con = libtcod.console_new(self.state.width, self.state.height)
        libtcod.console_init_root(self.state.width, self.state.height, 'libtcod tutorial', False)
        self.show()

    def show(self):
        key = libtcod.Key()
        mouse = libtcod.Mouse()
        while not libtcod.console_is_window_closed():
            for y in range(self.state.height):
                for x in range(self.state.width):
                    color = self.mapping[self.state.get_cell(x, y)]
                    libtcod.console_set_char_background(self.con, x, y, color, libtcod.BKGND_SET)

            libtcod.console_blit(self.con, 0, 0, self.con.width, self.con.height, 0, 0, 0)
            libtcod.console_flush()  # present everything on screen

            libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS, key, mouse)
            if key.vk == libtcod.KEY_ESCAPE:
                return True


if __name__ == '__main__':
    mapping = {0: libtcod.white, 1: libtcod.black}
    aut = CellularAutomaton(50, 50)
    observer = AutomatonObserver(aut.cells, mapping)
