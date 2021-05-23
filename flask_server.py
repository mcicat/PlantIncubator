#tutorial used: https://www.youtube.com/watch?v=Z1RJmh_OqeA

from os import stat
from flask import Flask, render_template, url_for, flash, request
from werkzeug.utils import redirect

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@app.route('/led_on', methods=['GET', 'POST'])
def led_on():
    if request.method == 'POST':
        led(status=True)
        
    return render_template('index.html')

@app.route('/led_off', methods=['GET', 'POST'])
def led_off():
    if request.method == 'POST':
        led(status=True)
        
    return render_template('index.html')


def led(status):
    if (status):
        print("LED ON")
    else:
        print("LED OFF")

if __name__ == "__main__":
    app.run(debug=True)


