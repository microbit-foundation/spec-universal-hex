---
layout: page
title: Universal Hex Format Specification
heading: Universal Hex Format Specification
description: Specification for the micro:bit Universal Hex Format
permalink: /software/spec-universal-hex
ref: spec-universal-hex
lang: en
---

# 🌌 micro:bit Universal Hex Format Specification

Specification version 0.4.0.


## Goal

The goal of a micro:bit Universal Hex is to be able to create a single-file format that can be flashed into a micro:bit V1 and a micro:bit V2 successfully.


## Definitions and Rationale

<img align="right" src="https://tech.microbit.org/software/spec-universal-hex/spec/img/universal-hex.png" alt="universal hex">

Universal Hex is a superset of the Intel Hex file format to be able to contain binary code for multiple micro:bit boards or subsystems.

The microcontroller used in the micro:bit V2 (nRF52) is different than the microcontroller used in micro:bit V1 (nRF51), with a different architecture (Arm Cortex M0+ vs Cortex M4), slightly different peripherals, and different hardware components on the board.

The micro:bit V1 and V2 boards use an interface chip with the DAPLink firmware to flash the target microcontroller. DAPLink is responsible for processing the files dropped into the micro:bit MSD drive and any new file format has to be implemented in that project.

To easily support our users, we want the online editors to generate a single file that will work in both micro:bit V1 and micro:bit V2.

Therefore, a micro:bit Universal Hex is a file that contains the binary data for both micro:bit V1 and micro:bit V2, in a format that the DAPLink can process to only write to memory the data relevant to its board.


## Requirements

- shall: mandatory feature
- should: desired feature

1. The Universal Hex file shall flash correctly in a micro:bit V2 with any version of DAPLink
2. The Universal Hex file shall flash correctly on a micro:bit V1 with DAPLink v0234 or newer
4. The Universal Hex file flash time should be similar (+/- 10%) than the same microbit-v1-only hex file
5. The micro:bit v2 DAPLink interface shall also consume ‘standard’ Intel Hex and bin files for micro:bit V2 (eg produced by Mbed or other tools)


## DAPLink Interface Versions Shipped

- 0234: Version shipped in the original BBC drop, over 800K units with this version
- 0241: Version shipped in the v1.3B retail version
- 0249: Version shipped in micro:bit v1.5
- 0254: Latest official DAPLink version before this format was defined
- 0255: Version released with micro:bit v2

Conclusions about DAPLink versions:

- All versions of DAPLink ignore record types after type `0x05`
- All versions of DAPLink need the first hex line to be a valid Intel Hex record
- Version 0234 does not stop processing the file after the End-Of-File record
    - This is because the hex data is processed in blocks of 512 bytes, and the EoF record only stops processing the block which includes it, so subsequent blocks are still processed
- Version 0241+ will stop processing the file after the End-Of-File record
- Version 0241 to 0253 can only flash data in sequential addresses
    - If a hex record goes “back”, then DAPLink will stop and produces a fail.txt file
    - This could have been used to our advantage to write mb1 data and then mb2 data without an EOF record in the middle
        - However it produces a fail.txt and is not valid for newer DAPLink versions
        - So this does not meet our requirements
- Version 0234 and 0254+ can write to non-sequential addresses


## Intel Hex and Universal Hex relationship

