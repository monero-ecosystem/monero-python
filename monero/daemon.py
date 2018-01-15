class Daemon(object):
    def __init__(self, backend):
        self._backend = backend

    def get_info(self):
        return self._backend.get_info()

    def send_transaction(self, blob):
        return self._backend.send_transaction(blob)
