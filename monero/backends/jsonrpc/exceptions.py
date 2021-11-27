from ... import exceptions


class RPCError(exceptions.BackendException):
    pass


class Unauthorized(RPCError):
    pass


class MethodNotFound(RPCError):
    pass


class RestrictedRPC(RPCError):
    pass