The micro:bit Universal Hex format is a superset of the [Intel Hex file format](https://en.wikipedia.org/wiki/Intel_HEX) designed to be able to include data for multiple targets into a single file.

In all the DAPLink versions we’ve tested DAPLink ignores any Intel Hex record with an unrecognised record type.
The only exception is the first line of the hex file, which needs to be a valid Intel Hex record, otherwise the entire file is discarded.

This can be used to our advantage to pack micro:bit V2 data within unused record types that will be ignored in the deployed versions of DAPLink for micro:bit V1, and will be correctly processed in DAPLink for micro:bit V2.

The Universal Hex format builds on top of the Intel Hex format, and creates new records with un-used record type values.


## Universal Hex New Record Types

| Hex Code | Record Type | Data Length |Description |
|----------|-------------|-------------|-------------|
| `0x0A`   | Block Start | 2+ | Second record in a section/block, includes a "Data Type" ID in the data field |
| `0x0B`   | Block End   | 0+ | Last record in a section/block, can include padding data to be ignored|
| `0x0C`   | Padded Data | 0+ | Used to pad the section/block to the required alignment, data field content will be ignored |
| `0x0D`   | Custom Data | 0+ | Follows the same format as a normal data record (`0x00`), but contains data for the "Data Type" indicated in the Block Start record |
| `0x0E`   | Other Data  | 0+ | For other tools to embed additional data, to be ignored by DAPLink |

### Block Type

The `Block Start` record contains metadata to identify the kind of data contained in the subsequent Data (`0x00`) or Custom Data (`0x0D`) records.

The data field for this record has a minimum size of 2 bytes. The valid values for these two bytes are:

| Hex Code | Data Type    | Description |
|----------|--------------|-------------|
| `0x9900` | micro:bit V1 | Contains data for micro:bit V1 |
| `0x9903` | micro:bit V2 | Contains data for micro:bit V2 |

Additional data bytes can be included but will be ignored by DAPLink.


## Universal Hex Block/Section Format

There are two valid formats for packing the V1 and V2 records:

- 512 Byte Blocks
- 512 Byte Aligned Sections (recommended format)

USB packs and sends data in blocks of 512 bytes. As the DAPLink MSD drive could receive the hex file blocks out-of-order, it would be useful to create a format that contains self-contained 512-byte blocks with metadata.

Previous versions of this specification only defined the format described in the "512 Byte Blocks" section, but testing showed DAPLink 0234 was significantly slower to process this format.
For this reason the "512 Byte Aligned Sections" format was introduced and **is the currently recommended format**.

Receiving blocks out-of-order has not been an issue yet, but in case this becomes a problem in the future (e.g. an operating system update introduces this change), DAPLink will remain compatible with the "512 Byte Blocks" format, so that any online editors could switch to it without having to update the micro:bit firmware.

In both formats a Universal Hex must contain data for at least 2 targets, one for micro:bit V1, one for micro:bit V2, and any additional targets are optional. This is required because if DAPLink processes a file without data for its own target it will throw a hard to understand error.

### 512 Byte Blocks

> **This format is for future use only. The "512 Byte Aligned Sections" format should be used instead**.

This format can be found in the [format-deprecated.md](https://github.com/microbit-foundation/spec-universal-hex/blob/master/spec/format-deprecated.md) document, and while it is supported by DAPLink, it use is discouraged.

### 512 Byte Aligned Sections

DAPLink 0234 is very slow flashing Universal Hex files with the 512 byte block format.
This is caused by having an Extended Linear Address record present on each block.

Removing the Extended Linear Address record to reduce the flashing time makes the format susceptible to issues caused by file blocks arriving out of order.
So, if the blocks are no longer self contained and the file format depends on the blocks arriving in order, we can reduce the total file size by only adding the metadata record once per board "section", therefore reducing the flashing time even further.

A "section" in this format includes all the Data and Extended Linear Address records for a specific target. So a Universal Hex will have a micro:bit V1 section, and a V2 section.

To ensure a USB 512-byte block doesn't contain data for two targets, each section must be 512-byte aligned.

So, each target section:
- Is 512-byte aligned
- Starts with an Extended Linear Address record
- Followed by a Block Start custom record (`0x0A`)
    - This record type includes the target metadata in the Data field
- Then it includes all the data and Extended Linear Address (`0x04`) records for the target
    - micro:bit V1 data uses the standard Intel Hex data record (`0x00`)
    - Data for any other board, like the micro:bit V2, uses the Custom Data record type (`0x0D`)
    - Extended Segment Address records (`0x03`) are converted to Extended Linear Address (`0x04`) records
    - Start Segment Address (`0x03`) and Start Linear Address (`0x05`) records are excluded
- Padded Data records (`0x0C`) can be used to align the end of the section to a 512-byte boundary
- Ends with Block End custom record (`0x0B`)
    - This record type is used only to indicate the end of the section
    - Any data can be added to the Data field to pad the block, as it will be ignored

Note that the End Of File record is excluded from the sections, only one EoF record is include as the last record of the file.

It is also recommended to:
- Use Data or Custom Data records with 32 bytes in the Data field
    - The most common Data field sizes are 16 and 32 bytes
    - Although the Intel Hex format does not limit the data field length, DAPLink has a max length of 32 bytes
    - Having longer records reduces the overall file size and save up over a second of flashing time
- Place the micro:bit V1 Section first, followed by the micro:bit V2 Section
   - DAPLink versions < 255 only halt the target microcontroller when the first flash operation starts, so in the opposite order micro:bit V1 would flash the DAPLink LED a couple of seconds before the user program on the micro:bit stops running

#### Section Format In A Hex File

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

Universal Hex:

```
micro:bit V1 section, 512-byte aligned
{
    Extended Linear Address record (`0x04`)
    Start block record (`0x0A`), with "Block Type" set to "micro:bit V1"
    N * Extended Linear Address (`0x04`) or Data records (`0x00`)
    Optional Padded Data records (`0x0C`) to align to a 512-byte boundary
    Block end record (`0x0B`) with padding data
}
micro:bit V2 section, 512-byte aligned
{
    Extended Linear Address record (`0x04`)
    Start block record (`0x0A`), with "Block Type" set to "micro:bit V2"
    N * Extended Linear Address (`0x04`) or Custom Data records (`0x0D`)
    Optional Padded Data records (`0x0C`) to align to a 512-byte boundary
    Block end record (`0x0B`) with optional padding data
}
End of file record
```

#### Example

So this small Intel Hex file for micro:bit V1:

```
:020000040000FA                              <- Extended Linear Address record
:1000000000400020218E01005D8E01005F8E010006  <- Data records
:1000100000000000000000000000000000000000E0
:10002000000000000000000000000000618E0100E0
:100030000000000000000000638E0100658E0100DA
:10004000678E01005D3D000065950100678E01002F
:10005000678E010000000000218F0100678E010003
:1000600069E80000D59A0100D9930100678E01006C
:10007000678E0100678E0100678E0100678E0100A8
:020000040001F9                              <- Extended Linear Address record
:1000000003D13000F8BD4010F3E7331D0122180082  <- Data records
:10001000F8F7B2FD4460EFE7E4B30200F0B5070083
:1000200089B000201E000D00019215F0ECFB0E4B74
:020000041000EA                              <- Extended Linear Address record
:1010C0007CB0EE17FFFFFFFF0A0000000000E30006  <- Data records
:0C10D000FFFFFFFF2D6D0300000000007B
:0400000500018E2147                          <- Start Linear Address record
:00000001FF                                  <- End Of File record
```

And this small Intel Hex file for micro:bit V2:

```
:1000000000040020810A000015070000610A0000BA  <- Data records
:100010001F07000029070000330700000000000050
:10002000000000000000000000000000A50A000021
:100030003D070000000000004707000051070000D6
:100040005B070000650700006F07000079070000EC
:10005000830700008D07000097070000A10700003C
:10006000AB070000B5070000BF070000C90700008C
:020000023000CC                              <- Extended Segment Address record
:10000000440205004A0200003C020500FA0D00000F  <- Data records
:1000100064020500D20F000034020500B20E000099
:100020007C020500720D000070020500420B00000A
:10003000F80405004A0B0000F00405003A0B00002C
:020000020000FC                              <- Extended Segment Address record
:020000041000EA                              <- Extended Linear Address record
:081014000080070000E0070066                  <- Data records
:1010C0007CB0EE47FFFFFFFF0C0000000000530064
:0C10D000FFFFFFFF000000000000000018
:040000033000225156                          <- Start Segment Address
:00000001FF                                  <- End Of File record
```

Will transform into this Universal Hex:

```
:020000040000FA                                                              <- Extended Linear Address record
:0400000A9900C0DEBB                                                          <- Block Start record, 0x9900 Block Type
:2000000000400020218E01005D8E01005F8E010000000000000000000000000000000000F6  <- Data records
:20002000000000000000000000000000618E01000000000000000000638E0100658E0100EA   |
:20004000678E01005D3D000065950100678E0100678E010000000000218F0100678E010082   |
:2000600069E80000D59A0100D9930100678E0100678E0100678E0100678E0100678E010084   |
:020000040001F9                                                              <- Extended Linear Address record
:2000000003D13000F8BD4010F3E7331D01221800F8F7B2FD4460EFE7E4B30200F0B5070015  <- Data records
:2000200089B000201E000D00019215F0ECFB0E4B04D8                                 |
:020000041000EA                                                              <- Extended Linear Address record
:1C10C0007CB0EE17FFFFFFFF0A0000000000E300FFFFFFFF2D6D03000000000061          <- Data record
:2000000CFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF4  <- Padded Data records
:2000000CFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF4   |
:2000000CFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF4   |
:2000000CFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF4   |
:2000000CFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF4   |
:2000000CFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF4         |
:0000000BF5                                                                  <- Block End record
:020000040000FA                                                              <- Extended Linear Address record
:0400000A9903C0DEB8                                                          <- Block Start record, 0x9903 Block Type
:2000000D00040020810A000015070000610A00001F0700002907000033070000000000000D  <- Data records
:2000200D000000000000000000000000A50A00003D0700000000000047070000510700001A   |
:2000400D5B070000650700006F07000079070000830700008D07000097070000A10700006B   |
:2000600DAB070000B5070000BF070000C9070000CB                                   |
:020000040003F7                                                              <- Extended Linear Address record
:2000000D440205004A0200003C020500FA0D000064020500D20F000034020500B20E0000AB  <- Data records
:2000200D7C020500720D000070020500420B0000F80405004A0B0000F00405003A0B000059   |
:020000041000EA                                                              <- Extended Linear Address record
:0810140D0080070000E0070059                                                  <- Data record
:1C10C00D7CB0EE47FFFFFFFF0C00000000005300FFFFFFFF00000000000000004F           |
:2000000CFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF4  <- Padded Data records
:2000000CFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF4   |
:2000000CFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF4   |
:2000000CFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF4   |
:2000000CFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF4   |
:1600000BFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF5                      <- Block End record with padding
:00000001FF                                                                  <- End Of File record with a new line

```
