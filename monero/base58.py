# MoneroPy - A python toolbox for Monero
# Copyright (C) 2016 The MoneroPy Developers.
#
# MoneroPy is released under the BSD 3-Clause license. Use and redistribution of
# this software is subject to the license terms in the LICENSE file found in the
# top-level directory of this distribution.
#
# Modified by emesik and rooterkyberian:
#  + optimized
#  + proper exceptions instead of returning errors as results

__alphabet = [
    ord(s) for s in "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
]
__b58base = 58
__UINT64MAX = 2 ** 64
__encodedBlockSizes = [0, 2, 3, 5, 6, 7, 9, 10, 11]
__fullBlockSize = 8
__fullEncodedBlockSize = 11


def _hexToBin(hex_):
    if len(hex_) % 2 != 0:
        raise ValueError("Hex string has invalid length: %d" % len(hex_))
    return [int(hex_[i : i + 2], 16) for i in range(0, len(hex_), 2)]


def _binToHex(bin_):
    return "".join("%02x" % int(b) for b in bin_)


def _uint8be_to_64(data):
    if not (1 <= len(data) <= 8):
        raise ValueError("Invalid input length: %d" % len(data))

    res = 0
    for b in data:
        res = res << 8 | b
    return res


def _uint64_to_8be(num, size):
    if size < 1 or size > 8:
        raise ValueError("Invalid input length: %d" % size)
    res = [0] * size

    twopow8 = 2 ** 8
    for i in range(size - 1, -1, -1):
        res[i] = num % twopow8
        num = num // twopow8

    return res


def encode_block(data, buf, index):
    l_data = len(data)

    if l_data < 1 or l_data > __fullEncodedBlockSize:
        raise ValueError("Invalid block length: %d" % l_data)

    num = _uint8be_to_64(data)
    i = __encodedBlockSizes[l_data] - 1

    while num > 0:
        remainder = num % __b58base
        num = num // __b58base
        buf[index + i] = __alphabet[remainder]
        i -= 1

    return buf


def encode(hex):
    """Encode hexadecimal string as base58 (ex: encoding a Monero address)."""
    data = _hexToBin(hex)
    l_data = len(data)

    if l_data == 0:
        return ""

    full_block_count = l_data // __fullBlockSize
    last_block_size = l_data % __fullBlockSize
    res_size = (
        full_block_count * __fullEncodedBlockSize + __encodedBlockSizes[last_block_size]
    )

    res = bytearray([__alphabet[0]] * res_size)

    for i in range(full_block_count):
        res = encode_block(
            data[(i * __fullBlockSize) : (i * __fullBlockSize + __fullBlockSize)],
            res,
            i * __fullEncodedBlockSize,
        )

    if last_block_size > 0:
        res = encode_block(
            data[
                (full_block_count * __fullBlockSize) : (
                    full_block_count * __fullBlockSize + last_block_size
                )
            ],
            res,
            full_block_count * __fullEncodedBlockSize,
        )

    return bytes(res).decode("ascii")


def decode_block(data, buf, index):
    l_data = len(data)

    if l_data < 1 or l_data > __fullEncodedBlockSize:
        raise ValueError("Invalid block length: %d" % l_data)

    res_size = __encodedBlockSizes.index(l_data)
    if res_size <= 0:
        raise ValueError("Invalid block size: %d" % res_size)

    res_num = 0
    order = 1
    for i in range(l_data - 1, -1, -1):
        digit = __alphabet.index(data[i])
        if digit < 0:
            raise ValueError("Invalid symbol: %s" % data[i])

        product = order * digit + res_num
        if product > __UINT64MAX:
            raise ValueError(
                "Overflow: %d * %d + %d = %d" % (order, digit, res_num, product)
            )

        res_num = product
        order = order * __b58base

    if res_size < __fullBlockSize and 2 ** (8 * res_size) <= res_num:
        raise ValueError("Overflow: %d doesn't fit in %d bit(s)" % (res_num, res_size))

    tmp_buf = _uint64_to_8be(res_num, res_size)
    buf[index : index + len(tmp_buf)] = tmp_buf

    return buf


def decode(enc):
    """Decode a base58 string (ex: a Monero address) into hexidecimal form."""
    enc = bytearray(enc, encoding="ascii")
    l_enc = len(enc)

    if l_enc == 0:
        return ""

    full_block_count = l_enc // __fullEncodedBlockSize
    last_block_size = l_enc % __fullEncodedBlockSize
    try:
        last_block_decoded_size = __encodedBlockSizes.index(last_block_size)
    except ValueError:
        raise ValueError("Invalid encoded length: %d" % l_enc)

    data_size = full_block_count * __fullBlockSize + last_block_decoded_size

    data = bytearray(data_size)
    for i in range(full_block_count):
        data = decode_block(
            enc[
                (i * __fullEncodedBlockSize) : (
                    i * __fullEncodedBlockSize + __fullEncodedBlockSize
                )
            ],
            data,
            i * __fullBlockSize,
        )

    if last_block_size > 0:
        data = decode_block(
            enc[
                (full_block_count * __fullEncodedBlockSize) : (
                    full_block_count * __fullEncodedBlockSize + last_block_size
                )
            ],
            data,
            full_block_count * __fullBlockSize,
        )

    return _binToHex(data)
