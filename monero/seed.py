#!/usr/bin/env python

# Electrum - lightweight Bitcoin client
# Copyright (C) 2011 thomasv@gitorious
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation files
# (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge,
# publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
# BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# Note about US patent no 5892470: Here each word does not represent a given digit.
# Instead, the digit represented by a word is variable, it depends on the previous word.
#
# Copied 17 February 2018 from MoneroPy, originally from Electrum:
#     https://github.com/bigreddmachine/MoneroPy/blob/master/moneropy/mnemonic.py ch: 80cc16c39b16c55a8d052fbf7fae68644f7a5f02
#     https://github.com/spesmilo/electrum/blob/master/lib/old_mnemonic.py ch:9a0aa9b4783ea03ea13c6d668e080e0cdf261c5b
#
# Significantly modified on 26 May 2018 by Michal Salaban:
#   + support for 12/13-word seeds
#   + simplified interface, changed exceptions (assertions -> explicit raise)
#   + optimization

from monero import address
from monero import wordlists
from monero import ed25519
from monero import base58
from binascii import crc32, hexlify, unhexlify
from os import urandom
from sha3 import keccak_256

class Seed(object):
    """Creates a seed object either from local system randomness or an imported phrase.

    :rtype: :class:`Seed <monero.seed.Seed>`
    """

    n = 1626
    wordlist = wordlists.english.wordlist # default english for now

    phrase = "" #13 or 25 word mnemonic word string
    hex = "" # hexadecimal

    def __init__(self, phrase_or_hex=""):
        """If user supplied a seed string to the class, break it down and determine
        if it's hexadecimal or mnemonic word string. Gather the values and store them.
        If no seed is passed, automatically generate a new one from local system randomness.

        :rtype: :class:`Seed <monero.seed.Seed>`
        """
        if phrase_or_hex:
            seed_split = phrase_or_hex.split(" ")
            if len(seed_split) >= 24:
                # standard mnemonic
                self.phrase = phrase_or_hex
                if len(seed_split) == 25:
                    # with checksum
                    self._validate_checksum()
                self._decode_seed()
            elif len(seed_split) >= 12:
                # mymonero mnemonic
                self.phrase = phrase_or_hex
                if len(seed_split) == 13:
                    # with checksum
                    self._validate_checksum()
                self._decode_seed()
            elif len(seed_split) == 1:
                # single string, probably hex, but confirm
                if not len(phrase_or_hex) % 8 == 0:
                    raise ValueError("Not valid hexadecimal: {hex}".format(hex=phrase_or_hex))
                self.hex = phrase_or_hex
                self._encode_seed()
            else:
                raise ValueError("Not valid mnemonic phrase or hex: {arg}".format(arg=phrase_or_hex))
        else:
            self.hex = generate_hex()
            self._encode_seed()

    def is_mymonero(self):
        """Returns True if the seed is MyMonero-style (12/13-word)."""
        return len(self.hex) == 32

    def endian_swap(self, word):
        """Given any string, swap bits and return the result.

        :rtype: str
        """
        return "".join([word[i:i+2] for i in [6, 4, 2, 0]])

    def _encode_seed(self):
        """Convert hexadecimal string to mnemonic word representation with checksum.
        """
        out = []
        for i in range(len(self.hex) // 8):
            word = self.endian_swap(self.hex[8*i:8*i+8])
            x = int(word, 16)
            w1 = x % self.n
            w2 = (x // self.n + w1) % self.n
            w3 = (x // self.n // self.n + w2) % self.n
            out += [self.wordlist[w1], self.wordlist[w2], self.wordlist[w3]]
        checksum = get_checksum(" ".join(out))
        out.append(checksum)
        self.phrase = " ".join(out)

    def _decode_seed(self):
        """Calculate hexadecimal representation of the phrase.
        """
        phrase = self.phrase.split(" ")
        out = ""
        for i in range(len(phrase) // 3):
            word1, word2, word3 = phrase[3*i:3*i+3]
            w1 = self.wordlist.index(word1)
            w2 = self.wordlist.index(word2) % self.n
            w3 = self.wordlist.index(word3) % self.n
            x = w1 + self.n *((w2 - w1) % self.n) + self.n * self.n * ((w3 - w2) % self.n)
            out += self.endian_swap("%08x" % x)
        self.hex = out

    def _validate_checksum(self):
        """Given a mnemonic word string, confirm seed checksum (last word) matches the computed checksum.

        :rtype: bool
        """
        phrase = self.phrase.split(" ")
        if get_checksum(self.phrase) == phrase[-1]:
            return True
        raise ValueError("Invalid checksum")

    def sc_reduce(self, input):
        integer = ed25519.decodeint(unhexlify(input))
        modulo = integer % ed25519.l
        return hexlify(ed25519.encodeint(modulo)).decode()

    def hex_seed(self):
        return self.hex

    def _hex_seed_keccak(self):
        h = keccak_256()
        h.update(unhexlify(self.hex))
        return h.hexdigest()

    def secret_spend_key(self):
        a = self._hex_seed_keccak() if self.is_mymonero() else self.hex
        return self.sc_reduce(a)

    def secret_view_key(self):
        b = self._hex_seed_keccak() if self.is_mymonero() else self.secret_spend_key()
        h = keccak_256()
        h.update(unhexlify(b))
        return self.sc_reduce(h.hexdigest())

    def public_spend_key(self):
        keyInt = ed25519.decodeint(unhexlify(self.secret_spend_key()))
        aG = ed25519.scalarmultbase(keyInt)
        return hexlify(ed25519.encodepoint(aG)).decode()

    def public_view_key(self):
        keyInt = ed25519.decodeint(unhexlify(self.secret_view_key()))
        aG = ed25519.scalarmultbase(keyInt)
        return hexlify(ed25519.encodepoint(aG)).decode()

    def public_address(self, net='mainnet'):
        """Returns the master :class:`Address <monero.address.Address>` represented by the seed.

        :param net: the network, one of 'mainnet', 'testnet', 'stagenet'. Default is 'mainnet'.

        :rtype: :class:`Address <monero.address.Address>`
        """
        if net not in ('mainnet', 'testnet', 'stagenet'):
            raise ValueError(
                "Invalid net argument. Must be one of ('mainnet', 'testnet', 'stagenet').")
        netbyte = 18 if net == 'mainnet' else 53 if net == 'testnet' else 24
        data = "{:x}{:s}{:s}".format(netbyte, self.public_spend_key(), self.public_view_key())
        h = keccak_256()
        h.update(unhexlify(data))
        checksum = h.hexdigest()
        return base58.encode(data + checksum[0:8])


def get_checksum(phrase):
    """Given a mnemonic word string, return a string of the computed checksum.

    :rtype: str
    """
    phrase_split = phrase.split(" ")
    if len(phrase_split) < 12:
        raise ValueError("Invalid mnemonic phrase")
    if len(phrase_split) > 13:
        # Standard format
        phrase = phrase_split[:24]
    else:
        # MyMonero format
        phrase = phrase_split[:12]
    wstr = "".join(word[:3] for word in phrase)
    z = ((crc32(wstr.encode()) & 0xffffffff) ^ 0xffffffff ) >> 0
    z2 = ((z ^ 0xffffffff) >> 0) % len(phrase)
    return phrase_split[z2]

def generate_hex(n_bytes=32):
    """Generate a secure and random hexadecimal string. 32 bytes by default, but arguments can override.

    :rtype: str
    """
    h = hexlify(urandom(n_bytes))
    return "".join(h.decode("utf-8"))
