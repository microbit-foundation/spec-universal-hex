# Deprecated Format

The [format](format.md) document contains the latest version of the Universal
Hex format that should be used.

The format included in this document is supported in DAPLink only in case it
is needed in the future, but currently its use is discouraged.

## Block/Section Format

### 512 Byte Blocks

> **This format is for future use only. The "512 Byte Aligned Sections" format should be used instead**.

Grouping the Universal Hex records into self-contained 512-byte blocks overcomes issues arising from receiving file blocks out of order.
Furthermore, by making the first part of each 512-byte block contain header metadata, DAPLink can parse this information on every block and ‘throw away’ irrelevant blocks for its target.

Unfortunately all version of DAPLink (up to version 0254 at the time of writing) will try to validate the first line of the Intel Hex file. If the record type in that line does not correspond to a valid Intel Hex record type (`0x00` to `0x05`), it will fail validation and the file won't be processed.
For this reason the first record of each block will be an Extended Linear Address record (`0x04`), and the second record will contain the block metadata in the Block start record.

#### Block Format In A Hex File

> **This format is for future use only. The "512 Byte Aligned Sections" format should be used instead**.

Conventional Intel Hex for micro:bit V1 or V2:

```
Extended Linear Address record (optional if the data starts at address 0x0000_xxxx)
X * Data records of N bytes (typically 16)
...
Extended Linear Address record
Y * Data records of N bytes (typically 16)
...
End of file record
```

Universal Hex for micro:bit v1 and v2 with 512-byte blocks:

```
N * blocks of 512 bytes for micro:bit v1, each containing
{
    Extended Linear Address record
    Start block record (`0x0A`), with "Block Type" set to "micro:bit v1"
    N * normal Data records (`0x00`) of 16 bytes or 32 bytes, or Extended Linear Address records (`0x04`)
    Block end record (`0x0B`) with padding data
}
N * blocks of 512 bytes for micro:bit v2 each containing
{
    Extended Linear Address record
    Start block record (`0x0A`), with "Block Type" set to "micro:bit v2"
    N * Custom Data records (`0x0D`) of 16 bytes or 32 bytes, or Extended Linear Address records (`0x04`)
    Block end record (`0x0B`) with padding data
}
End of file record
```

#### Block Examples

> **This format is for future use only. The "512 Byte Aligned Sections" format should be used instead**.

This block of 10 Intel Hex data records:

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
:020000040000FA                              <- Extended Linear Address record
:0400000A9900C0DEBB                          <- Block Start record with 0x9901 Block Type
:1000A000DF010000E9010000F3010000FD01000094  <- Intel Hex data records
:1000B00007020000110200001B02000025020000E0
:1000C0001FB5C046C04600F0EFFA04B00FB41FBD24
:1000D00008205A49096809580847382057490968CB
:1000E000095808473C2055490968095808474020E5
:1000F0005249096809580847442050490968095875
:10010000084748204D490968095808474C204B4981
:10011000096809580847502048490968095808479C
:100120005420464909680958084758204349096836
:10013000095808475C204149096809580847602068
:0C00000BDEADC0DEDEADC0DEDEADC0DE6E          <- Block End record with padding
```

And for micro:bit v2:

```
:020000040000FA                              <- Extended Linear Address record
:0400000A9903C0DEB8                          <- Block Start record with 0x9903 Block Type
:1000A00DDF010000E9010000F3010000FD01000087  <- Custom Data records
:1000B00D07020000110200001B02000025020000D3
:1000C00D1FB5C046C04600F0EFFA04B00FB41FBD17
:1000D00D08205A49096809580847382057490968BE
:1000E00D095808473C2055490968095808474020D8
:1000F00D5249096809580847442050490968095868
:1001000D084748204D490968095808474C204B4974
:1001100D096809580847502048490968095808478F
:1001200D5420464909680958084758204349096829
:1001300D095808475C20414909680958084760205B
:0C00000BDEADC0DEDEADC0DEDEADC0DE6E          <- Block End record with padding
```

And an EoF record (`:00000001FF\n`) is placed after the last block, so the last block would look like this:

```
:020000040000FA                              <- Extended Linear Address record
:0400000A9903C0DEB8                          <- Block Start record with 0x9903 Block Type
:1000A00DDF010000E9010000F3010000FD01000087  <- Custom Data records
:1000B00D07020000110200001B02000025020000D3
:1000C00D1FB5C046C04600F0EFFA04B00FB41FBD17
:1000D00D08205A49096809580847382057490968BE
:1000E00D095808473C2055490968095808474020D8
:1000F00D5249096809580847442050490968095868
:1001000D084748204D490968095808474C204B4974
:1001100D096809580847502048490968095808478F
:1001200D5420464909680958084758204349096829
:1001300D095808475C20414909680958084760205B
:0C00000BDEADC0DEDEADC0DEDEADC0DE6E          <- Block End record with padding (to fit 512-bytes)
:00000001FF                                  <- End Of File record with a new line

```
