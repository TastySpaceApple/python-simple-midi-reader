import simplemidireader

midi_file = simplemidireader.MIDIFileReader("Aghostofachance.mid")
print("Tracks: %d" % midi_file.num_tracks)
ticks_per_beat = 24 #default
tick_duration = 500000 / ticks_per_beat #default
for midi_track in midi_file.tracks():
    # each midi track is composed of `events`
    for event in midi_track.events():
        if(event['name'] == "Time Signature"):
            nn, dd, cc, bb = event['data']
            ticks_per_beat = cc
            print(f"Tempo: {nn}/{2**dd}")
            print(f"Clocks per tick: {cc}")
        if(event['name'] == "Set Tempo"):
            mpqn = sum([event['data'][x] << (16 - (8 * x)) for x in range(3)]) # calculating 24 bit binary to int
            tick_duration = mpqn / ticks_per_beat
            print(f"Microseconds per quarter note: {mpqn}, Beats Per Minute: {float(6e7) / mpqn}")
        if(event['name'] == "Note On"):
            print(f"time_delta: {event['timestamp']} ticks == {event['timestamp'] * ticks_per_beat} microseconds, pitch: {event['data'][0]}, velocity: {event['data'][1]}")
            # By definition, a note-on message with velocity of 0 is equivalent to the message: "note-off vv=40"
