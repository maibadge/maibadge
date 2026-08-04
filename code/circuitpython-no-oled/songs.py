"""Complete MaiBadge songs and non-blocking playback."""

import math


def note_frequency(note):
    if not note or note in ("REST", "0") or note[0] not in "ABCDEFG":
        return 0
    semitones = {"C": -9, "D": -7, "E": -5, "F": -4, "G": -2, "A": 0, "B": 2}
    position = 1
    accidental = 0
    if len(note) > 1 and note[1] in ("#", "B"):
        accidental = 1 if note[1] == "#" else -1
        position = 2
    try:
        octave = int(note[position:])
    except ValueError:
        return 0
    distance = semitones[note[0]] + accidental + ((octave - 4) * 12)
    return int(round(440.0 * math.pow(2.0, distance / 12.0)))


def sequence_from_steps(notes, lengths, seconds_per_step):
    return tuple(
        (note_frequency(note.replace("S", "#")), steps * seconds_per_step)
        for note, steps in zip(notes, lengths)
    )


def parse_rtttl(tune):
    _name, defaults_text, notes_text = tune.split(":", 2)
    defaults = {"d": 4, "o": 5, "b": 120}
    for setting in defaults_text.split(","):
        if "=" in setting:
            key, value = setting.split("=", 1)
            defaults[key.strip().lower()] = int(value)
    whole_note_seconds = 240.0 / defaults["b"]
    result = []
    for raw_token in notes_text.split(","):
        token = raw_token.strip().lower()
        if not token:
            continue
        position = 0
        digits = ""
        while position < len(token) and token[position].isdigit():
            digits += token[position]
            position += 1
        duration = int(digits) if digits else defaults["d"]
        if position >= len(token) or token[position] not in "abcdefgp":
            continue
        note_name = token[position].upper()
        position += 1
        if position < len(token) and token[position] == "#":
            note_name += "#"
            position += 1
        dotted = False
        if position < len(token) and token[position] == ".":
            dotted = True
            position += 1
        digits = ""
        while position < len(token) and token[position].isdigit():
            digits += token[position]
            position += 1
        octave = int(digits) if digits else defaults["o"]
        if position < len(token) and token[position] == ".":
            dotted = True
        seconds = whole_note_seconds / duration
        if dotted:
            seconds *= 1.5
        identifier = "REST" if note_name == "P" else note_name + str(octave)
        result.append((note_frequency(identifier), seconds))
    return tuple(result)


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

SUPER_MARIO = "Super Mario:d=4,o=5,b=125:a,8f.,16c,16d,16f,16p,f,16d,16c,16p,16f,16p,16f,16p,8c6,8a.,g,16c,a,8f.,16c,16d,16f,16p,f,16d,16c,16p,16f,16p,16a#,16a,16g,2f,16p,8a.,8f.,8c,8a.,f,16g#,16f,16c,16p,8g#.,2g,8a.,8f.,8c,8a.,f,16g#,16f,8c,2c6"
QZKAGO = "QZKago:d=8,o=5,b=125:c,d,d#,g4,f#4,g4,g#4,d#,d,d#,f,d#,d,d#,d,c,b4,c,d,d#,g#4,g4,g#4,g4,d#,d,d#,d,c,b4,a4,b4,c,c,d,d#,g4,f#4,g4,g#4,d#,d,d#,f,d#,d,d#,d,c,c,g,d#,g#4,g4,g#4,g4,g4,f#4,g4,g,f#,g,f,d#,d,c,d,d#,f,b4,c"

SONGS = (
    ("Mai Intro", sequence_from_steps(INTRO_NOTES, INTRO_STEPS, 0.25), 1.0),
    ("Eye Song", sequence_from_steps(EYE_NOTES, EYE_STEPS, 0.070), 1.0),
    ("QZKago", parse_rtttl(QZKAGO), 0.9),
    ("Super Mario", parse_rtttl(SUPER_MARIO), 0.9),
)


class SongPlayer:
    def __init__(self, buzzer):
        self.buzzer = buzzer
        self.sequence = ()
        self.index = 0
        self.duration = 0.0
        self.deadline = 0.0
        self.phase = "stopped"
        self.tone_fraction = 0.9

    @property
    def playing(self):
        return self.phase != "stopped"

    def start(self, sequence, now, tone_fraction=0.9):
        self.stop()
        self.sequence = sequence
        self.index = 0
        self.tone_fraction = tone_fraction
        self._begin_note(now)

    def _begin_note(self, now):
        if self.index >= len(self.sequence):
            self.stop()
            return
        frequency, duration = self.sequence[self.index]
        self.duration = max(0.01, duration)
        self.buzzer.tone(frequency)
        self.phase = "tone"
        self.deadline = now + self.duration * self.tone_fraction

    def update(self, now):
        if not self.playing or now < self.deadline:
            return self.playing
        if self.phase == "tone":
            self.buzzer.off()
            if self.tone_fraction >= 1.0:
                self.index += 1
                self._begin_note(now)
            else:
                self.phase = "gap"
                self.deadline = now + self.duration * (1.0 - self.tone_fraction)
        else:
            self.index += 1
            self._begin_note(now)
        return self.playing

    def stop(self):
        self.buzzer.off()
        self.sequence = ()
        self.index = 0
        self.phase = "stopped"
