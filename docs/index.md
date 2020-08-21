# 🌌 micro:bit Universal Hex

Specification version 0.4.0.

## Goal

The goal of a micro:bit Universal Hex is to be able to create a single-file format that can be flashed into a micro:bit v1 and a micro:bit v2 successfully.

## Definitions and Rationale

<img align="right" src="img/universal-hex.png" alt="universal hex">

Universal Hex is a superset of the Intel Hex file format to be able to contain binary code for multiple micro:bit boards or subsystems.

The microcontroller used in the micro:bit v2 (nRF52) is different than the microcontroller used in micro:bit v1 (nRF51), with a different architecture (Arm Cortex M0+ vs Cortex M4), slightly different peripherals, and different hardware components on the board.

The micro:bit v1 and v2 boards use an interface chip with the DAPLink firmware to flash the target microcontroller. DAPLink is responsible for processing the files dropped into the micro:bit MSD drive and any new file format has to be implemented in that project.

To easily support our users, we want the online editors to generate a single file that will work in both micro:bit v1 and micro:bit v2.

Therefore, a micro:bit Universal Hex is a file that contains the binary data for both micro:bit v1 and micro:bit v2, in a format that the DAPLink can process to only write to memory the data relevant to its board.

## Requirements

- shall: mandatory feature
- should: desired feature

1. The Universal Hex file shall flash correctly in a micro:bit v2 with any version of DAPLink
2. The Universal Hex file shall flash correctly on a micro:bit v1 with DAPLink v0234 or newer
4. The Universal Hex file flash time should be similar (+/- 10%) than the same microbit-v1-only hex file
5. The micro:bit v2 DAPLink interface shall also consume ‘standard’ Intel Hex and bin files for micro:bit v2 (eg produced by Mbed or other tools)

## DAPLink Interface Versions Shipped

- 0234: Version shipped in the original BBC drop, over 800K units with this version
- 0241: Version shipped in the v1.3B retail version
- 0249: Version shipped in micro:bit v1.5
- 0254: Latest version at the time of writing
- 0255: Version to be released with micro:bit v2
