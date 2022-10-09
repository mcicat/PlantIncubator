#tutorial used: https://www.youtube.com/watch?v=Z1RJmh_OqeA
#!/usr/bin/env python3

from os import name, stat, path, remove
from flask import Flask, render_template, url_for, flash, request, escape
from werkzeug.utils import redirect
import json 
from  datetime import date, datetime
import threading 
import time as t 
import RPi.GPIO as GPIO
from abc import ABC, abstractmethod
import typing


#LED CLASS

class GpioElement:
    status = False
    def __init__(self, pin):
        self.pin = pin

    @abstractmethod
    def change_status(self, status):
        pass

class Led(GpioElement):
    def __init__(self, pin):
        GpioElement.__init__(self, pin)
        GPIO.setup(self.pin, GPIO.OUT, initial=GPIO.LOW)

    def change_status(self, status):
        if (status):
            print("Turning led on...")
            GPIO.output(self.pin, GPIO.HIGH) # Turn on
        else:
            print("Turning led off...")
            GPIO.output(self.pin, GPIO.LOW) # Turn off
        self.status = status

class Pump(GpioElement):
    def __init__(self, pin):
        GpioElement.__init__(self, pin)
        GPIO.setup(self.pin, GPIO.OUT, initial=GPIO.HIGH)

    def change_status(self, status):
        if (status):
            print("Turning pump on...")
            GPIO.output(self.pin, GPIO.LOW) # Turn on
        else:
            print("Turning pump off...")
            GPIO.output(self.pin, GPIO.HIGH) # Turn off
        self.status = status

class Timer: 
    class TimerThread:   
        lock = threading.Lock()
        thread_obj = None
        gpio_elements_configurations = []
        
        def set_timers(self, gpio_elements_configurations : list[tuple[GpioElement, str, str]]):
            self.lock.acquire()
            self.gpio_elements_configurations = gpio_elements_configurations
            self.lock.release()

        def run_loop(self) -> None:

            print("Initalizing loop.")
                        
            while (self.run_thread):
                
                self.lock.acquire()
                for (gpio_element, time_start, time_stop) in self.gpio_elements_configurations:
                    time = datetime.now()
                    time_start_obj = datetime.strptime(time_start,"%H:%M")
                    time_stop_obj = datetime.strptime(time_stop,"%H:%M")

                    if time.hour == time_start_obj.hour and time.minute == time_start_obj.minute and not gpio_element.status:
                        gpio_element.change_status(True)
                    elif time.hour == time_stop_obj.hour and time.minute == time_stop_obj.minute and gpio_element.status:
                        gpio_element.change_status(False)
                self.lock.release()
                
                t.sleep(1) 

        def run_thread_timer(self):
            self.run_thread = True
            self.thread_obj = threading.Thread(target=self.run_loop, name = "Thread timer")
            self.thread_obj.start()
        
        # def stop_thread_timer(self):
        #     if (self.thread_obj is not None):
        #         self.run_thread = False
        #         self.thread_obj.join()
        #         self.thread_obj = None

    ROOT_TAG = "config"
    CONFIG_FILENAME = "config.json"
    timers = []

    thread = TimerThread()

    def __init__ (self):
        if path.exists(self.CONFIG_FILENAME):
            self.status = "Timer is set"

            with open(self.CONFIG_FILENAME,'r') as f:
                config = json.load(f)[self.ROOT_TAG]
                for c in config:
                    gpio_element_text = c["gpio_element"]
                    timer_start = c["timer_start"]
                    timer_stop = c["timer_stop"]
                    if gpio_element_text == pump.__class__.__name__:
                        gpio_element = pump
                    elif gpio_element_text == led.__class__.__name__:
                        gpio_element = led
                    else :
                        raise(Exception("GPIO ELEMENT UNKNOWN"))
                    self.timers.append((gpio_element, timer_start, timer_stop))
        else:
            self.status = "Timer not set."

        self.thread.set_timers(self.timers)
        self.thread.run_thread_timer()
    
    def save_timer_config(self, gpio_element : GpioElement, timer_start : str, timer_stop : str): 
        if timer_start != "" and timer_stop !=  "" and timer_stop != timer_start:
            gpio_element_text = gpio_element.__class__.__name__

            if path.exists(self.CONFIG_FILENAME):
                with open(self.CONFIG_FILENAME,'r') as f:
                    config = json.load(f)
            else:
                config = {}
                config[self.ROOT_TAG] = []

            config[self.ROOT_TAG].append({"gpio_element" : gpio_element_text, "timer_start": timer_start, "timer_stop" : timer_stop})
            
            with open(self.CONFIG_FILENAME, 'w') as f:
                json.dump(config, f)

            self.status = f"Timer created successfully ({timer_start}-{timer_stop})"

            self.timers.append((gpio_element, timer_start, timer_stop))
            
            self.thread.set_timers(self.timers)
        else:
            self.status = "Timer creation failed."
        
    def discard_timer_config(self, gpio_element : GpioElement):
        if path.exists(self.CONFIG_FILENAME):

            with open(self.CONFIG_FILENAME,'r') as f:
                config = json.load(f)

            gpio_element_text = gpio_element.__class__.__name__

            timers_to_remove = []
            for c in config[self.ROOT_TAG]:
                if c["gpio_element"] == gpio_element_text:
                    timers_to_remove.append(c)
            for t in timers_to_remove:
                config[self.ROOT_TAG].remove(t)
            
            timers_to_remove = []
            for t in self.timers:
                if t[0] == gpio_element:
                    timers_to_remove.append(t)
            for t in timers_to_remove:
                self.timers.remove(t)

            with open(self.CONFIG_FILENAME, 'w') as f:
                json.dump(config, f)
                    
            self.status = "Timers discarded successfully"
        else:
            self.status = "Timer was not set. Skipping action..."

            
