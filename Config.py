# Avoid using string magic words. Declare global variables. Store configurations in a separate file.

# GAP TASK TYPES.
GAP_COUNT_TASK = "count task"
GAP_MATH_TASK = "math task"
# GAP_TASK_SPECIFICATIONS.
CIRCLE = "circle"
RECT = "rectangle"
TRIANG = "triangle"

# Global marks
BLANK_LINE = ""
# Modes.
MODE_ADAPTIVE = "adaptive"
MODE_MANUAL = "manual"
MODE_PRESENT_ALL = "present all"
MODE_CONTEXTUAL = "contextual adaptive"

# Experiment conditions.
CONDITION_POS_HOR = "position horizontal"

# For pilot studies.
# Configurations. The condition number listed here are generated randomly. Use dictionary to store data.
CONDITIONS_DATA_COLLECTION = {
    1: {
        "duration_gap": 2000,
        "mode_update": MODE_MANUAL
    }
}

CONDITIOMS_TRAININGS = {
    1: {
        "duration_gap": 2000,
        "mode_update": MODE_PRESENT_ALL
    },
    2: {
        "duration_gap": 2000,
        "mode_update": MODE_ADAPTIVE
    },
    3: {
        "duration_gap": 2000,
        "mode_update": MODE_CONTEXTUAL
    }
}
CONDITIONS_STUDIES = {
    1: {
        "duration_gap": 5000,
        "mode_update": MODE_PRESENT_ALL
    },
    2: {
        "duration_gap": 15000,
        "mode_update": MODE_CONTEXTUAL
    },
    3: {
        "duration_gap": 5000,
        "mode_update": MODE_ADAPTIVE
    },
    4: {
        "duration_gap": 5000,
        "mode_update": MODE_CONTEXTUAL
    },
    5: {
        "duration_gap": 15000,
        "mode_update": MODE_ADAPTIVE
    },
    6: {
        "duration_gap": 15000,
        "mode_update": MODE_PRESENT_ALL
    }
}

SOURCE_TEXTS_PATH_LIST = [
    "Reading Materials/Pilot version 6 July/Story02_366wrds_32sts_11.44wpst.txt",
    # This text is for the data collection session and training session.
    "Reading Materials/Pilot version 6 July/Story03_372wrds_19sts_19.58wpst.txt",
    "Reading Materials/Pilot version 6 July/Story05_351wrds_27sts_13wpst.txt",
    "Reading Materials/Pilot version 6 July/Story06_355wrds_26sts_13.65wpst.txt",
    "Reading Materials/Pilot version 6 July/Story07_367wrds_22sts_16.68wpst.txt",
    "Reading Materials/Pilot version 6 July/Story10_347wrds_19sts_18.26wpst.txt",
    "Reading Materials/Pilot version 6 July/Story12_348wds_20sts_17.4wpst.txt"
]

# Runners (instances)' argument settings.
AMOUNT_WORDS = 35   # The number of words.
COLOR_TEXTS = (73, 232, 56)     # The color of texts displayed: green.
COLOR_BACKGROUND = "black"
SIZE_TEXTS = 60     # The size of texts displayed.
SIZE_GAP_TASK = 64  # The size of elements in secondary tasks.
POS_TEXTS = (50, 50)        # The starting position of texts displayed: x_pixels and y_pixels.
POS_GAP = (0, 0)            # The starting position of gap task displayed.
OFFSET_READING_SPEED = 0    # The offset of specific participant's reading speed.
WPS_READING_SPEED_INITIAL = 9   # The reading speed initialization of a specific participant.
