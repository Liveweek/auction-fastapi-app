from enum import Enum


class AuctionStatus(str, Enum):
    on_moderate = "ON_MODERATE"
    scheduled   = "SCHEDULED"
    auc_open    = "OPEN"
    auc_closed  = "CLOSED"
    