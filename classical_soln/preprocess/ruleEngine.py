
MAX_ETD_FROM_IMPACTED_FLIGHT_IN_HOURS = 72
MAX_CONNECTION_TIME = 12
MIN_CONNECTION_TIME = 1

# This reference table can be used for identifying the cabin for each class of service
CABIN_CLASS_MAP = {
    "J": ["A", "D", "J"],
    "F": ["F", "B"],
    "Y": ["S", "V", "W", "Z", "O", "S", "T", "U", "M", "N", "Y"]
}

# This will be Used when Original class is not available to rebook
CLASS_TO_CLASS_MAP = {
    "A": ["F", "S"],
    "S": ["F", "A"],
    "F": ["S", "A"],
    "J": ["O", "C", "I"],
    "C": ["O", "J", "I"],
    "I": ["J", "C", "O"],
    "O": ["J", "C", "I"],
    "Y": ["B", "P", "Z"],
    "B": ["Y", "P", "Z"],
}

# 1. This is only applicable if Downgrade is on.
# 2. If Downgrade to Cabin J/F then refer to Downgrade class respectively
DOWNGRADE_CLASS_MAP = {
    "J": "Y",
    "F": "Y",
}

# 1. This is only applicable if Upgrade is enabled.
# 2. If Upgraded to Cabin F/J then refer to Upgrade class respectively
UPGRADE_CLASS_MAP = {
    "Y": "F",
    "F": "J",
}

class PNR:
    def __init__(self):

        self.Recloc = None
        self.TYPE = None
        self.SSR = None
        self.Cabin = None
        self.Class = None
        self.Number_Of_Down_lineConnections = 0
        self.PaidServices = None
        self.Booked_As = None
        self.Number_of_PAX = None
        self.Loyalty = None
        self.ForceKickOut = None

    def Score(self):

        Special_Services = ["INFT", "WHCR", "WCHS", "WCHC", "LANG", "CHILD", "EXST", "BLND", "DEAF"]
        total_score = None
        self.ForceKickOut = True

        # SSR Score
        if self.TYPE == "PNR.INDIVIDUAL" and self.SSR in Special_Services:
            total_score += 200

        # Cabin Score
        if self.TYPE == "PNR.INDIVIDUAL" and self.Cabin:
            cabin_score_mapping = {
                "J": 2000,
                "F": 1700,
                "Y": 1500
            }
            total_score += cabin_score_mapping.get(self.Cabin, 0)

        # Class Score
        if self.TYPE == "PNR.INDIVIDUAL" and self.Class:
            class_score_mapping = {
                "A": 1000,
                "C": 700,
                "K": 500,
            }
            total_score += class_score_mapping.get(self.Class, (0, 0))[0]

        # Connection Score
        if self.TYPE == "PNR.INDIVIDUAL" and self.Number_Of_Down_lineConnections is not None:
            total_score += 100 * self.Number_Of_Down_lineConnections

        # Paid Service Score
        if self.TYPE == "PNR.INDIVIDUAL" and self.PaidServices == "Yes":
            self.ForceKickOut = False
            total_score += 200

        # Booking-Type Score
        if self.TYPE == "PNR.INDIVIDUAL" and self.Booked_As == "Group":
            self.ForceKickOut = False
            total_score += 500

        # No of PAX Score
        if self.TYPE == "PNR.INDIVIDUAL" and self.Number_of_PAX is not None:
            self.ForceKickOut = False
            total_score += 50 * self.Number_of_PAX

        # Loyalty Score
        if self.TYPE == "PNR.INDIVIDUAL" and self.Loyalty is not None:
            loyalty_score_mapping = {
                "CM Presidential platinum": 2000,
                "Platinum": 1800,
                "Gold": 1600,
                "Silver": 1500,
            }
            self.ForceKickOut = False
            total_score += loyalty_score_mapping.get(self.Loyalty, 0)

        return total_score, self.ForceKickOut


def flight_selection(current_delay, current_flight_arrival, down_line_flight_depart):

    if current_delay >= MAX_ETD_FROM_IMPACTED_FLIGHT_IN_HOURS:
        return False

    connection_time = current_flight_arrival - down_line_flight_depart

    if connection_time > MAX_CONNECTION_TIME:
        return False

    if connection_time < MIN_CONNECTION_TIME:
        return False

    return True
