import json
import os
import unittest

class JSONTestCase(unittest.TestCase):
    jsonrpc_url = 'http://127.0.0.1:18088/json_rpc'
    data_subdir = None

    def _read(self, *args):
        path = os.path.join(os.path.dirname(__file__), 'data')
        if self.data_subdir:
            path = os.path.join(path, self.data_subdir)
        path = os.path.join(path, *args)
        with open(path, 'r') as fh:
            return json.loads(fh.read())
