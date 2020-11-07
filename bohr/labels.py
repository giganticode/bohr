from enum import Enum


class Label(Enum):
    BUG = 1
    BUGLESS = 0
    ABSTAIN = -1