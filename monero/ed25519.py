import binascii
import six

import nacl.bindings


def bit(h, i):
    return (six.indexbytes(h, i // 8) >> (i % 8)) & 1


def encodeint(y):
    bits = [(y >> i) & 1 for i in range(256)]
    return b"".join(
        [six.int2byte(sum([bits[i * 8 + j] << j for j in range(8)])) for i in range(32)]
    )


def decodeint(s):
    return sum(2 ** i * bit(s, i) for i in range(0, 256))


edwards_add = nacl.bindings.crypto_core_ed25519_add
inv = nacl.bindings.crypto_core_ed25519_scalar_invert
scalarmult_B = nacl.bindings.crypto_scalarmult_ed25519_base_noclamp
scalarmult = nacl.bindings.crypto_scalarmult_ed25519_noclamp


def scalar_reduce(v):
    return nacl.bindings.crypto_core_ed25519_scalar_reduce(v + 32 * b"\0")


def public_from_secret_hex(hk):
    try:
        return binascii.hexlify(scalarmult_B(binascii.unhexlify(hk))).decode()
    except nacl.exceptions.RuntimeError:
        raise ValueError("Invalid secret key")
