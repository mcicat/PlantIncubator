#tutorial used: https://www.youtube.com/watch?v=Z1RJmh_OqeA

from os import stat
from flask import Flask, render_template, url_for, flash, request
from werkzeug.utils import redirect

import RPi.GPIO as GPIO 

#LED CLASS

class Led:
    def __init__(self, pin):
        self.pin = pin

        GPIO.setmode(GPIO.BOARD)   
        GPIO.setup(self.pin, GPIO.OUT, initial=GPIO.LOW)

    def change_status(self, status):
        if (status):
            print("Turning led on...")
            GPIO.output(self.pin, GPIO.HIGH) # Turn on
        else:
            print("Turning led off...")
            GPIO.output(self.pin, GPIO.LOW) # Turn off

#GLOBAL CLASSES 

app = Flask(__name__)
led = Led(pin=8)


#ROUTES

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@app.route('/led_on', methods=['GET', 'POST'])
def led_on():
    if request.method == 'POST':
        led.change_status(status=True)
        
    return render_template('index.html')

@app.route('/led_off', methods=['GET', 'POST'])
def led_off():
    if request.method == 'POST':
        led.change_status(status=False)
        
    return render_template('index.html')


#MAIN 

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0")



