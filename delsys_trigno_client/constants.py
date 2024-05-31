import enum

class TrignoPort(enum.Enum):
    COMMAND = 50040
    EMG_DATA = 50043
    AUX_DATA = 50044

DEFAULT_DIGITAL_SERVER_IP = "169.254.113.0"