# Pico-LCD-HID Controller

This project implements a Human Interface Device (HID) using a Raspberry Pi Pico and the Waveshare Pico-LCD-1.3 expansion module. It allows the device to act as a standard USB mouse and keyboard through a graphical user interface.

## Functionality

The software operates in two distinct modes, switchable via a dedicated hardware button.

### Mouse Mode

* Joystick: Controls 2D cursor movement.
* Key A: Left mouse button.
* Key B: Right mouse button.
* Key X: Middle mouse button (scroll click).

### Keyboard Mode

* Visual Grid: A QWERTY layout displayed on the LCD.
* Navigation: Joystick highlights the desired character.
* Key A: Sends the selected character to the host computer.
* Key B: Backspace.
* Key X: Shift toggle (switches between lowercase and uppercase).
* Special Keys: Support for Space, Enter, and Escape.

## Hardware Configuration

The project is designed for the Waveshare Pico-LCD-1.3 hat with the following pin mapping:

* Display (ST7789):
* SPI CLK: GP10
* SPI MOSI: GP11
* CS: GP9
* DC: GP8
* Reset: GP12
* Backlight: GP13


* Inputs:
* Joystick: GP2, GP18, GP16, GP20, GP3
* Buttons: GP15, GP17, GP19, GP21



## Requirements

### Software

* CircuitPython 10.x firmware.

### Required Libraries

The following libraries from the Adafruit CircuitPython Bundle must be placed in the `lib` folder:

* adafruit_display_text
* adafruit_st7789
* adafruit_hid
* fourwire (included in CircuitPython 10.x core)
