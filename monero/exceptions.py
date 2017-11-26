class MoneroException(Exception):
    pass

class BackendException(MoneroException):
    pass

class AccountException(MoneroException):
    pass

class NotEnoughMoney(AccountException):
    pass
