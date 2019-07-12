from struct import unpack, pack
from enum import Enum

class MIDITrackEventType(Enum):
    SysexEvent = 1,
    MetaEvent = 2,
    MIDIEvent = 3

class MIDIFileReader(object):
    def __init__(self, midifile_path):
        if type(midifile_path) != str: raise ValueError("File path should be a string")

        self.filestream = open(midifile_path, 'rb')

        chunkType, chunkLength = self.read_chunk_header()
        if chunkType != b'MThd': raise TypeError("Bad header in MIDI file.")
        format, num_tracks, resolution = unpack(">HHH", self.filestream.read(chunkLength))
        self.num_tracks = num_tracks
        self.currentTrackIndex = 0

    def tracks(self):
        while self.currentTrackIndex < self.num_tracks:

            chunkType, chunkLength = self.read_chunk_header()

            if chunkType != b'MTrk': raise TypeError("Bad header in MIDI file. %s, %d" % (chunkType, chunkLength))

            trackReader = MIDITrackChunkReader(self.filestream, chunkLength, self.currentTrackIndex)

            self.currentTrackIndex += 1

            yield trackReader


    def read_chunk_header(self):
        chunkType, chunkLength = unpack(">4sL", self.filestream.read(8))

        return(chunkType, chunkLength)

class MIDITrackChunkReader(object):
    MIDIEvents = {
        # key: (event name as string, event data length)
        0x80: ('Note Off', 2),
        0x90: ('Note On', 2),
        0xA0: ('Polyphonic Key Pressure', 2),
        0xB0: ('Controller Change', 2),
        0xC0: ('Program Change', 1),
        0xD0: ('Channel Key Pressure', 1),
        0xE0: ('Pitch Bend', 2),
    }

    MetaEvents = { #https://www.csie.ntu.edu.tw/~r92092/ref/midi/#meta_event
        0x2F: ('End Of Track',),
        0x51: ('Set Tempo', ),
        0x58: ('Time Signature', ),
        0x59: ('Key Signature', ),
        0x01: ('Text Event',),
        0x03: ('Sequence/Track Name',)
    }

    def __init__(self, filestream, chunk_length, track_index):
        self.chunk_length = chunk_length
        self.filestream = filestream
        self.index = 0
        self.track_index = track_index

    def read_timestamp(self):
        NEXTBYTE = 1
        value = 0
        while NEXTBYTE:
            chr = self.read_byte()
            if not (chr & 0x80):
                NEXTBYTE = 0
            chr = chr & 0x7f
            value = value << 7
            value += chr
        return value

    def next_event(self):
        if(self.eof()): return False
        timestamp = self.read_timestamp()

        event_type = None
        status = 0x00
        data = []
        event_name = None

        event_status_byte = self.read_byte()

        if event_status_byte == 0xF0 or event_status_byte == 0xF7: #SysexEvent
            event_type = MIDITrackEventType.SysexEvent
            status = event_status_byte
            event_length = self.read_byte()
            data = self.read(event_length)
        elif event_status_byte == 0xFF: #MetaEvent
            event_type = MIDITrackEventType.MetaEvent
            status, event_length = self.read_bytes(2)
            data = self.read(event_length)
            ev = self.MetaEvents.get(status)
            if ev: event_name = ev[0]
        else:
            event_type = MIDITrackEventType.MIDIEvent
            status = event_status_byte
            key = status & 0xF0
            channel = status & 0x0F # who cares at this point
            midievent = self.MIDIEvents.get(key)
            if(midievent):
                data = self.read_bytes(midievent[1]) # event data length is second in tuple
                self.running_status = status
            else:
                midievent = self.MIDIEvents.get(self.running_status)
                data = ([event_status_byte] +
                        self.read_bytes(midievent[1] - 1)) # event data length is second in tuple

            event_name = midievent[0] # event name is first in typle

        return {'timestamp': timestamp, 'type': event_type,
           'status': status, 'data': data, 'name': event_name}

    def events(self):
        while True:
            event = self.next_event()
            if event: yield event
            else: break

    def read_byte(self):
        return ord(self.read(1))

    def read_bytes(self, len):
        return [self.read_byte() for i in range(len)]

    def read(self, len):
        if(len == 0): return []
        self.index += len
        return self.filestream.read(len)

    def eof(self):
        return self.index >= self.chunk_length

    def skipToEndOfTrack(self):
        self.read(self.chunk_length - self.index)
