from enum import Enum

class ApplicationStatus(Enum):
    APPLIED = "Applied"
    OA = "OA"
    INTERVIEW = "Interview"
    FINAL_ROUND = "Final Round"
    REJECTED = "Rejected"
    OFFER = "Offer"