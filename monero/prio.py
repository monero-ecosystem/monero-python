import warnings
warnings.warn(
    "monero.prio is deprecated and will be gone in 0.8; use monero.const.PRIO_* consts instead",
    DeprecationWarning)

UNIMPORTANT=1
NORMAL=2
ELEVATED=3
PRIORITY=4
