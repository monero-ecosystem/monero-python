# ed25519.py - Optimized version of the reference implementation of Ed25519
#
# Written in 2011? by Daniel J. Bernstein <djb@cr.yp.to>
#            2013 by Donald Stufft <donald@stufft.io>
#            2013 by Alex Gaynor <alex.gaynor@gmail.com>
#            2013 by Greg Price <price@mit.edu>
#            2019 by Michal Salaban <michal@salaban.info>
#
# To the extent possible under law, the author(s) have dedicated all copyright
# and related and neighboring rights to this software to the public domain
# worldwide. This software is distributed without any warranty.
#
# You should have received a copy of the CC0 Public Domain Dedication along
# with this software. If not, see
# <http://creativecommons.org/publicdomain/zero/1.0/>.

"""
NB: This code is not safe for use with secret keys or secret data.
The only safe use of this code is for verifying signatures on public messages.

Functions for computing the public key of a secret key and for signing
a message are included, namely publickey_unsafe and signature_unsafe,
for testing purposes only.

The root of the problem is that Python's long-integer arithmetic is
not designed for use in cryptography.  Specifically, it may take more
or less time to execute an operation depending on the values of the
inputs, and its memory access patterns may also depend on the inputs.
This opens it to timing and cache side-channel attacks which can
disclose data to an attacker.  We rely on Python's long-integer
arithmetic, so we cannot handle secrets without risking their disclosure.
"""

import binascii
import six

import nacl.bindings


b = 256
q = 2 ** 255 - 19
l = 2 ** 252 + 27742317777372353535851937790883648493


def bit(h, i):
    return (six.indexbytes(h, i // 8) >> (i % 8)) & 1


def encodeint(y):
    bits = [(y >> i) & 1 for i in range(b)]
    return b"".join(
        [
            six.int2byte(sum([bits[i * 8 + j] << j for j in range(8)]))
            for i in range(b // 8)
        ]
    )


def decodeint(s):
    return sum(2 ** i * bit(s, i) for i in range(0, b))


edwards_add = nacl.bindings.crypto_core_ed25519_add
inv = nacl.bindings.crypto_core_ed25519_scalar_invert
public_from_secret = nacl.bindings.crypto_sign_ed25519_sk_to_pk
scalar_reduce = nacl.bindings.crypto_core_ed25519_scalar_reduce
scalarmult_B = nacl.bindings.crypto_scalarmult_ed25519_base_noclamp


def scalarmult(P, e):
    return nacl.bindings.crypto_scalarmult_ed25519_noclamp(e, P)


d = -121665 * decodeint(inv(encodeint(121666))) % q
I = pow(2, (q - 1) // 4, q)


def xrecover(y):
    xx = (y * y - 1) * decodeint(inv(encodeint(d * y * y + 1)))
    x = pow(xx, (q + 3) // 8, q)

    if (x * x - xx) % q != 0:
        x = (x * I) % q

    if x % 2 != 0:
        x = q - x

    return x


By = 4 * decodeint(inv(encodeint(5)))
Bx = xrecover(By)
B = (Bx % q, By % q, 1, (Bx * By) % q)
ident = (0, 1, 1, 0)


def encodepoint(P):
    (x, y, z, t) = P
    zi = inv(z)
    x = (x * zi) % q
    y = (y * zi) % q
    bits = [(y >> i) & 1 for i in range(b - 1)] + [x & 1]
    return b"".join(
        [
            six.int2byte(sum([bits[i * 8 + j] << j for j in range(8)]))
            for i in range(b // 8)
        ]
    )


def decodepoint(s):
    y = sum(2 ** i * bit(s, i) for i in range(0, b - 1))
    x = xrecover(y)
    if x & 1 != bit(s, b - 1):
        x = q - x
    P = (x, y, 1, (x * y) % q)
    return P


def pad_to_64B(v):
    return nacl.bindings.utils.sodium_pad(v, 64)


def public_from_secret_hex(hk):
    return binascii.hexlify(
        public_from_secret(pad_to_64B(binascii.unhexlify(hk)))
    ).decode()
