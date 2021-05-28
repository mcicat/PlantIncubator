BOARD = 1
OUT = 1
IN = 1
LOW = 0
HIGH = 1


def setmode(a):
   print(f"Setting mode [{a}]...")
def setup(pin, mode, initial):
   print(f"Setting pin [{pin},{mode},{initial}]...")
def output(a, b):
   print(f"Outptuting [{a},{b}]...")
def cleanup():
   print(f"Cleaning up...")
def setwarnings(flag):
   print(f"Settings warning [{flag}]")