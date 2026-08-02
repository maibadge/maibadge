"""Small, timestamped rhythm-game charts.

Times are the moment a note reaches its matching outer touch electrode.  Keeping
charts as tuples makes them easy to edit on a desktop and cheap to keep in RAM.
"""


TUTORIAL_TITLE = "TOUCH TUTORIAL"
TUTORIAL_DIFFICULTY = "EASY"

# (hit time in seconds, pad location 0-7).  The first phrase teaches the four
# cardinal pads, then the diagonals, followed by a gentle clockwise pattern.
TUTORIAL_CHART = (
    (2.00, 0), (2.75, 2), (3.50, 4), (4.25, 6),
    (5.50, 1), (6.25, 3), (7.00, 5), (7.75, 7),
    (9.00, 0), (9.45, 1), (9.90, 2), (10.35, 3),
    (10.80, 4), (11.25, 5), (11.70, 6), (12.15, 7),
    (13.50, 7), (13.95, 6), (14.40, 5), (14.85, 4),
    (15.30, 3), (15.75, 2), (16.20, 1), (16.65, 0),
    (18.00, 0), (18.00, 4), (18.70, 2), (18.70, 6),
    (20.00, 1), (20.45, 3), (20.90, 5), (21.35, 7),
)
