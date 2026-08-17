import mido
import time
import serial
import threading
from queue import Queue

# CONFIG
MIDI_FILE = "tool.mid"

SERIAL_MEGA = "COM3"   # fretting
SERIAL_UNO  = "COM4"   # rack + pluck

BAUD = 115200

LOOKAHEAD = 0.06
RACK_PRELOAD = 0.035   # time before pluck
PLUCK_LATENCY = 0.010

stop_flag = False

# NOTE MAP
NOTE_MAP = {
    40:1, 42:2, 43:3, 45:4, 47:5, 48:6, 50:7
}

# SERIAL 

mega = serial.Serial(SERIAL_MEGA, BAUD, timeout=1)
uno  = serial.Serial(SERIAL_UNO,  BAUD, timeout=1)

time.sleep(2)

event_queue = Queue()

# KILLSWITCH 
def killswitch():
    global stop_flag
    input("Press ENTER to stop\n")
    stop_flag = True
    mega.write(b"STOP\n")
    uno.write(b"STOP\n")

threading.Thread(target=killswitch, daemon=True).start()

# BUILD EVENTS
def build_events(mid):

    events = []
    current_time = 0

    for msg in mid:

        current_time += msg.time

        if msg.type == "note_on" and msg.velocity > 0:

            if msg.note not in NOTE_MAP:

                continue

            events.append({

                "time": current_time,
                "note": msg.note,
                "vel": msg.velocity,
                "type": "on"
            })

        if msg.type == "note_off" or (msg.type == "note_on" and msg.velocity == 0):

            if msg.note not in NOTE_MAP:
                continue

            events.append({

                "time": current_time,
                "note": msg.note,
                "type": "off"
            })

    return sorted(events, key=lambda e: e["time"])

# === PLAYER ===

def player():

    while not stop_flag:

        try:

            e = event_queue.get(timeout=0.1)
        except:
            continue

        if e["type"] == "on":

            sol = NOTE_MAP[e["note"]]

            # 1. FRET (MEGA)
            mega.write(f"FRET:{sol}\n".encode())

            # 2. PRELOAD RACK BEFORE HIT
            uno.write(b"RACK_DOWN\n")

            time.sleep(RACK_PRELOAD)

            # 3. PLUCK WITH VELOCITY
            strength = int(60 + (e["vel"]/127)*195)
            uno.write(f"PLUCK:{strength}\n".encode())

        elif e["type"] == "off":

            mega.write(b"RELEASE\n")

            uno.write(b"RACK_UP\n")

threading.Thread(target=player, daemon=True).start()

# LOAD MIDI
mid = mido.MidiFile(MIDI_FILE)
events = build_events(mid)

# PLAYBACK ENGINE
start = time.perf_counter()
i = 0

while i < len(events) and not stop_flag:

    now = time.perf_counter() - start

    while i < len(events) and events[i]["time"] <= now + LOOKAHEAD:

        event_queue.put(events[i])
        i += 1

    time.sleep(0.001)

# HARD STOP
mega.write(b"STOP\n")
uno.write(b"STOP\n")

print("Playback finished")
