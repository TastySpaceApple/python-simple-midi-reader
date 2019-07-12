Python Simple MIDI Reader
=======================================

Because reading a midi file should be done with only one file. just copy `simplemidireader.py` to your project. No dependencies attached.

How to use
-------------

Code example:

```python
import simplemidireader

midi_file = simplemidireader.MIDIFileReader("Aghostofachance.mid")
print("Tracks: %d" % midi_file.num_tracks)
for midi_track in midi_file.tracks():
    # each midi track is composed of `events`
    for event in midi_track.events():
        print(event)

```

use https://www.csie.ntu.edu.tw/~r92092/ref/midi/,
and particularly https://www.csie.ntu.edu.tw/~r92092/ref/midi/midi_channel_voice.html to get the most out of this code.
