# micro:bit Fat Binaries DAPLink Tests

https://github.com/microbit-foundation/DAPLink-builds/tree/f0b80210f9bf0336ce36674454119a8843bf9e85/tests/fat-binaries

**Conclusions about DAPLink versions:**

- Version 0234 does not stop processing the file after the End-Of-File record
    - We don’t fully understand this behaviour yet
    - Still need to look into source code to see if there is a way to exploit this in our advantage
    - More info in https://github.com/microsoft/pxt-microbit/issues/1631
        - In essence this hex file contains: flash data + UICR data + EOF + data to RAM
        - The end result is a micro:bit with none of the flash data present, and some of the RAM data written to flash
        - We believe that it flashes the data, then after the EOF is encounter it does a full erase, and writes some of the RAM data into flash
- Version 0241+ will stop processing the file after the End-Of-File record
- Version 0241 to 0253 can only flash data in sequential addresses.
    - If a hex record goes “back”, then DAPLink will stop and produces a fail.txt file
    - This could have been used in our advantage to write data mb1 data and then mb2 data without without an EOF record in the middle
        - However it produces a fail.txt and is not valid for newer DAPLink versions
        - Not a valid option
- Version 0234 and 0254 can write to non-sequential addresses

**Current Proposition**
Our current proposition contains data in this order in 512-byte blocks:

- micro:bit v1 flash data
- micro:bit v1 UICR data
- End-of-file record 
- micro:bit v2 flash data
- micro:bit v2 UICR data
- End-of-file record 

This format:

- Works on micro:bit v1 DAPLink versions 0241 and newer
    - The undefined record types are ignored
- Fails completely on micro:bit v1 DAPLink version 0234
    - Flash data corrupted
    - UICR data corrupted
    - No fail.txt file produced
    - In some operating systems it produces a file-copy error
- Needs updates on DAPLink for micro:bit v2 to know how to process the undefined record types used for metadata
- Needs updates on DAPLink for micro:bit v2 to ignore the first end-of-file record
    - This record possibly needs to be wrapped in some metadata

