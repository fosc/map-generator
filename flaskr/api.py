from flask import Flask, render_template
from flaskr.generator import CaveGenerator
import flaskr.make_noise
app = Flask(__name__)


@app.route('/home/<data_source>')
def get_page(data_source):
    return render_template('test.html', data_source=data_source)


@app.route('/cave')
def get_cave():
    """returns an implementation of the MapData interface"""
    cave_gen = CaveGenerator(100, 100, density=0.59)
    for i in range(3):
        cave_gen.advance_state()

    return cave_gen.cells.to_json()


@app.route('/noise')
def get_noise():
    """returns an implementation of the MapData interface"""
    return flaskr.make_noise.to_json(100, 100)
