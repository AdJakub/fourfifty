from enum import Enum
from dataclasses import dataclass

class Label(Enum):
    NORMAL = "normal"
    RETRY = "retry"
    PROMO = "promo"
    COMPROMISED = "compromised"
    HARVEST = "harvest"
    BOT = "bot"

@dataclass(frozen=True, slots=True)
class Event:
    timestamp: float
    client_ip: str
    mail_from: str
    rcpt_to: str
    message_id: int
    label: Label

