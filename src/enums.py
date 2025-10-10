import enum


class VMStatus(enum.Enum):
    ACTIVE = 1
    DISABLE = 0


class Company(enum.IntEnum):
    MK = 383595
    UGMK = 395338
    SNACK = 395457


class MKStatuses(enum.IntEnum):
    NETWORK_CONNECTION_ERROR = 1
    MATRIX_LOADED = 21
    SALE_UNKNOWN_PRODUCT = 36
    FISCAL_ERROR = 44
