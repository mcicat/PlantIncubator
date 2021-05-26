#tutorial used: https://www.youtube.com/watch?v=Z1RJmh_OqeA
#!/usr/bin/env python3

from os import name, stat, path, remove
from flask import Flask, render_template, url_for, flash, request
from werkzeug.utils import redirect
import json 
from  datetime import date, datetime
import threading 
import time as t 
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

class Timer: 
    class TimerThread:         
        thread_obj = None
        def run_loop(self, time_start, time_stop):
            while (self.run_thread):

                time = datetime.now()
                time_start_obj = datetime.strptime(time_start,"%H:%M")
                time_stop_obj = datetime.strptime(time_stop,"%H:%M")

                if (time.hour == time_start_obj.hour and time.minute == time_start_obj.minute):
                    led.change_status(True)
                elif (time.hour == time_stop_obj.hour and time.minute == time_stop_obj.minute):
                    led.change_status(False)
                
                t.sleep(60) 

        def run_thread_timer(self, time_start, time_stop):
            self.run_thread = True
            self.thread_obj = threading.Thread(target=self.run_loop, name = "Thread timer", args=[time_start, time_stop])
            self.thread_obj.start()

        
        def stop_thread_timer(self):
            if (self.thread_obj is not None):
                self.run_thread = False
                self.thread_obj.join()
                self.thread_obj = None

    CONFIG_FILENAME = "config.json"
    time_start=""
    time_stop=""
    thread = TimerThread()

    def __init__ (self):
        if path.exists(self.CONFIG_FILENAME):
            self.status = "Timer is set"

            if (self.time_start is "" or self.time_stop is ""):
                with open(self.CONFIG_FILENAME,'r') as f:
                    config = json.load(f)['config']
                    self.time_start = config['timer_start']
                    self.time_stop = config['timer_stop']

            self.thread.run_thread_timer(self.time_start, self.time_stop)
        else:
            self.status = "Timer not set."
    def save_timer_config(self, timer_start, timer_stop): 
        if (timer_start != "" and timer_stop !=  "" and timer_stop != timer_start) :
            config = {}
            config['config'] = {'timer_start': timer_start, 'timer_stop' : timer_stop}
            with open(self.CONFIG_FILENAME, 'w') as f:
                json.dump(config, f)

            self.status = f"Timer created successfully ({timer_start}-{timer_stop})"

            self.time_start = timer_start
            self.time_stop = timer_stop 

            self.thread.run_thread_timer(timer_start, timer_stop)
        else:
            self.status = "Timer creation failed."
        
    def discard_timer_config(self):
        if path.exists(self.CONFIG_FILENAME):
            self.thread.stop_thread_timer()
            remove(self.CONFIG_FILENAME)
            self.status = "Timer discarded successfully"

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
    app.run(debug=True, host="0.0.0.0", use_reloader=False)



