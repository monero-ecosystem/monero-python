# The reference Ed25519 software is in the public domain.
#     Source: https://ed25519.cr.yp.to/python/ed25519.py
#
# Parts Copyright (c) 2016 The MoneroPy Developers. Released under the BSD 3-Clause
# Parts taken from https://github.com/monero-project/mininero/blob/master/ed25519ietf.py

from binascii import hexlify, unhexlify
import hashlib
import operator as _oper
import sys as _sys

# Set up byte handling for Python 2 or 3
if _sys.version_info.major == 2:    # pragma: no cover
    int2byte = chr
    range = xrange

    def indexbytes(buf, i):
        return ord(buf[i])

    def intlist2bytes(l):
        return b"".join(chr(c) for c in l)
else:                               # pragma: no cover
    indexbytes = _oper.getitem
    intlist2bytes = bytes
    int2byte = _oper.methodcaller("to_bytes", 1, "big")

b = 256
q = 2**255 - 19
l = 2**252 + 27742317777372353535851937790883648493

def expmod(b, e, m):
    if e == 0: return 1
    t = expmod(b, e//2, m)**2 % m
    if e & 1: t = (t*b) % m
    return t

def inv(x):
  return expmod(x, q-2, q)

d = -121665 * inv(121666)
I = expmod(2, (q-1)//4, q)

def xrecover(y):
    xx = (y*y-1) * inv(d*y*y+1)
    x = expmod(xx, (q+3)//8, q)
    if (x*x - xx) % q != 0: x = (x*I) % q
    if x % 2 != 0: x = q-x
    return x

def compress(P):
    zinv = inv(P[2])
    return (P[0] * zinv % q, P[1] * zinv % q)

def decompress(P):
    return (P[0], P[1], 1, P[0]*P[1] % q)

By = 4 * inv(5)
Bx = xrecover(By)
B = [Bx%q, By%q]

def edwards(P, Q):
    x1 = P[0]
    y1 = P[1]
    x2 = Q[0]
    y2 = Q[1]
    x3 = (x1*y2+x2*y1) * inv(1+d*x1*x2*y1*y2)
    y3 = (y1*y2+x1*x2) * inv(1-d*x1*x2*y1*y2)
    return [x3%q, y3%q]

def add(P, Q):
    A = (P[1]-P[0])*(Q[1]-Q[0]) % q
    B = (P[1]+P[0])*(Q[1]+Q[0]) % q
    C = 2 * P[3] * Q[3] * d % q
    D = 2 * P[2] * Q[2] % q
    E = B-A
    F = D-C
    G = D+C
    H = B+A
    return (E*F, G*H, F*G, E*H)

def add_compressed(P, Q):
    return compress(add(decompress(P), decompress(Q)))

def scalarmult(P, e):
    if e == 0: return [0, 1]
    Q = scalarmult(P, e//2)
    Q = edwards(Q, Q)
    if e & 1: Q = edwards(Q, P)
    return Q

def encodeint(y):
    bits = [(y >> i) & 1 for i in range(b)]
    return b''.join([int2byte(sum([bits[i*8 + j] << j for j in range(8)])) for i in range(b//8)])

def encodepoint(P):
    x = P[0]
    y = P[1]
    bits = [(y >> i) & 1 for i in range(b-1)] + [x & 1]
    return b''.join([int2byte(sum([bits[i * 8 + j] << j for j in range(8)])) for i in range(b//8)])

def bit(h, i):
    return (indexbytes(h, i//8) >> (i%8)) & 1

def isoncurve(P):
    x = P[0]
    y = P[1]
    return (-x*x + y*y - 1 - d*x*x*y*y) % q == 0

def decodeint(s):
    return sum(2**i * bit(s, i) for i in range(0, b))

def decodepoint(s):
    y = sum(2**i * bit(s, i) for i in range(0, b-1))
    x = xrecover(y)
    if x & 1 != bit(s, b-1): x = q - x
    P = [x, y]
    if not isoncurve(P): raise Exception("decoding point that is not on curve")
    return P

# These are unused but let's keep them
#def H(m):
#    return hashlib.sha512(m).digest()
#
#def Hint(m):
#    h = H(m)
#    return sum(2**i * bit(h, i) for i in range(2*b))
#
#def publickey(sk):
#    h = H(sk)
#    a = 2**(b-2) + sum(2**i * bit(h, i) for i in range(3, b-2))
#    A = scalarmult(B, a)
#    return encodepoint(A)
#
#def signature(m, sk, pk):
#    h = H(sk)
#    a = 2**(b-2) + sum(2**i * bit(h, i) for i in range(3, b-2))
#    r = Hint(intlist2bytes([indexbytes(h, j) for j in range(b//8, b//4)]) + m)
#    R = scalarmult(B, r)
#    S = (r + Hint(encodepoint(R)+pk+m) * a) % l
#    return encodepoint(R) + encodeint(S)
#
#def checkvalid(s, m, pk):
#    if len(s) != b//4: raise Exception("signature length is wrong")
#    if len(pk) != b//8: raise Exception("public-key length is wrong")
#    R = decodepoint(s[0:b//8])
#    A = decodepoint(pk)
#    S = decodeint(s[b//8:b//4])
#    h = Hint(encodepoint(R) + pk + m)
#    if scalarmult(B, S) != edwards(R, scalarmult(A, h)):
#        raise Exception("signature does not pass verification")

def public_from_secret(k):
    keyInt = decodeint(k)
    aB = scalarmult(B, keyInt)
    return encodepoint(aB)

def public_from_secret_hex(hk):
    return hexlify(public_from_secret(unhexlify(hk))).decode()
