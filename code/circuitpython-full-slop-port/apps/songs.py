"""RTTTL parsing and non-blocking PWM song playback."""

import math


def note_frequency(note):
    if not note or note == "REST" or note == "0" or note[0] not in "ABCDEFG":
        return 0
    semitones = {"C": -9, "D": -7, "E": -5, "F": -4, "G": -2, "A": 0, "B": 2}
    name = note[0]
    position = 1
    accidental = 0
    if len(note) > 1 and note[1] in ("#", "B"):
        accidental = 1 if note[1] == "#" else -1
        position = 2
    try:
        octave = int(note[position:])
    except ValueError:
        return 0
    distance = semitones[name] + accidental + ((octave - 4) * 12)
    return int(round(440.0 * math.pow(2.0, distance / 12.0)))


def sequence_from_steps(notes, step_lengths, seconds_per_step):
    result = []
    for note, steps in zip(notes, step_lengths):
        result.append((note_frequency(note.replace("S", "#")), steps * seconds_per_step))
    return result


def parse_rtttl(tune):
    """Decode RTTTL with the same streaming semantics as MicroPython.

    The original parser consumes one character beyond each note instead of
    tokenising on commas.  Keeping that behaviour matters for the legacy
    QZKago string, so this is intentionally a direct, non-blocking port.
    """
    pieces = tune.split(":")
    if len(pieces) != 3:
        raise ValueError("tune should contain exactly 2 colons")

    defaults = {"d": 4, "o": 5, "b": 120}
    value = 0
    identifier = " "
    for character in pieces[1]:
        character = character.lower()
        if character.isdigit():
            value = (value * 10) + ord(character) - ord("0")
            if identifier in defaults:
                defaults[identifier] = value
        elif character.isalpha():
            identifier = character
            value = 0

    notes_text = pieces[2]
    note_index = 0

    def next_char():
        nonlocal note_index
        if note_index >= len(notes_text):
            return "|"
        character = notes_text[note_index]
        note_index += 1
        return " " if character == "," else character

    whole_note_seconds = 240.0 / defaults["b"]
    result = []
    while True:
        character = next_char()
        while character == " ":
            character = next_char()

        duration = 0
        while character.isdigit():
            duration = (duration * 10) + ord(character) - ord("0")
            character = next_char()
        if duration == 0:
            duration = defaults["d"]
        if character == "|":
            break

        note_name = character.upper()
        character = next_char()
        if character == "#":
            note_name += "#"
            character = next_char()

        duration_multiplier = 1.0
        if character == ".":
            duration_multiplier = 1.5
            character = next_char()

        if "4" <= character <= "7":
            octave = character
            character = next_char()
        else:
            octave = str(defaults["o"])

        if character == ".":
            duration_multiplier = 1.5

        note_identifier = "REST" if note_name == "P" else note_name + octave
        seconds = (whole_note_seconds / duration) * duration_multiplier
        result.append((note_frequency(note_identifier), seconds))
    return result


INTRO_NOTES = (
    "E5", "G4", "D5", "G4", "C5", "G4", "A4", "B4", "C5", "D5", "E5", "C5",
    "F5", "A4", "E5", "A4", "D5", "G4", "A4", "D5", "C5", "B4", "A4", "G4",
)
INTRO_STEPS = (2, 2, 1.5, 2, 1.5, 1, 1, 1, 1, 1, 1, 1, 2, 2, 1.5, 2, 1.5, 1, 1, 1, 1, 1, 1, 1)

EYE_NOTES = (
    "B4", "F#5", "E5", "D5", "0", "B4", "F5", "E5", "D5", "0",
    "B4", "F5", "E5", "D5", "0", "A#4", "B4", "C#5", "D5", "C#5", "B4", "A#4",
)
EYE_STEPS = (4, 4, 4, 16, 4, 4, 4, 4, 16, 4, 4, 4, 4, 16, 4, 4, 4, 4, 4, 4, 4, 12)

SUPER_MARIO = "Super Mario - Main Theme:d=4,o=5,b=125:a,8f.,16c,16d,16f,16p,f,16d,16c,16p,16f,16p,16f,16p,8c6,8a.,g,16c,a,8f.,16c,16d,16f,16p,f,16d,16c,16p,16f,16p,16a#,16a,16g,2f,16p,8a.,8f.,8c,8a.,f,16g#,16f,16c,16p,8g#.,2g,8a.,8f.,8c,8a.,f,16g#,16f,8c,2c6"

