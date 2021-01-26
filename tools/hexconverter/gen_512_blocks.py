"""Script to generate hex files for testing mb1 and mbnext universal hex.

This code is not properly tested and will need more attention and clean up.
"""
from array import array
from binascii import hexlify, unhexlify
from collections import namedtuple


from hex_tools import Record, decode_record


def hex_file_512_blocks(ihex_lines):
    """Build a hex file with 512 blocks of ihex data including custom records.
    We assume normal hex files produced by MakeCode and MicroPython.
    """
    open_block_record = Record.custom(0x00, 0xA, [0xDE, 0xAD, 0xC0, 0xDE]) + '\n'
    end_block_record = Record.custom(0x00, 0xB, [0xDE, 0xAD, 0xC0, 0xDE] * 3) + '\n'
    full_dummy_record = Record.custom(0x00, 0xC, [0xDE, 0xAD, 0xC0, 0xDE] * 4) + '\n'
    start_flash_ela_record = Record.extended_linear_address(0x0000) + '\n'
    ela_record_start = start_flash_ela_record[:9]
    # Check ihex starts at 0, if not who knows what other oddities we'll find
    assert start_flash_ela_record == ihex_lines[0], \
        '\nexp: {}\ngot: {}'.format(start_flash_ela_record, ihex_lines[0])
    # Start building the lines for a new file with 512 byte blocks
    # We assume we have 10 full data records to begin with
    new_ihex_lines = [ihex_lines[0]] + [open_block_record] + ihex_lines[1:11] + [end_block_record]
    last_ela_record = start_flash_ela_record
    current_block = []

    def attach_block(block):
        nonlocal new_ihex_lines, current_block, last_ela_record
        nonlocal open_block_record, end_block_record
        new_ihex_lines += [last_ela_record, open_block_record]
        new_ihex_lines += current_block
        new_ihex_lines += [end_block_record]
        current_block = []

    line_number = 11
    while line_number < len(ihex_lines):
        line = ihex_lines[line_number]
        if not line.rstrip('\r\n'):
            continue
        if ela_record_start in line:
            # This line contains a extended linear address record, so fill up
            # the block with dummy data to reach the block boundary
            lines_needed = 10 - len(current_block)
            current_block += [full_dummy_record] * lines_needed
            # Close the block
            attach_block(current_block)
            last_ela_record = ihex_lines[line_number]
        elif len(line) != 44:
            # A full data record (16 Bytes) contains 43 characters + new line
            assert len(line) < 44, 'record line {} is too long: {}'.format(
                    line_number, len(line))
            # We assume the rest of the 16 Bytes can just be 0xFF
            record = decode_record(line)
            new_data = [0xFF] * (16 - record.record_length)
            new_data = record.data + array('B', new_data)
            new_record = Record.data(record.address, new_data) + '\n'
            current_block += [new_record]
        elif len(line) == 44:
            # Normal line, just add it
            current_block += [line]
        elif Record.eof() in line:
            # We are done, finish up the block
            attach_block(current_block)
            break
        else:
            raise Exception('Unexpected record in line {}'.format(line_number))
        if len(current_block) == 10:
            # Okay, we need to start wrapping this up
            attach_block(current_block)
        line_number += 1
    new_ihex_lines += [Record.eof() + '\n']
    return new_ihex_lines


def main():
    # Testing a file
    ihex_lines = []
    with open('../hex-files/mb1-icons-duck-umbrella.hex', 'r') as f:
        ihex_lines = f.readlines()
    new_ihex_lines = hex_file_512_blocks(ihex_lines)
    with open('mb1-icons-duck-umbrella-512-blocks.hex', 'w') as f:
        f.write(''.join(new_ihex_lines))
    print('Done :)')


if __name__ == '__main__':
    main()
