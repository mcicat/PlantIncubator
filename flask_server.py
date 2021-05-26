#tutorial used: https://www.youtube.com/watch?v=Z1RJmh_OqeA
#!/usr/bin/env python3

from os import stat, path, remove
from flask import Flask, render_template, url_for, flash, request
from werkzeug.utils import redirect
import json 

# import RPi.GPIO as GPIO 

#LED CLASS

class Led:
    def __init__(self, pin):
        self.pin = pin

        # GPIO.setmode(GPIO.BOARD)   
        # GPIO.setup(self.pin, GPIO.OUT, initial=GPIO.LOW)

    def change_status(self, status):
        if (status):
            print("Turning led on...")
            # GPIO.output(self.pin, GPIO.HIGH) # Turn on
        else:
            print("Turning led off...")
            # GPIO.output(self.pin, GPIO.LOW) # Turn off

class Timer: 
    CONFIG_FILENAME = "config.json"
    
    def __init__ (self):
        if path.exists(self.CONFIG_FILENAME):
            self.status = "Timer is set"
        else:
            self.status = "Timer not set."

    def save_timer_config(self, timer_start, timer_stop): 
        if (timer_start != "" and timer_stop !=  "" and timer_stop != timer_start) :
            config = {}
            config['config'] = {'timer_start': timer_start, 'timer_stop' : timer_stop}
            with open(self.CONFIG_FILENAME, 'w') as f:
                json.dump(config, f)

            self.status = f"Timer created successfully ({timer_start}-{timer_stop})"
        else:
            self.status = "Timer creation failed."
        
    def discard_timer_config(self):
        if path.exists(self.CONFIG_FILENAME):
            self.status = "Timer discarded successfully"
            remove(self.CONFIG_FILENAME)
        else:
            self.status = "Timer was not set. Skipping action..."
        
    
    
#GLOBAL CLASSES 

app = Flask(__name__)
led = Led(pin=8)
timer = Timer()


config_filename = 'config.conf'
#ROUTES

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html', timer_log=timer.status)

@app.route('/led_on', methods=['GET', 'POST'])
def led_on():
    if request.method == 'POST':
        led.change_status(status=True)
        
    return render_template('index.html', timer_log=timer.status)


@app.route('/led_off', methods=['GET', 'POST'])
def led_off():
    if request.method == 'POST':
        led.change_status(status=False)
        
    return render_template('index.html', timer_log=timer.status)

@app.route('/timer_on', methods=['POST'])
def timer_on():
    if request.method == 'POST':
        time_start = request.form.get("timer_start")
        time_stop = request.form.get("timer_stop")
    
        
        timer.save_timer_config(timer_start = time_start,timer_stop=time_stop)

    return render_template('index.html', timer_log=timer.status)

@app.route('/timer_off', methods=['POST'])
def timer_off():
    if request.method == 'POST':
        timer.discard_timer_config()
        
    return render_template('index.html', timer_log=timer.status)

#MAIN 

if __name__ == "__main__":    
    app.run(debug=True, host="0.0.0.0")



