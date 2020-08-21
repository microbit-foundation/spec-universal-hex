# micro:bit Universal Hex DAPLink Tests

https://github.com/microbit-foundation/DAPLink-builds/tree/f0b80210f9bf0336ce36674454119a8843bf9e85/tests/fat-binaries

## Conclusions about DAPLink versions:

- All versions of DAPLink ignore record types after type 05
- All versions of DAPLink need the first hex line to be a valid Intel Hex record
- Version 0234 does not stop processing the file after the End-Of-File record
    - This is because the hex data is processed in blocks of 512 bytes, and the EoF record only stops processing the block which includes it, so subsequent blocks are still processed
- Version 0241+ will stop processing the file after the End-Of-File record
- Version 0241 to 0253 can only flash data in sequential addresses
    - If a hex record goes “back”, then DAPLink will stop and produces a fail.txt file
    - This could have been used in our advantage to write data mb1 data and then mb2 data without without an EOF record in the middle
        - However it produces a fail.txt and is not valid for newer DAPLink versions
        - Not a valid option
- Version 0234 and 0254+ can write to non-sequential addresses

## Current Proposition

Our current proposition contains data in this order in 512-byte blocks:

- Extended linear address record (first record needs to be valid Intel Hex)
- A record using a new record type for metadata
- micro:bit v1 flash data
- micro:bit v1 UICR data
- A record using a new record type for metadata
- micro:bit v2 flash data using a new record type
- micro:bit v2 UICR data using a new record type
- End-of-file record

This format:

- Works on micro:bit v1 DAPLink versions 0234 and newer
    - The undefined record types are ignored
- Needs updates on DAPLink for micro:bit v2 to know how to process the new record types used for metadata
