# micro:bit Fat Binaries Format

## Intel Hex Record Types

In all the DAPLink versions we’ve tested DAPLink ignores any Intel Hex record with an unrecognised record type.
We can use this to our advantage to include metadata in unused record types that will be ignored in the deployed versions of DAPLink for micro:bit v1, and processed in DAPLink for micro:bit v2.

## 512 Byte Blocks

USB packs and sends data in blocks of 512 bytes, in the case of out-of-order blocks, it would be useful to create a format that contains self-contained 512-byte blocks with metadata.
Furthermore, by making the first part of each 512-byte block contain header information, we can parse only this and ‘throw away’ bocks not useful for the device we’re on.

## 512 Bytes Blocks in Intel Hex Format with Unused Record Types

Conventional hex:

    Extended Linear Address
    X * Data lines of N bytes (typically 16)
    ...
    
    Extended Linear Address
    Y * Data lines of N bytes (typically 16)
    ...
    End of file record

Proposed Fat hex:

    X * 512 byte "hex blocks" for micro:bit v1 each containing
    {
      Extended Linear Address
      Header metadata record 
      10* 16 byte lines
      Block end record (& padding)
    }
    End of file record/block (512 bytes, or compacted with previous block?)
    P * 512 byte "hex blocks" for micro:bit v2 each containing
    {
      Extended Linear Address
      Header metadata record 
      10* 16 byte lines
      Block end record (& padding)
    }
    End of file record/block (512 bytes, or compacted with previous block?)


As an initial test, a Python script has been used to convert a ‘standard’ micro:bit v1 Intel Hex file, broke it down in blocks of 10 records with 16 bytes of data each (the original data records were 16 bytes already), and modify each block to contain the following:

- Start with an Extended Linear Address record
- Follow with an undefined record type `0x0A` to include some metadata
    - This could indicate the block of records is for a specific micro:bit version 
    - Any other record type could be used
    - The data included in this case (`0xDEADC``0``DE`) is just a placeholder
- Then the original 10 Intel Hex data records
- End with another undefined record type (`0x0B`)
    - In this case the record type is used only to indicate the block is ending
    - The `0xDEADC``0``DE` data in this case is only used to pad the block to  be 512 bytes long
    - It might only need to indicate this is the end of block

So this block of 10 Intel Hex data records:

    :10000000C0070000D1060000D1000000B1060000CA
    :1000100000000000000000000000000000000000E0
    :100020000000000000000000000000005107000078
    :100030000000000000000000DB000000E500000000
    :10004000EF000000F9000000030100000D010000B6
    :1000500017010000210100002B0100003501000004
    :100060003F01000049010000530100005D01000054
    :1000700067010000710100007B01000085010000A4
    :100080008F01000099010000A3010000AD010000F4
    :10009000B7010000C1010000CB010000D501000044

Becomes:

    :020000040000FA
    :0400000ADEADC0DEC9
    :10000000C0070000D1060000D1000000B1060000CA
    :1000100000000000000000000000000000000000E0
    :100020000000000000000000000000005107000078
    :100030000000000000000000DB000000E500000000
    :10004000EF000000F9000000030100000D010000B6
    :1000500017010000210100002B0100003501000004
    :100060003F01000049010000530100005D01000054
    :1000700067010000710100007B01000085010000A4
    :100080008F01000099010000A3010000AD010000F4
    :10009000B7010000C1010000CB010000D501000044
    :0C00000BDEADC0DEDEADC0DEDEADC0DE6E

This format could be tweaked:

- The first metadata record could be the first line, and the Extended Linear Address record the second line
- The first metadata record could be longer to contain more data
- Currently there isn’t any metadata wrapping the end of file record
- Additional unused records can be used to included other types of data