#GLOBAL CLASSES 

app = Flask(__name__)
led = Led(pin=8)
pump = Pump(pin=10)
timer = Timer()


config_filename = 'config.conf'
#ROUTES

def parse_time(time_start_hours:str, time_start_minutes:str, time_stop_hours:str, time_stop_minutes:str) -> tuple[str, str]:
    start_minutes = int(time_start_minutes)
    if  start_minutes <= 9:
        time_start_minutes = f"0{start_minutes}"
    
    stop_minutes = int(time_stop_minutes)
    if  stop_minutes <= 9:
        time_stop_minutes = f"0{stop_minutes}"

    start_hours = int(time_start_hours)
    if  start_hours <= 9:
        time_start_hours = f"0{start_hours}"
    
    stop_hours = int(time_stop_hours)
    if int(stop_hours) <= 9:
        time_stop_hours = f"0{stop_hours}"
    
    time_start = f"{time_start_hours}:{time_start_minutes}"
    time_stop = f"{time_stop_hours}:{time_stop_minutes}"

    return time_start, time_stop

def parse_timers(timers):
    parsed_timers = []
    for gpio, tstart, tstop  in timers:
        parsed_timers.append((gpio.__class__.__name__, tstart, tstop))

    return parsed_timers
@app.route('/', methods=['GET', 'POST'])
def index():
    d = datetime.now()
    timer_text =  f"Current server time = {d.hour:02d}:{d.minute:02d}"
    timer.status = timer_text
    return render_template('index.html', timer_log=timer.status, table_data = parse_timers(timer.timers))

# LED
@app.route('/led_on', methods=['GET', 'POST'])
def led_on():
    if request.method == 'POST':
        led.change_status(status=True)

    timer.status = "LED on..."
        
    return render_template('index.html', timer_log=timer.status, table_data = parse_timers(timer.timers))
    
@app.route('/led_off', methods=['GET', 'POST'])
def led_off():
    if request.method == 'POST':
        led.change_status(status=False)
    
    timer.status = "LED turned off..."
        
    return render_template('index.html', timer_log=timer.status, table_data = parse_timers(timer.timers))

@app.route('/led_timer_on', methods=['POST'])
def led_timer_on():
    if request.method == 'POST':
        time_start_hours = request.form.get("led_start_hours")
        time_start_minutes = request.form.get("led_start_minutes")
        time_stop_hours = request.form.get("led_stop_hours")
        time_stop_minutes = request.form.get("led_stop_minutes")
        
        time_start, time_stop = parse_time(time_start_hours, time_start_minutes, time_stop_hours, time_stop_minutes)

        timer.save_timer_config(led, timer_start = time_start, timer_stop=time_stop)

    return render_template('index.html', led_timer_log=timer.status, table_data = parse_timers(timer.timers))

@app.route('/led_timer_off', methods=['POST'])
def led_timer_off():
    if request.method == 'POST':
        timer.discard_timer_config(led)
        
    return render_template('index.html', timer_log=timer.status, table_data = parse_timers(timer.timers))

#PUMP 
@app.route('/pump_on', methods=['GET', 'POST'])
def pump_on():
    if request.method == 'POST':
        pump.change_status(status=True)

    timer.status = "Pump turned on..."
        
    return render_template('index.html', timer_log=timer.status, table_data = parse_timers(timer.timers))


@app.route('/pump_off', methods=['GET', 'POST'])
def pump_off():
    if request.method == 'POST':
        pump.change_status(status=False)
        
    timer.status = "Pump turned off..."

    return render_template('index.html', timer_log=timer.status, table_data = parse_timers(timer.timers))

@app.route('/pump_timer_on', methods=['POST'])
def pump_timer_on():
    if request.method == 'POST':
        time_start_hours = request.form.get("pump_start_hours")
        time_start_minutes = request.form.get("pump_start_minutes")
        time_stop_hours = request.form.get("pump_stop_hours")
        time_stop_minutes = request.form.get("pump_stop_minutes")
        
        time_start, time_stop = parse_time(time_start_hours, time_start_minutes, time_stop_hours, time_stop_minutes)

        timer.save_timer_config(pump, timer_start = time_start, timer_stop=time_stop)

    return render_template('index.html', timer_log=timer.status, table_data = parse_timers(timer.timers))

@app.route('/pump_timer_off', methods=['POST'])
def pump_timer_off():
    if request.method == 'POST':
        timer.discard_timer_config(pump)
        
    return render_template('index.html', timer_log=timer.status, table_data = parse_timers(timer.timers))

#MAIN 

if __name__ == "__main__":    
    GPIO.setmode(GPIO.BOARD)   
    app.run(debug=True, host="0.0.0.0", use_reloader=False)