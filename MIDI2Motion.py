import mido

midi = mido.MidiFile("Unholy Confessions drum.mid")

time_ms = 0

for msg in midi:
    time_ms += int(msg.time * 1000)

    if msg.type == "note_on" and msg.velocity > 0:

        # convert MIDI note to actuator position
        pos = int((msg.note - 36) / (84 - 36) * 120 + 30)

        print(f"{time_ms},{pos}")