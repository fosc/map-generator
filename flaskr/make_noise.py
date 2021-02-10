from noise import pnoise2
import json
from random import randint


def noise_grid(width, height, dec_places):
    base = randint(0, 100)  # we don't want the same thing every time
    result = list()
    for y in range(height):
        result.append(list())
        for x in range(width):
            nx = (x/width - 0.5)*2
            ny = (y/height - 0.5)*2
            n_val = (pnoise2(nx, ny, repeatx=1, repeaty=1, base=base) + 1) / 2  # between 0 and 1
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


def color_mapping(num_dec_place):
    resolution = 10**num_dec_place
    shades = [x/resolution for x in range(resolution + 1)]
    mapping = dict()
    for shade in shades:
        mapping[shade] = css_greyscale(int(255*shade))
    return mapping


def to_json(width, height, dec_places=2):
    ng = noise_grid(width, height, dec_places)
    dump_dict = {'num_rows': height, 'num_cols': width, 'color_map': color_mapping(dec_places), 'data': list()}
    for y in range(height):
        for x in range(width):
            dump_dict['data'].append({'x': x, 'y': y, 'val': str(ng[y][x])})
    return json.dumps(dump_dict)

if __name__ == "__main__":
    print(color_mapping(2))