import json
import time
import threading
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI(title="Smart Fan Controller API")

class Fan:
    def __init__(self):
        self.speed = 1
        self.is_on = False

    def turn_on(self):
        if self.is_on:
            return "Fan is already ON."
        self.is_on = True
        return "Fan has turned on."

    def increase_speed(self):
        if not self.is_on:
            return "Please turn on the fan first."
        if self.speed < 5:
            self.speed += 1
            return f"Fan speed is {self.speed}"
        return "Fan is already at maximum speed."

    def decrease_speed(self):
        if not self.is_on:
            return "Please turn on the fan first."
        if self.speed > 1:
            self.speed -= 1
            return f"Fan speed is {self.speed}"
        return "Fan is already at minimum speed."

    def turn_off(self):
        if not self.is_on:
            return "Fan is already OFF."
        self.is_on = False
        self.speed = 1
        return "Fan has turned off. Speed reset to 1."

    def show_status(self):
        if self.is_on:
            return f"Fan is ON | Speed: {self.speed}"
        return "Fan is OFF | Speed: 1"

    def auto_off(self, seconds):
        time.sleep(seconds)
        if self.is_on:
            self.turn_off()
            message = "Timer finished. Fan has turned off."
            messages.append(message)
            save_data()

fan = Fan()
messages = []

def save_data():
    fan_info = {
        "speed": fan.speed,
        "is_on": fan.is_on,
        "actions": messages
    }
    try:
        with open("fan.json", "w") as file:
            json.dump(fan_info, file, indent=4)
    except Exception:
        pass

# --- API Endpoints ---

@app.get("/", response_class=HTMLResponse)
def read_root():
    with open("templates/index.html", "r") as file:
        return file.read()

@app.post("/turn-on")
def web_turn_on():
    msg = fan.turn_on()
    messages.append(msg)
    save_data()
    return {"status": msg}

@app.post("/increase-speed")
def web_increase_speed():
    msg = fan.increase_speed()
    messages.append(msg)
    save_data()
    return {"status": msg}

@app.post("/decrease-speed")
def web_decrease_speed():
    msg = fan.decrease_speed()
    messages.append(msg)
    save_data()
    return {"status": msg}

@app.post("/turn-off")
def web_turn_off():
    msg = fan.turn_off()
    messages.append(msg)
    save_data()
    return {"status": msg}

@app.get("/status")
def web_status():
    return {"status": fan.show_status()}

@app.post("/set-timer")
def web_set_timer(minutes: float):
    if not fan.is_on:
        return {"error": "Please turn on the fan first."}
    if minutes <= 0:
        return {"error": "Timer must be greater than 0 minutes."}
    
    seconds = minutes * 60.0
    msg = f"Fan will turn off after {minutes} minutes."
    messages.append(msg)
    save_data()
    
    timer = threading.Thread(target=fan.auto_off, args=(seconds,))
    timer.daemon = True
    timer.start()
    return {"status": msg}

@app.get("/history")
def web_history():
    return {"action_history": messages}
