from noise import pnoise2
import json
from random import randint

OCEAN_BLUE = '#028bad'


def get_noise_value(nx, ny, freq, base):
    raw = pnoise2(freq*nx, freq*ny, repeatx=freq+1, repeaty=freq+1, base=base)  # this is between -1 and 1
    return (raw + 1) / 2  # between 0 and 1


def coord_transform(x, max_x):
    """Transform coordinate x in [0, max_x] to a value in [-1, 1]"""
    return (x/max_x - 0.5)*2


def noise_grid(width, height, freq, dec_places=2):
    base = randint(0, 20)  # we don't want the same thing every time
    result = list()
    for y in range(height):
        result.append(list())
        for x in range(width):
            nx = coord_transform(x, width)
            ny = coord_transform(y, height)
            n_val = get_noise_value(nx, ny, freq, base)
            n_val = round(n_val, dec_places)
            result[y].append(n_val)
    return result


def hex_string(int_val):
    str_val = hex(int_val).replace('0x', '')
    if len(str_val) < 2:
        return '0' + str_val
    return str_val


def css_greyscale(int_val):
    return '#'+hex_string(int_val)*3


def color_mapping(num_dec_place, water_level=0.473):
    resolution = 10**num_dec_place
    shades = [x/resolution for x in range(resolution + 1)]
    mapping = dict()
    for shade in shades:
        if shade < water_level:
            mapping[shade] = OCEAN_BLUE
        else:
            mapping[shade] = css_greyscale(int(255*shade))
    return mapping


def to_json(width, height, freq, dec_places=3):
    ng = noise_grid(width, height, freq, dec_places)
    dump_dict = {'num_rows': height, 'num_cols': width, 'color_map': color_mapping(dec_places), 'data': list()}
    for y in range(height):
        for x in range(width):
            dump_dict['data'].append({'x': x, 'y': y, 'val': str(ng[y][x])})
    return json.dumps(dump_dict)

if __name__ == "__main__":
    print(color_mapping(2))