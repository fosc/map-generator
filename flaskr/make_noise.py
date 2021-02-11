"""
Create a JSON string with the MapBuilder class. This JSON object is a instance of Map Data:
1. num_rows --> int
2. num_cols --> int
3. data --> [...{x: 9, y: 45, val: '0.x' }...]
4. color_map --> {...,0.463: '#404040',...}
"""
import json
from configparser import ConfigParser
from noise import pnoise2

OCEAN_BLUE = '#028bad'
CONFIG_FILE = '../config.ini'
CONFIG_READER = ConfigParser()
CONFIG_READER.read(CONFIG_FILE)


def hex_string(int_val):
    """return a string of length 2 representing the hex value of int_value"""
    str_val = hex(int_val).replace('0x', '')
    if len(str_val) < 2:
        return '0' + str_val
    return str_val


def css_greyscale(int_val):
    """given an integer return a greyscale css color string."""
    return '#'+hex_string(int_val)*3


def color_mapping(config):
    try:
        dec_places = int(CONFIG_READER[config]['decimal_places'])
        water_level = float(CONFIG_READER[config]['water_level'])
    except KeyError:
        raise Exception(f'{CONFIG_FILE} section {config} is missing required value(s).')

    resolution = 10**dec_places
    shades = [x/resolution for x in range(resolution + 1)]
    mapping = dict()
    for shade in shades:
        if shade < water_level:
            mapping[shade] = OCEAN_BLUE
        else:
            mapping[shade] = css_greyscale(int(255*shade))
    return mapping


class Grid:
    def __init__(self, width, height):
        self._grid = list()
        for y in range(height):
            self._grid.append(list())
            for x in range(width):
                self._grid[y].append(0)
        self.width = width
        self.height = height

    def set(self, x, y, val):
        self._grid[y][x] = val

    def get(self, x, y):
        return self._grid[y][x]

    def to_dict(self):
        dump_dict = {'num_rows': self.height, 'num_cols': self.width, 'data': list()}
        for y in range(self.height):
            for x in range(self.width):
                dump_dict['data'].append({'x': x, 'y': y, 'val': str(self.get(x, y))})
        return dump_dict


class NoiseGrid(Grid):
    def __init__(self, width, height, config='Default'):
        super().__init__(width, height)
        try:
            self.freq = float(CONFIG_READER[config]['frequency'])
            self.profile = json.loads(CONFIG_READER[config]['profile'])
            self.base = int(CONFIG_READER[config]['base'])
            self.dec_places = int(CONFIG_READER[config]['decimal_places'])
        except KeyError:
            raise Exception(f'{CONFIG_FILE} section {config} is missing required value(s).')

        for y in range(self.height):
            for x in range(self.width):
                self.set_layered_noise_value(x, y)

    def get_raw_noise_value(self, n_x, n_y, freq):
        """Return a float between 0 and 1 of perlin noise"""
        raw = pnoise2(freq*n_x, freq*n_y, repeatx=freq+1, repeaty=freq+1, base=self.base)
        return (raw + 1) / 2  # convert [-1, 1] -> [0, 1]

    def set_layered_noise_value(self, x, y):
        """Set grid value at x, y to a value of layered frequencies of perlin noise"""
        def coord_transform(i, max_i):
            """Transform coordinate i in [0, max_i] to a value in [-1, 1]"""
            return (i / max_i - 0.5) * 2
        n_x = coord_transform(x, self.width)
        n_y = coord_transform(y, self.height)
        n_val = 0
        for mode in self.profile:
            n_val += (1 / mode) * self.get_raw_noise_value(n_x, n_y, mode * self.freq)
        n_val = n_val / sum(map(lambda i: i ** -1, self.profile))
        n_val = round(n_val, self.dec_places)
        self.set(x, y, n_val)


class MapBuilder:
    def __init__(self, width, height, config='Default'):
        self.noise_grid = NoiseGrid(width, height, config)
        self.color_map = color_mapping(config)

    def map_data(self):
        dump_dict = self.noise_grid.to_dict()
        dump_dict['color_map'] = self.color_map
        return json.dumps(dump_dict)
