from time import sleep
from copy import deepcopy
import random
from collections import Counter
import tcod as libtcod


class CellGrid:
    def __init__(self, width, height, density):
        self.height = height
        self.width = width
        self.cells = [[int(random.random() + density) for x in range(width)] for y in range(height)]

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
    def __init__(self, width, height, density=0.5, edge_default=1):
        self.edge_default = edge_default
        self.cells = CellGrid(width, height, density=density)

    def next_generation(self, neighbor_counts: dict, state:int) -> int:
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
        return self.next_generation(self.neighbor_profile(x, y), self.cells.get_cell(x, y))

    def advance_state(self):
        next_state = deepcopy(self.cells)
        for x in range(self.cells.width):
            for y in range(self.cells.height):
                next_state.set_cell(x, y, self.next_state(x, y))
        self.cells = next_state


class TestAutomaton(CellularAutomaton):
    def next_generation(self, neighbor_counts, state):
        if neighbor_counts[1] > 4:
            return 1
        else:
            return 0


class ConwayAutomaton(CellularAutomaton):
    def next_generation(self, neighbor_counts, state):
        if state == 1 and neighbor_counts[1] in (2,3):
            return 1
        if state == 0 and neighbor_counts[1] == 3:
            return 1
        return 0

class AutomatonObserver:

    tileset = libtcod.tileset.load_tilesheet(
        "img.png", 32, 8, libtcod.tileset.CHARMAP_TCOD,
    )
    def __init__(self, state, mapping):
        self.mapping = mapping
        self.refresh = True
        self._state = state
        self.pix_size =3
        self.context = libtcod.context.new_window(width=self.pix_size*self.state.width,
                                                  height=self.pix_size*self.state.height,
                                                  tileset=self.tileset)
        self.con = self.context.new_console( min_columns=self.state.width,
                                            min_rows=self.state.height,
                                            magnification=0.9)

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, new_state):
        self._state = new_state
        self.show()

    def show(self):
        self.con.clear()
        for y in range(self.state.height):
            for x in range(self.state.width):
                color = self.mapping[self.state.get_cell(x, y)]
                self.con.print(x, y, ' ', bg=color)
        self.context.present(self.con)


if __name__ == '__main__':
    mapping = {0: (255,255,255), 1:(0,0,0)}
    aut = TestAutomaton(500, 500, edge_default=1, density=0.6)
    observer = AutomatonObserver(aut.cells, mapping)
    for i in range(10):
        aut.advance_state()
        observer.state = aut.cells
        input("hit enter")
