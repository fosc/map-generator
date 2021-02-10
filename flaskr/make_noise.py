from noise import pnoise2
import json


def noise_grid(width, height):
    result = list()
    for y in range(height):
        result.append(list())
        for x in range(width):
            nx = (x/width - 0.5)*2
            ny = (y/height - 0.5)*2
            n_val = (pnoise2(nx, ny, repeatx=1, repeaty=1, base=5) + 1) / 2  # between 0 and 1
            n_val = int(n_val*10)/10  # floor to nearest 0.1
            result[y].append(n_val)
    return result


def to_json(width, height):
    ng = noise_grid(width, height)
    color_map = {0.0: '#000000', 0.1: '#242424', 0.2: '#404040', 0.3: '#626262', 0.4: '#737373', 0.5: '#858585',
                 0.6: '#a1a1a1', 0.7: '#bdbdbd', 0.8: '#d1d1d1', 0.9: '#e6e6e6', 1.0: '#ffffff'}
    dump_dict = {'num_rows': height, 'num_cols': width, 'color_map': color_map, 'data': list()}
    for y in range(height):
        for x in range(width):
            dump_dict['data'].append({'x': x, 'y': y, 'val': str(ng[y][x])})
    print(json.dumps(dump_dict))
    return json.dumps(dump_dict)

if __name__ == "__main__":
    m = 1000
    n = noise_grid(m, m)
    for y in range(m):
        print(f'{max(n[y])},{min(n[y])}')