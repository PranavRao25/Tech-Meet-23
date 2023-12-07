MAX_ETD_FROM_IMPACTED_FLIGHT_IN_HOURS = 72
MAX_CONNECTION_TIME = 12
MIN_CONNECTION_TIME = 1

class PNR:
    def __init__(self):

        self.TYPE = None
        self.SSR = None
        self.Cabin = None
        self.Class = None
        self.Number_Of_Down_lineConnections = None
        self.PaidServices = None
        self.Booked_As = None
        self.Number_of_PAX = None
        self.Loyalty = None

    def score(self):
        return 100

def flight_selection(current_delay, current_flight_arrival, down_line_flight_depart):

    if current_delay >= MAX_ETD_FROM_IMPACTED_FLIGHT_IN_HOURS:
        return False

    connection_time = current_flight_arrival - down_line_flight_depart

    if connection_time > MAX_CONNECTION_TIME:
        return False

    if connection_time < MIN_CONNECTION_TIME:
        return False

    return True

# TODO : Downgrade & Upgrade class rules
CABIN_CLASS_MAP = {
    "J": ["J", "A", "D"],
    "F": ["F", "B"],
    "Y": ["Y", "M", "N", "O", "P", "S", "T", "U", "V", "W", "Z"]
}
