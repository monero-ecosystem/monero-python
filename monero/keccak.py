cd_keccak = None
sha3_keccak = None

try:
    from Cryptodome.Hash import cd_keccak
except ImportError:
    from sha3 import keccak_256 as sha3_keccak


def keccak_256(data):
    """
    Return a hashlib-compatible Keccak 256 object for the given data.
    """
    if cd_keccak is not None:
        h = cd_keccak.new(digest_bits=256)
        h.update(data)
    elif sha3_keccak is not None:
        h = sha3_keccak(data)
    else:   # pragma: no cover
        raise RuntimeError("SHA3 implementation is missing. Install either 'pycryptodomex' (recommended) or 'pysha3' package to provide it")
    return h
