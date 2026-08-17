import mido
import os
import serial
import serial.tools.list_ports
import time
import threading
import heapq

# CONFIG
SERIAL_BAUD = 115200
MIDI_FILE = "A7x.mid"

LOOKAHEAD_TIME = 0.10
ROLL_THRESHOLD = 0.030
FLAM_DELAY = 0.015
ENABLE_FLAMS = True

# STATE
stop_flag = False

boards = {}
board_queues = {}

# priority queue
event_queue = []

# MAP
NOTE_MAP = {
    35:[9],36:[1],40:[3,4],41:[2],42:[2],43:[6],
    45:[5],49:[7],51:[2],52:[10],53:[11]
}

# STROKES
def velocity_to_stroke(v):
    if v <= 40: return ("ghost",120,0.030)
    elif v <= 90: return ("normal",180,0.045)
    elif v <= 110: return ("accent",230,0.055)
    else: return ("rim",255,0.060)

# SERIAL THREAD
def board_worker(board_id, q):
    while not stop_flag:
        try:
            cmd = q.pop(0)
        except:
            time.sleep(0.001)
            continue

        try:
            boards[board_id].write((cmd + "\n").encode())
        except:
            pass

# SEND
def trigger_actuator(actuator, action, speed):
    board_id = (actuator - 1) // 2 + 1

    if board_id not in board_queues:
        board_queues[board_id] = []

        threading.Thread(
            target=board_worker,
            args=(board_id, board_queues[board_id]),
            daemon=True
        ).start()

    motor = "A" if actuator % 2 == 1 else "B"
    cmd = f"{motor},{action},{speed}"

    board_queues[board_id].append(cmd)

# LOAD MIDI
script_dir = os.path.dirname(os.path.abspath(__file__))
midi = mido.MidiFile(os.path.join(script_dir, MIDI_FILE))

# BUILD EVENTS
last_hit_time = {}

current_time = 0

for msg in midi:

    current_time += msg.time

    if msg.type == "note_on" and msg.velocity > 0 and msg.note in NOTE_MAP:

        stroke, speed, strike_time = velocity_to_stroke(msg.velocity)

        actuators = NOTE_MAP[msg.note]
        main = actuators[0]
        flam = actuators[1] if len(actuators) > 1 else None

        prev = last_hit_time.get(msg.note, None)

        is_roll = prev is not None and (current_time - prev) < ROLL_THRESHOLD

        # MAIN NOTE
        heapq.heappush(event_queue, (
            current_time,
            main,
            speed,
            strike_time
        ))

        # FLAM ONLY IF NOT A ROLL
        if (
            ENABLE_FLAMS and
            flam is not None and
            not is_roll and
            msg.velocity > 85
        ):
            heapq.heappush(event_queue, (
                current_time - FLAM_DELAY,
                flam,
                max(120, speed - 40),
                strike_time
            ))

        last_hit_time[msg.note] = current_time

# REAL-TIME ENGINE
def playback_engine():

    start_time = time.perf_counter()

    while event_queue and not stop_flag:

        now = time.perf_counter() - start_time

        # schedule ahead
        while event_queue and event_queue[0][0] <= now + LOOKAHEAD_TIME:

            t, actuator, speed, strike_time = heapq.heappop(event_queue)

            # wait until exact time
            while (time.perf_counter() - start_time) < t:
                time.sleep(0.0003)

            # STRIKE
            threading.Thread(
                target=execute_strike,
                args=(actuator, speed, strike_time),
                daemon=True
            ).start()

        time.sleep(0.001)

# STRIKE SEQUENCE
def execute_strike(actuator, speed, strike_time):

    trigger_actuator(actuator, 1, speed)
    time.sleep(strike_time)

    trigger_actuator(actuator, 0, 255)
    time.sleep(0.060)

    trigger_actuator(actuator, 2, 0)

# KILLSWITCH
def killswitch():
    global stop_flag
    input("Press ENTER to stop\n")
    stop_flag = True

threading.Thread(target=killswitch, daemon=True).start()

# SERIAL DETECTION
ports = serial.tools.list_ports.comports()

for port in ports:
    try:
        ser = serial.Serial(port.device, SERIAL_BAUD, timeout=1)
        time.sleep(2)

        line = ser.readline().decode().strip()

        if "READY:" in line:
            board_id = int(line.split(":")[1])
            boards[board_id] = ser
            print(f"Board {board_id} ready")
    except:
        pass

# RUN
print(f"Loaded {len(event_queue)} events")

playback_engine()

print("Done")
