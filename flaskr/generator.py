from copy import deepcopy
import random
from collections import Counter
import tcod as libtcod
import json


class CellGrid:
    """
    A wrapper for a list of lists.
    Initialize each list element randomly to 0 (with P=1-density) or 1 (with P=density)
    """
    def __init__(self, width, height, density):
        self.height = height
        self.width = width
        self.cells = [[int(random.random() + density) for x in range(width)] for y in range(height)]

    def get_cell(self, x, y):
        try:
            return self.cells[y][x]
        except IndexError:
            return None

    def set_cell(self, x, y, val):
        try:
            self.cells[y][x] = val
        except IndexError:
            raise Warning(f'index {x} {y} out of range')

    def to_json(self):
        dump_dict = {
            'num_rows': self.height,
            'num_cols': self.width,
            'data': list()
                     }
        for x in range(self.width):
            for y in range(self.height):
                dump_dict['data'].append({'x': x, 'y': y, 'val':self.get_cell(x, y)})

        return json.dumps(dump_dict)


class CellularAutomaton:
    """
    Abstract class for 2D cellular Automaton.
    Can advance to next state and return a CellGrid object.
    """
    def __init__(self, width, height, density=0.5, edge_default=1):
        self._edge_default = edge_default
        self.cells = CellGrid(width, height, density=density)

    def next_generation(self, neighbor_counts: dict, state: int) -> int:
        raise NotImplementedError("Abstract method: subclass must implement.")

    def _get_neighborhood(self, x, y):
        neighborhood = list()
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if not (dy == 0 and dx == 0):
                    nbr = self.cells.get_cell(x + dx, y + dy)
                    if nbr is not None:
                        neighborhood.append(nbr)
                    else:
                        neighborhood.append(self._edge_default)
        return neighborhood

    def _neighbor_profile(self, x, y):
        return Counter(self._get_neighborhood(x, y))

    def _next_state(self, x, y):
        return self.next_generation(self._neighbor_profile(x, y), self.cells.get_cell(x, y))

    def advance_state(self):
        next_state = deepcopy(self.cells)
        for x in range(self.cells.width):
            for y in range(self.cells.height):
                next_state.set_cell(x, y, self._next_state(x, y))
        self.cells = next_state


class CaveGenerator(CellularAutomaton):
    def next_generation(self, neighbor_counts, state):
        if neighbor_counts[1] > 4:
            return 1
        return 0


class ConwayAutomaton(CellularAutomaton):
    def next_generation(self, neighbor_counts, state):
        if state == 1 and neighbor_counts[1] in (2,3):
            return 1
        if state == 0 and neighbor_counts[1] == 3:
            return 1
        return 0


class GridView:
    """
    Display a CellGrid object (self._state) using the tcod library.
    Colours for cells determined by the dict self._mapping.
    """
    TILE_SET = libtcod.tileset.load_tilesheet('img.png', 32, 8, libtcod.tileset.CHARMAP_TCOD)

    def __init__(self, state: CellGrid, mapping: dict, pix_size=800):
        self._mapping = mapping
        self._state = state
        self._context = libtcod.context.new_window(width=pix_size, height=pix_size, tileset=self.TILE_SET)
        self._console = self._context.new_console(min_columns=self.state.width, min_rows=self.state.height)
        self._show()

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, new_state):
        self._state = new_state
        self._show()

    def _show(self):
        self._console.clear()
        for y in range(self.state.height):
            for x in range(self.state.width):
                color = self._mapping[self.state.get_cell(x, y)]
                self._console.print(x, y, ' ', bg=color)
        self._context.present(self._console)


if __name__ == '__main__':
    MAPPING = {0: (255, 255, 255), 1: (0, 0, 0)}
    aut = CaveGenerator(100, 100, density=0.59)
    observer = GridView(aut.cells, MAPPING)
    input("hit enter")
    for i in range(5):
        aut.advance_state()
        observer.state = aut.cells
        inpt = input("hit enter")
        if inpt.strip() == 's':
            aut.cells.to_json('caves1.json')

