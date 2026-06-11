import enum


class ContactStatus(str, enum.Enum):
    VIP = "VIP"
    BLOCKED = "Blocked"
    ACTIVE = "Active"
    CHURNED = "Churned"


class ThreadStatus(str, enum.Enum):
    OPEN = "Open"
    RESOLVED = "Resolved"
    ESCALATED = "Escalated"
    IGNORED = "Ignored"


class EmailStatus(str, enum.Enum):
    RECEIVED = "Received"
    PROCESSING = "Processing"
    REPLIED = "Replied"
    ESCALATED = "Escalated"
    IGNORED = "Ignored"
