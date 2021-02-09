from flask import Flask, render_template
from flaskr.generator import CaveGenerator
app = Flask(__name__)


@app.route('/home')
def get_page():
    return render_template('test.html')

@app.route('/cave')
def get_cave():
    cave_gen = CaveGenerator(100, 100, density=0.59)
    for i in range(3):
        cave_gen.advance_state()

    return cave_gen.cells.to_json()
