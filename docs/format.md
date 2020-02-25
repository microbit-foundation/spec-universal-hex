# micro:bit Fat Binaries Format

Specification version 0.2.0.

## Intel Hex Record Types

In all the DAPLink versions we’ve [tested](tests.md) DAPLink ignores any Intel Hex record with an unrecognised record type.
We can use this to our advantage to pack micro:bit v2 data in unused record types that will be ignored in the deployed versions of DAPLink for micro:bit v1, and will be correctly processed in DAPLink for micro:bit v2.

## 512 Byte Blocks

USB packs and sends data in blocks of 512 bytes, in the case of out-of-order blocks, it would be useful to create a format that contains self-contained 512-byte blocks with metadata.
Furthermore, by making the first part of each 512-byte block contain header information, we can parse this and ‘throw away’ bocks not useful for the device we’re on.

Unfortunately all version of DAPLink (up to version 0254 at the time of writing) will try to validate the first line of the Intel Hex file. If the record type in that line does not correspond to a valid Intel Hex record type (`0x00` to `0x05`), it will fail validation and the file won't be processed.
For this reason the first record of each block will be an Extended Linear Address record (`0x04`), and the second record will contain the block metadata.

## New Record Types

| Hex Code | Record Type | Description |
|----------|-------------|-------------|
| `0x0A`   | Block Start | Second record in a 512-byte block, includes a "Block Type" ID in the data field |
| `0x0B`   | Block End   | Last record in a 512-byte block |
| `0x0C`   | Padded Data | Used to pad the block to the 512-bytes size, content can be discarded |
| `0x0D`   | Custom Data | Follows the same format as a normal data record (`0x00`), but contains data for this "Block Type" that will be ignored by older versions of DAPLink|

## Block Type

The `Block Start` record contains metadata to identify what kind of data there is in this block.

| Hex Code | Block Type   | Description |
|----------|--------------|-------------|
| `0x9901` | micro:bit v1 | Contains data for micro:bit v1 |
| `0x9903` | micro:bit v2 | Contains data for micro:bit v2 |

## Intel Hex Block Format Proposition

Conventional hex:

```
Extended Linear Address record
X * Data records of N bytes (typically 16)
...
Extended Linear Address record
Y * Data records of N bytes (typically 16)
...
End of file record
```

Proposed fat hex:

```
X * 512 byte "hex blocks" for micro:bit v1 each containing
{
    Extended Linear Address record
    Start block record (`0x0A`), with "Block Type" set to "micro:bit v1"
    10 * normal Data records (`0x00`) of 16 bytes
    Block end record (`0x0B`) with padding data
}
P * 512 byte "hex blocks" for micro:bit v2 each containing
{
    Extended Linear Address record
    Start block record (`0x0A`), with "Block Type" set to "micro:bit v2"
    10 * Custom Data records (`0x0D`) of 16 bytes
    Block end record (`0x0B`) with padding data
}
End of file record
```

As a proof-of-concept, a Python script has been used to convert a 'standard' Intel Hex file.
It breaks it down into blocks of 10 records with 16 bytes of data each (the original data records were 16 bytes already), and modifies each block to contain the following:

- For each block of 10 data records:
    - Starts with an Extended Linear Address record
    - Followed by a Block Start custom record type `0x0A` and includes the "Block Type"
        - The last 4 bytes of the data field (`0xC0DE`) are just a place-holder
        - The metadata should indicate the micro:bit version for the block
    - Then the original 10 data records
        - micro:bit v1 data uses the standard Intel Hex data record (`0x00`)
        - Data for any other board, like the micro:bit v2, uses the Custom Data record type (`0D`)
    - If the last block contains less than 10 data records it will add Padded Data records (`0x0C`)
    - Ends with Block End custom record type (`0x0B`)
        - This type is used only to indicate the block is ending
        - The `0xDEADC0DE` data is only used to pad the block to be 512 bytes long
- The last 512-byte block is followed by an End Of File record and a new line

So this block of 10 Intel Hex data records:

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
:020000040000FA
:0400000A9901C0DEBA
:1000A000DF010000E9010000F3010000FD01000094
:1000B00007020000110200001B02000025020000E0
:1000C0001FB5C046C04600F0EFFA04B00FB41FBD24
:1000D00008205A49096809580847382057490968CB
:1000E000095808473C2055490968095808474020E5
:1000F0005249096809580847442050490968095875
:10010000084748204D490968095808474C204B4981
:10011000096809580847502048490968095808479C
:100120005420464909680958084758204349096836
:10013000095808475C204149096809580847602068
:0C00000BDEADC0DEDEADC0DEDEADC0DE6E
```

And for micro:bit v2:

```
:020000040000FA
:0400000A9903C0DEB8
:1000A00DDF010000E9010000F3010000FD01000087
:1000B00D07020000110200001B02000025020000D3
:1000C00D1FB5C046C04600F0EFFA04B00FB41FBD17
:1000D00D08205A49096809580847382057490968BE
:1000E00D095808473C2055490968095808474020D8
:1000F00D5249096809580847442050490968095868
:1001000D084748204D490968095808474C204B4974
:1001100D096809580847502048490968095808478F
:1001200D5420464909680958084758204349096829
:1001300D095808475C20414909680958084760205B
:0C00000BDEADC0DEDEADC0DEDEADC0DE6E
```

And an EoF record (`:00000001FF\n`) is placed after the last block, so it would look like this:

```
:020000040000FA
:0400000A9903C0DEB8
:1000A00DDF010000E9010000F3010000FD01000087
:1000B00D07020000110200001B02000025020000D3
:1000C00D1FB5C046C04600F0EFFA04B00FB41FBD17
:1000D00D08205A49096809580847382057490968BE
:1000E00D095808473C2055490968095808474020D8
:1000F00D5249096809580847442050490968095868
:1001000D084748204D490968095808474C204B4974
:1001100D096809580847502048490968095808478F
:1001200D5420464909680958084758204349096829
:1001300D095808475C20414909680958084760205B
:0C00000BDEADC0DEDEADC0DEDEADC0DE6E
:00000001FF

```

This format can still be tweaked:

- The "Block Start" record could be extended to include more metadata in the data field
- Additional unused records can be used to included other types of data or metadata
    - Preferably we should include all metadata in the "Block Start" record, to reserve the rest of the record types
- The "Block End" record is not currently used and is simply ignored in DAPLink
    - Updating DAPLink to read this record before flashing the block might be to intrusive, so might remove this record type
    - To mitigate partial blocks we could only flash "Custom data" records if there was a "Block Start" record in the same block
