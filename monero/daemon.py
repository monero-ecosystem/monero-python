class Daemon(object):
    def __init__(self, backend):
        self._backend = backend

    def get_info(self):
        return self._backend.get_info()

    def get_height(self):
        return self._backend.get_info()['height']

    def send_transaction(self, tx):
        return self._backend.send_transaction(tx.blob)

    def get_mempool(self):
        return self._backend.get_mempool()
