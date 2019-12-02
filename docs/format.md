# micro:bit Fat Binaries Format

Specification version 0.2.0.

## Intel Hex Record Types

In all the DAPLink versions we’ve [tested](tests.md) DAPLink ignores any Intel Hex record with an unrecognised record type.
We can use this to our advantage to pack micro:bit v2 data in unused record types that will be ignored in the deployed versions of DAPLink for micro:bit v1, and correctly processed in DAPLink for micro:bit v2.

## 512 Byte Blocks

USB packs and sends data in blocks of 512 bytes, in the case of out-of-order blocks, it would be useful to create a format that contains self-contained 512-byte blocks with metadata.
Furthermore, by making the first part of each 512-byte block contain header information, we can parse this and ‘throw away’ bocks not useful for the device we’re on.

## New Record Types

| Hex Code | Record Type | Description |
|----------|-------------|-------------|
| `0x0A`   | Block Start | First record in a 512-byte block |
| `0x0B`   | Block End   | Last record in a 512-byte block |
| `0x0C`   | Padded Data | Used to pad the block to the 512-bytes size, content can be discarded |
| `0x0D`   | Mbv2 Data   | Follows the same format as a normal data record (`0x00`), but contains micro:bit v2 data |

## Intel Hex Block Format Proposition

Conventional hex:

```
Extended Linear Address
X * Data records of N bytes (typically 16)
...
Extended Linear Address
Y * Data records of N bytes (typically 16)
...
End of file record
```

Proposed fat hex:

```
X * 512 byte "hex blocks" for micro:bit v1 each containing
{
    Start block record (`0x0A`), with metadata to identify micro:bit v1 block
    Extended Linear Address
    10 * normal data records (`0x00`) of 16 bytes
    Block end record (`0x0B`) with padding data
}
P * 512 byte "hex blocks" for micro:bit v2 each containing
{
    Start block record, with metadata to identify micro:bit v2 block
    Extended Linear Address
    10 * Mbv2 Data records (`0x0D`) of 16 bytes
    Block end record (`0x0B`) with padding data
}
End of file record/block (512 bytes, or compacted with previous block?)
```

As a proof-of-concept, a Python script has been used to convert a 'standard' micro:bit v1 Intel Hex file.
It breaks it down into blocks of 10 records with 16 bytes of data each (the original data records were 16 bytes already), and modifies each block to contain the following:

- Starts with Block Start custom record type `0x0A` to include some metadata
    - The data included in this case (`0xDEADC0DE`) is just a place-holder
    - The metadata should indicate the micro:bit version for the block
- Followed by an Extended Linear Address record
- Then the original 10 data records
    - micro:bit v1 data uses the standard Intel Hex data record (`0x00`)
    - micro:bit v2 data uses Mbv2 Data custom record type (`0D`)
- If the last block contains less than 10 data records it will add Padded Data records (`0x0C`)
- End with Block End custom record type (`0x0B`)
    - This type is used only to indicate the block is ending
    - The `0xDEADC0DE` data is only used to pad the block to  be 512 bytes long
- An end-of-file record can be included in the last 512 byte block of data

So this block of micro:bit v1 10 Intel Hex data records:

```
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
```

Becomes for micro:bit v1:

```
:0400000A01ADC0DEA6
:020000040000FA
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
```

And this block of 10 micro:bit v2 data records:

```
:1000000000040020E508000079050000C508000094
:10001000830500008D05000097050000000000002A
:1000200000000000000000000000000009090000BE
:10003000A105000000000000AB050000B5050000B0
:10004000BF050000C9050000D3050000DD05000064
:10005000E7050000F1050000FB05000005060000B3
:100060000F06000019060000230600002D06000000
:1000700037060000410600004B0600005506000050
:100080005F06000069060000730600007D060000A0
:1000900087060000910600009B060000A5060000F0
```

Becomes for micro:bit v2:

```
:0400000A02ADC0DEA5
:020000040000FA
:1000000D00040020E508000079050000C508000087
:1000100D830500008D05000097050000000000001D
:1000200D00000000000000000000000009090000B1
:1000300DA105000000000000AB050000B5050000A3
:1000400DBF050000C9050000D3050000DD05000057
:1000500DE7050000F1050000FB05000005060000A6
:1000600D0F06000019060000230600002D060000F3
:1000700D37060000410600004B0600005506000043
:1000800D5F06000069060000730600007D06000093
:1000900D87060000910600009B060000A5060000E3
:0C00000BDEADC0DEDEADC0DEDEADC0DE6E
```

And the last data block with an EoF record (`:00000001FF`) would look like this:

```
:0400000A02ADC0DEA5
:020000040000FA
:1000000D00040020E508000079050000C508000087
:1000100D830500008D05000097050000000000001D
:1000200D00000000000000000000000009090000B1
:1000300DA105000000000000AB050000B5050000A3
:1000400DBF050000C9050000D3050000DD05000057
:1000500DE7050000F1050000FB05000005060000A6
:1000600D0F06000019060000230600002D060000F3
:1000700D37060000410600004B0600005506000043
:00000001FF
:1000000CDEADC0DEDEADC0DEDEADC0DEDEADC0DE40
:0A00000CDEADC0DEDEADC0DEDEAD0D
:0C00000BDEADC0DEDEADC0DEDEADC0DE6E
```


This format can still be tweaked:

- The first metadata record could be longer to contain more data
- Then End Of Data record is included in the last block of the file and could be extracted to it's own block
    - Or if it truly is the end of the file it might not need to be in a 512-byte block
- Additional unused records can be used to included other types of data or metadata
    - Preferably we should include all metadata in the Block Start record, to reserve the rest of the record types
