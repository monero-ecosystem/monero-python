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

    def __init__(self, phrase=""):
        """If user supplied a seed string to the class, break it down and determine
        if it's hexadecimal or mnemonic word string. Gather the values and store them.
        If no seed is passed, automatically generate a new one from local system randomness.

        :rtype: :class:`Seed <monero.seed.Seed>`
        """
        if phrase:
            seed_split = phrase.split(" ")
            if len(seed_split) >= 24:
                # standard mnemonic
                self.phrase = phrase
                if len(seed_split) == 25:
                    # with checksum
                    self.validate_checksum()
                self.hex = self.decode_seed()
            elif len(seed_split) >= 12:
                # mymonero mnemonic
                self.phrase = phrase
                if len(seed_split) == 13:
                    # with checksum
                    self.validate_checksum()
                self.hex = self.decode_seed()
            elif len(seed_split) == 1:
                # single string, probably hex, but confirm
                if not len(phrase) % 8 == 0:
                    raise ValueError("Not valid hexadecimal: {hex}".format(hex=phrase))
                self.hex = phrase
                self.phrase = self.encode_seed()
            else:
                raise ValueError("Not valid mnemonic phrase: {phrase}".format(phrase=phrase))
        else:
            self.hex = generate_hex()
            self.encode_seed()


    def endian_swap(self, word):
        """Given any string, swap bits and return the result.

        :rtype: str
        """
        return "".join([word[i:i+2] for i in [6, 4, 2, 0]])

    def encode_seed(self):
        """Given a hexadecimal string, return it's mnemonic word representation with checksum.

        :rtype: str
        """
        assert self.hex, "Seed hex not set"
        assert len(self.hex) % 8 == 0, "Not valid hexadecimal"
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
        return self.phrase

    def decode_seed(self):
        """Given a mnemonic word string, return it's hexadecimal representation.

        :rtype: str
        """
        assert self.phrase, "Seed phrase not set"
        phrase = self.phrase.split(" ")
        assert len(phrase) >= 12, "Not valid mnemonic phrase"
        out = ""
        for i in range(len(phrase) // 3):
            word1, word2, word3 = phrase[3*i:3*i+3]
            w1 = self.wordlist.index(word1)
            w2 = self.wordlist.index(word2) % self.n
            w3 = self.wordlist.index(word3) % self.n
            x = w1 + self.n *((w2 - w1) % self.n) + self.n * self.n * ((w3 - w2) % self.n)
            out += self.endian_swap("%08x" % x)
        self.hex = out
        return self.hex

    def validate_checksum(self):
        """Given a mnemonic word string, confirm seed checksum (last word) matches the computed checksum.

        :rtype: bool
        """
        assert self.phrase, "Seed phrase not set"
        phrase = self.phrase.split(" ")
        assert len(phrase) > 12, "Not valid mnemonic phrase"
        is_match = get_checksum(self.phrase) == phrase[-1]
        assert is_match, "Not valid checksum"
        return is_match

    def sc_reduce(self, input):
        integer = ed25519.decodeint(unhexlify(input))
        modulo = integer % ed25519.l
        return hexlify(ed25519.encodeint(modulo))

    def hex_seed(self):
        return self.hex

    def secret_spend_key(self):
        return self.sc_reduce(self.hex)

    def secret_view_key(self):
        h = keccak_256()
        h.update(unhexlify(self.secret_spend_key()))
        return self.sc_reduce(h.hexdigest())

    def public_spend_key(self):
        keyInt = ed25519.decodeint(unhexlify(self.secret_spend_key()))
        aG = ed25519.scalarmultbase(keyInt)
        return hexlify(ed25519.encodepoint(aG))

    def public_view_key(self):
        keyInt = ed25519.decodeint(unhexlify(self.secret_view_key()))
        aG = ed25519.scalarmultbase(keyInt)
        return hexlify(ed25519.encodepoint(aG))

    def public_address(self):
        data = str.encode("12") + self.public_spend_key() + self.public_view_key()
        h = keccak_256()
        h.update(unhexlify(data))
        checksum = str.encode(h.hexdigest())
        return base58.encode(data + checksum[0:8])


def get_checksum(phrase):
    """Given a mnemonic word string, return a string of the computed checksum.

    :rtype: str
    """
    phrase_split = phrase.split(" ")
    assert len(phrase_split) >= 12, "Not valid mnemonic phrase"
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
