from Cryptodome.Hash import keccak


def keccak_256(data):
    """
    Return a hashlib-compatible Keccak 256 object for the given data.
    """
    hash = keccak.new(digest_bits=256)
    hash.update(data)
    return hash
