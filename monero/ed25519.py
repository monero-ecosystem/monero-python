import binascii
import nacl.bindings

edwards_add = nacl.bindings.crypto_core_ed25519_add
inv = nacl.bindings.crypto_core_ed25519_scalar_invert
scalar_add = nacl.bindings.crypto_core_ed25519_scalar_add
scalarmult_B = nacl.bindings.crypto_scalarmult_ed25519_base_noclamp
scalarmult = nacl.bindings.crypto_scalarmult_ed25519_noclamp

# https://github.com/monero-project/monero/blob/9f814edbd78c70c70b814ca934c1ddef58768262/src/ringct/rctTypes.h#L615
H = binascii.unhexlify(
    "8b655970153799af2aeadc9ff1add0ea6c7251d54154cfa92c173a0dd39c1f94"
)


def scalarmult_H(v):
    return scalarmult(v, H)


def scalar_reduce(v):
    return nacl.bindings.crypto_core_ed25519_scalar_reduce(v + (64 - len(v)) * b"\0")


def public_from_secret_hex(hk):
    try:
        return binascii.hexlify(scalarmult_B(binascii.unhexlify(hk))).decode()
    except nacl.exceptions.RuntimeError:
        raise ValueError("Invalid secret key")
