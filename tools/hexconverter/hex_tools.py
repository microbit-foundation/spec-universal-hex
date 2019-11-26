"""Tools to generate and read Intel Hex data.

This code is not properly tested and will need more attention and clean up.

Executing this file will drop you into an ipython REPL with access to these
helpers.
"""
from array import array
from binascii import hexlify, unhexlify
from collections import namedtuple

from intelhex.compat import array_tobytes, asstr, asbytes


# From IntelHex.Record, reduced and modified for our purposes, more record
# types can be found there
class Record(object):
    """Helper methods to build valid ihex records."""

    @staticmethod
    def _from_bytes(byte_list):
        """Takes a list of bytes, computes the checksum, and outputs the entire
        record as a string. bytes should be the hex record without the colon
        or final checksum.
        @param  byte_list   list of byte values so far to pack into record.
        @return             String representation of one HEX record
        """
        assert len(byte_list) >= 4
        # calculate checksum
        s = (-sum(byte_list)) & 0x0FF
        bin = array('B', byte_list + [s])
        return ':' + asstr(hexlify(array_tobytes(bin))).upper()

    @staticmethod
    def custom(offset=0x00, record_type=0x00, byte_list=[]):
        """Return a custom non-standard record.
        This constructs the full record, including the length information,
        the offset, the record type, and the checksum.
        @param  offset         Load offset of first byte.
        @param  record_type    A custom record type (don't use 0x00 to 0x05).
        @param  byte_list      list of byte values to pack into record.
        @return                String representation of one HEX record
        """
        assert 0 <= offset < 0x10000
        assert 0 < len(byte_list) < 0x100
        b = [len(byte_list),
             (offset >> 8) & 0x0FF,
             offset & 0x0FF,
             record_type]
        b += byte_list
        return Record._from_bytes(b)

    @staticmethod
    def data(offset=0x00, byte_list=[]):
        """Return Data record. This constructs the full record, including
        the length information, the record type (0x00), the
        checksum, and the offset.
        @param  offset       load offset of first byte.
        @param  byte_list    list of byte values to pack into record.
        @return              String representation of one HEX record
        """
        return Record.custom(offset, 0x00, byte_list)

    @staticmethod
    def eof():
        """Return End of File record as a string.
        @return         String representation of Intel Hex EOF record 
        """
        return ':00000001FF'

    @staticmethod
    def extended_linear_address(ulba):
        """Return Extended Linear Address Record.
        @param  ulba    Upper Linear Base Address.
        @return         String representation of Intel Hex ELA record.
        """
        b = [2, 0, 0, 0x04, (ulba >> 8) & 0x0FF, ulba & 0x0FF]
        return Record._from_bytes(b)


def decode_record(s):
    """Decode one record of HEX file."""
    s = s.rstrip('\r\n')
    if not s:
        raise Exception('Record line is empty.')

    record_length = None
    record_type = None
    address = None
    data = None

    if s[0] == ':':
        try:
            bin = array('B', unhexlify(asbytes(s[1:])))
        except (TypeError, ValueError):
            # this might be raised by unhexlify when odd hexascii digits
            raise Exception('Error decoding ascii digits.')
        length = len(bin)
        if length < 5:
            raise Exception('Not enough data in record line.')
    else:
        raise Exception('Record line does not start with ":".')

    crc = sum(bin)
    crc &= 0x0FF
    if crc != 0:
        raise Exception('Record checksum does not add up.')

    record_length = bin[0]
    if length != (5 + record_length):
        raise Exception('Record length calculation does not add up.')

    address = (bin[1] << 8) | bin[2]
    record_type = bin[3]
    data = bin[4:-1]

    RecordData = namedtuple('RecordData', 'record_type record_length address data')
    record_data = RecordData(record_type, record_length, address, data)
    return record_data


def main():
    # Printing a couple of useful records for testing
    print('Quick reference quick record lines for test:')
    print(Record.custom(0x00, 0xA, [0xDE, 0xAD, 0xC0, 0xDE]))
    print(Record.custom(0x00, 0xB, [0xDE, 0xAD, 0xC0, 0xDE] * 3))
    print('-' * 79)

    # Drop into the iPython REPl
    import IPython
    IPython.embed()


if __name__ == '__main__':
    main()