QZKAGO = (
    "QZKago:d=4,o=5,b=125:8c,8d,8d#,8g4,8f#4,16g4,8g#4,8d#,16d#,8d,8d#,")
QZKAGO += "8f,8d#,8d,16d#,8d,8c,16b4,8c,8d,"
QZKAGO += "8d#,8g#4,16g4,8g#4,8g4,16d#,16d,16d#,8d,8c,8b4,8a4,8b4,c"
QZKAGO += "8c,8d,8d#,8g4,8f#4,16g4,8g#4,8d#,16d#,8d,8d#,"
QZKAGO += "8f,8d#,8d,16d#,8d,16c,16c,4g,"
QZKAGO += "8d#,8g#4,16g4,8g#4,8g4,16g4,16f#4,16g4,16.,16g,16f#,16g,16.,"
QZKAGO += "16f,16d#,16d,16c,16d,16d#,16f,16b4,4c"


SONGS = {
    "song_intro": ("Mai intro", sequence_from_steps(INTRO_NOTES, INTRO_STEPS, 0.25)),
    "song_eye": ("Eye song", sequence_from_steps(EYE_NOTES, EYE_STEPS, 0.070)),
    "song_qzkago": ("QZKago", parse_rtttl(QZKAGO)),
    "song_mario": ("Mario", parse_rtttl(SUPER_MARIO)),
}

# The blocking intro/eye functions held each note for its full duration.  The
# original RTTTL MusicPlayer alone used a 90% tone / 10% silence articulation.
SONG_TONE_DUTY = {
    "song_intro": 1.0,
    "song_eye": 1.0,
    "song_qzkago": 0.9,
    "song_mario": 0.9,
}


class SongPlayer:
    def __init__(self, buzzer):
        self.buzzer = buzzer
        self.sequence = ()
        self.index = 0
        self.deadline = 0.0
        self.duration = 0.0
        self.phase = "stopped"
        self.total_duration = 0.0
        self.completed_duration = 0.0
        self.note_started_at = 0.0
        self.completed = False
        self.tone_duty = 0.9

    @property
    def playing(self):
        return self.phase != "stopped"

    @property
    def progress(self):
        if self.total_duration <= 0:
            return 0.0
        if self.completed:
            return 1.0
        return min(1.0, self.completed_duration / self.total_duration)

    def progress_at(self, now):
        if not self.playing:
            return self.progress
        current = min(self.duration, max(0.0, now - self.note_started_at))
        return min(1.0, (self.completed_duration + current) / self.total_duration)

    def start(self, sequence, now, tone_duty=0.9):
        self.stop()
        self.sequence = sequence
        self.index = 0
        self.tone_duty = min(1.0, max(0.0, tone_duty))
        self.total_duration = sum(item[1] for item in sequence)
        self.completed_duration = 0.0
        self.completed = False
        self._begin_next(now)

    def _begin_next(self, now):
        if self.index >= len(self.sequence):
            self._finish()
            return
        frequency, duration = self.sequence[self.index]
        self.duration = max(0.01, duration)
        self.note_started_at = now
        self.buzzer.tone(frequency)
        self.phase = "tone"
        self.deadline = now + (self.duration * self.tone_duty)

    def update(self, now):
        if self.phase == "stopped" or now < self.deadline:
            return self.playing
        if self.phase == "tone":
            self.buzzer.off()
            if self.tone_duty >= 1.0:
                self.completed_duration += self.duration
                self.index += 1
                self._begin_next(now)
                return self.playing
            self.phase = "gap"
            self.deadline = now + (self.duration * (1.0 - self.tone_duty))
        else:
            self.completed_duration += self.duration
            self.index += 1
            self._begin_next(now)
        return self.playing

    def _finish(self):
        self.buzzer.off()
        self.phase = "stopped"
        self.completed_duration = self.total_duration
        self.completed = True

    def stop(self):
        self.buzzer.off()
        self.phase = "stopped"
        self.sequence = ()
        self.index = 0
        self.duration = 0.0
        self.total_duration = 0.0
        self.completed_duration = 0.0
        self.note_started_at = 0.0
        self.completed = False
        self.tone_duty = 0.9
