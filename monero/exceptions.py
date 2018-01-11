class MoneroException(Exception):
    pass

class BackendException(MoneroException):
    pass

class AccountException(MoneroException):
    pass

class WrongAddress(AccountException):
    pass

class WrongPaymentId(AccountException):
    pass

class NotEnoughMoney(AccountException):
    pass

class NotEnoughUnlockedMoney(NotEnoughMoney):
    pass

class AmountIsZero(AccountException):
    pass

class TransactionNotPossible(AccountException):
    pass
