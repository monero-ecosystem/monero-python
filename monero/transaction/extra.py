import binascii
import six
import varint


class ExtraParser(object):
    TX_EXTRA_TAG_PADDING = 0x00
    TX_EXTRA_TAG_PUBKEY = 0x01
    TX_EXTRA_TAG_EXTRA_NONCE = 0x02
    TX_EXTRA_TAG_ADDITIONAL_PUBKEYS = 0x04
    KNOWN_TAGS = (
        TX_EXTRA_TAG_PADDING,
        TX_EXTRA_TAG_PUBKEY,
        TX_EXTRA_TAG_EXTRA_NONCE,
        TX_EXTRA_TAG_ADDITIONAL_PUBKEYS,
    )

    def __init__(self, extra):
        if isinstance(extra, str):
            extra = binascii.unhexlify(extra)
        if isinstance(extra, bytes):
            extra = list(extra)
        self.extra = extra

    def parse(self):
        self.data = {}
        self.offset = 0
        self._parse(self.extra)
        return self.data

    def _strip_padding(self, extra):
        while extra and extra[0] == self.TX_EXTRA_TAG_PADDING:
            extra = extra[1:]
            self.offset += 1
        return extra

    def _pop_pubkey(self, extra):
        key = bytes(bytearray(extra[:32]))  # bytearray() is for py2 compatibility
        if len(key) < 32:
            raise ValueError(
                "offset {:d}: only {:d} bytes of key data, expected 32".format(
                    self.offset, len(key)
                )
            )
        if "pubkeys" in self.data:
            self.data["pubkeys"].append(key)
        else:
            self.data["pubkeys"] = [key]
        extra = extra[32:]
        self.offset += 32
        return extra

    def _extract_pubkey(self, extra):
        if extra:
            if extra[0] == self.TX_EXTRA_TAG_PUBKEY:
                extra = extra[1:]
                self.offset += 1
                extra = self._pop_pubkey(extra)
            elif extra[0] == self.TX_EXTRA_TAG_ADDITIONAL_PUBKEYS:
                extra = extra[1:]
                self.offset += 1
                keycount = varint.decode_bytes(bytearray(extra))
                valen = len(varint.encode(keycount))
                extra = extra[valen:]
                self.offset += valen
                for i in range(keycount):
                    extra = self._pop_pubkey(extra)
        return extra

    def _extract_nonce(self, extra):
        if extra and extra[0] == self.TX_EXTRA_TAG_EXTRA_NONCE:
            noncelen = extra[1]
            extra = extra[2:]
            self.offset += 2
            if noncelen > len(extra):
                raise ValueError(
                    "offset {:d}: extra nonce exceeds field size".format(self.offset)
                )
                return []
            nonce = bytearray(extra[:noncelen])
            if "nonces" in self.data:
                self.data["nonces"].append(nonce)
            else:
                self.data["nonces"] = [nonce]
            extra = extra[noncelen:]
            self.offset += noncelen
        return extra

    def _parse(self, extra):
        while extra:
            if extra[0] not in self.KNOWN_TAGS:
                raise ValueError(
                    "offset {:d}: unknown tag 0x{:x}".format(self.offset, extra[0])
                )
            extra = self._strip_padding(extra)
            extra = self._extract_pubkey(extra)
            extra = self._extract_nonce(extra)
