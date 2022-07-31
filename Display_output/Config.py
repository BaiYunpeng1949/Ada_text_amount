# Avoid using string magic words. Declare global variables. Store configurations in a separate file.

# Key press enumerators
RIGHT_CLICK_RING_MOUSE = 3

# GAP TASK TYPES.
GAP_COUNT_TASK = "count task"
GAP_MATH_TASK = "math task"
# GAP_TASK_SPECIFICATIONS.
CIRCLE = "circle"
RECT = "rectangle"
TRIANG = "triangle"

# Global marks
BLANK_LINE = "dudu"
# Modes.
MODE_ADAPTIVE = "adaptive"
MODE_MANUAL = "manual"
MODE_PRESENT_ALL = "present all"
MODE_CONTEXTUAL = "contextual adaptive"

# Experiment conditions.
CONDITION_POS_HOR = "position horizontal"

# For pilot studies.
# Configurations. The condition number listed here are generated randomly. Use dictionary to store data.
# WARNING: if the attention duration of secondary(gap) task time is too short, then there will be invalid gap task buffers.
CONDITIONS_DATA_COLLECTION = {
    1: {
        "duration_gap": 2000,
        "mode_update": MODE_MANUAL,
        "number of words": 3
    },
    2: {
        "duration_gap": 2000,
        "mode_update": MODE_MANUAL,
        "number of words": 1
    }
}

CONDITIOMS_TRAININGS = {
    1: {
        "duration_gap": 2000,
        "mode_update": MODE_MANUAL,
        "number of words": 5
    },
    2: {
        "duration_gap": 2000,
        "mode_update": MODE_MANUAL,
        "number of words": 5
    }
}

CONDITIONS_STUDIES = {
    1: {
        "duration_gap": 5000,
        "mode_update": MODE_MANUAL,
        "number of words": 2,
        "margin width": 50
    },
    2: {
        "duration_gap": 5000,
        "mode_update": MODE_MANUAL,
        "number of words": 2,
        "margin width": 50
    },
    3: {
        "duration_gap": 5000,
        "mode_update": MODE_MANUAL,
        "number of words": 2,
        "margin width": 50
    },
    4: {
        "duration_gap": 5000,
        "mode_update": MODE_MANUAL,
        "number of words": 2,
        "margin width": 50
    }
}

SOURCE_TEXTS_PATH_LIST_DATA_COLLECTION = [
    # Text for testing on data-collection session.
    "Display_output/Reading Materials/Pilot version 1 July/Earth day_144.txt",
    # Text for formal data-collection session and training session.
    "Display_output/Reading Materials/Pilot version 6 July/Story02_366wrds_32sts_11.44wpst.txt",
]

SOURCE_TEXTS_PATH_LIST_TRAINING = [
    # Text for formal data-collection session and training session.
    "Display_output/Reading Materials/Pilot version 1 July/Earth day_144.txt",
    # "Display_output/Reading Materials/Pilot version 6 July/Story02_366wrds_32sts_11.44wpst.txt",
]

SOURCE_TEXTS_PATH_LIST_FORMAL_STUDIES = [
    # Text for formal studies.
    # "Display_output/Reading Materials/Pilot version 6 July/Story12_348wds_20sts_17.4wpst.txt",
    # "Display_output/Reading Materials/Pilot version 6 July/Story03_372wrds_19sts_19.58wpst.txt",
    # "Display_output/Reading Materials/Pilot version 6 July/Story05_351wrds_27sts_13wpst.txt",
    # "Display_output/Reading Materials/Pilot version 6 July/Story06_355wrds_26sts_13.65wpst.txt",
    # "Display_output/Reading Materials/Pilot version 6 July/Story07_367wrds_22sts_16.68wpst.txt",
    # "Display_output/Reading Materials/Pilot version 6 July/Story10_347wrds_19sts_18.26wpst.txt",
    # "Display_output/Reading Materials/Pilot version 6 July/Story12_348wds_20sts_17.4wpst.txt"

    # "Display_output/Reading Materials/Pilot version 6 July/Story19_375wrds_34sts_11.03wpst.txt",
    # "Display_output/Reading Materials/Pilot version 6 July/Story20_349wrds_35sts_9.97wpst.txt",
    # "Display_output/Reading Materials/Pilot version 6 July/Story13.txt",
    # "Display_output/Reading Materials/Pilot version 6 July/Story14.txt"

    "Display_output/Reading Materials/Pilot version 31 July/L3S16_FS93_239wrds.txt",
    "Display_output/Reading Materials/Pilot version 31 July/L6S16_FS80_339wrds.txt",
    "Display_output/Reading Materials/Pilot version 31 July/L7S16_FS70_341wrds.txt",
    "Display_output/Reading Materials/Pilot version 31 July/L13S9_FS48_504wrds.txt"
]

# Runners (instances)' argument settings.
COLOR_TEXTS = (73, 232, 56)     # The color of texts displayed: green.
COLOR_BACKGROUND = "black"
SIZE_TEXTS = 45     # The size of texts displayed.
SIZE_GAP_TASK = 64  # The size of elements in secondary tasks.
POS_TEXTS = (325, 50)        # The starting position of texts displayed: x_pixels and y_pixels.
POS_GAP = (0, 0)            # The starting position of gap task displayed.
OFFSET_READING_SPEED = 0    # The offset of specific participant's reading speed.
WPS_READING_SPEED_INITIAL = 19   # The reading speed initialization of a specific participant.
MARGIN_BOT_RIGHT_WIDTH = 150     # The horizontal margin of ipa data displayed on the right bottom corner.
MARGIN_BOT_RIGHT_HEIGHT = 150    # The vertical margin of ipa data displayed on the right bottom corner.

# Socket configurations.
IP_LOCAL_HOST = '127.0.0.1'
PORT_RANDOM = 50000

# IPA arguments.
IS_3D_METHOD = False    # The 3D model's pupil diameter's data show less difference.
IS_2_PUPILS = False     # Whether to split 2 pupil's data apart and average or not. Still, not much difference.
