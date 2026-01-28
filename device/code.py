import time
import board
import digitalio
import busio
import usb_hid
import displayio
import terminalio

try:
    from fourwire import FourWire
except ImportError:
    from displayio import FourWire

from adafruit_display_text import label
from adafruit_st7789 import ST7789
from adafruit_hid.mouse import Mouse
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS
from adafruit_hid.keycode import Keycode

# screen conf

displayio.release_displays()

# pins definitions
tft_clk = board.GP10
tft_mosi = board.GP11
tft_res = board.GP12
tft_dc = board.GP8
tft_cs = board.GP9
tft_bl = board.GP13

# SPI
spi = busio.SPI(clock=tft_clk, MOSI=tft_mosi)

# Display Bus
display_bus = FourWire(spi, command=tft_dc, chip_select=tft_cs, reset=tft_res)

# ST7789 config
display = ST7789(
    display_bus,
    width=240,
    height=240,
    rowstart=80,
    rotation=270,        # rotate screen to match orientation
    invert=True
)

backlight = digitalio.DigitalInOut(tft_bl)
backlight.direction = digitalio.Direction.OUTPUT
backlight.value = True

# keys

pins = {
    'JOY_UP': board.GP2,
    'JOY_DOWN': board.GP18,
    'JOY_LEFT': board.GP16,
    'JOY_RIGHT': board.GP20,
    'JOY_CENTER': board.GP3,
    'KEY_A': board.GP15,
    'KEY_B': board.GP17,
    'KEY_X': board.GP19,
    'KEY_Y': board.GP21,
}

buttons = {}
for name, pin in pins.items():
    btn = digitalio.DigitalInOut(pin)
    btn.direction = digitalio.Direction.INPUT
    btn.pull = digitalio.Pull.UP
    buttons[name] = btn

def is_pressed(name):
    return not buttons[name].value

mouse = Mouse(usb_hid.devices)
keyboard = Keyboard(usb_hid.devices)
layout = KeyboardLayoutUS(keyboard)

# states
MODE_MOUSE = 0
MODE_KEYBOARD = 1
current_mode = MODE_MOUSE

kbd_grid = [
    ['1','2','3','4','5','6','7','8','9','0'],
    ['Q','W','E','R','T','Y','U','I','O','P'],
    ['A','S','D','F','G','H','J','K','L',';'],
    ['Z','X','C','V','B','N','M',',','.','/'],
    ['SPACE', 'ENTER', 'ESC']
]
sel_row = 1
sel_col = 0
key_hold_active = False 

main_group = displayio.Group()
display.root_group = main_group

# ui

def draw_mouse_mode():
    while len(main_group) > 0: main_group.pop()
    
    text_area = label.Label(terminalio.FONT, text="MOUSE MODE", scale=3, color=0x00FF00)
    text_area.anchor_point = (0.5, 0.5)
    text_area.anchored_position = (120, 80)
    
    instr = label.Label(terminalio.FONT, text="Joy: Move\nA: L-Click  B: R-Click\nX: M-Click\nY: Switch Mode", scale=1, color=0xFFFFFF)
    instr.anchor_point = (0.5, 0.5)
    instr.anchored_position = (120, 160)
    
    main_group.append(text_area)
    main_group.append(instr)

def draw_keyboard_mode():
    while len(main_group) > 0: main_group.pop()
    
    title = label.Label(terminalio.FONT, text="KEYBOARD", scale=2, color=0x00FFFF)
    title.x = 70; title.y = 15
    main_group.append(title)
    
    start_y = 45; step_y = 35; step_x = 22
    
    for r_idx, row in enumerate(kbd_grid):
        for c_idx, char in enumerate(row):
            color = 0xFFFFFF
            if r_idx == sel_row and c_idx == sel_col:
                color = 0x00FF00
                if key_hold_active: color = 0xFF0000
            
            x_pos = 10 + (c_idx * step_x)
            y_pos = start_y + (r_idx * step_y)
            if r_idx == 4: x_pos = 20 + (c_idx * 70)
            
            lbl = label.Label(terminalio.FONT, text=char, scale=2, color=color)
            lbl.x = x_pos; lbl.y = y_pos
            main_group.append(lbl)

def get_keycode(char_str):
    if char_str == 'SPACE': return Keycode.SPACE
    if char_str == 'ENTER': return Keycode.ENTER
    if char_str == 'ESC': return Keycode.ESCAPE
    return None

# main loop
draw_mouse_mode()
last_move_time = 0

while True:
    now = time.monotonic()
    
    # Zmiana trybu (Y)
    if is_pressed('KEY_Y'):
        time.sleep(0.2)
        if current_mode == MODE_MOUSE:
            current_mode = MODE_KEYBOARD
            draw_keyboard_mode()
        else:
            current_mode = MODE_MOUSE
            keyboard.release_all()
            key_hold_active = False
            draw_mouse_mode()
        while is_pressed('KEY_Y'): pass

    if current_mode == MODE_MOUSE:
        mx, my = 0, 0
        speed = 5
        if is_pressed('JOY_UP'): my = -speed
        if is_pressed('JOY_DOWN'): my = speed
        if is_pressed('JOY_LEFT'): mx = -speed
        if is_pressed('JOY_RIGHT'): mx = speed
        
        if mx or my: mouse.move(x=mx, y=my)
        
        if is_pressed('KEY_A'):
            mouse.press(Mouse.LEFT_BUTTON)
            while is_pressed('KEY_A'): pass
            mouse.release(Mouse.LEFT_BUTTON)
        if is_pressed('KEY_B'):
            mouse.click(Mouse.RIGHT_BUTTON); time.sleep(0.2)
        if is_pressed('KEY_X'):
            mouse.click(Mouse.MIDDLE_BUTTON); time.sleep(0.2)

    elif current_mode == MODE_KEYBOARD:
        if now - last_move_time > 0.15:
            moved = False
            if is_pressed('JOY_UP'): sel_row = max(0, sel_row-1); moved=True
            if is_pressed('JOY_DOWN'): sel_row = min(4, sel_row+1); moved=True
            if is_pressed('JOY_LEFT'): sel_col = max(0, sel_col-1); moved=True
            if is_pressed('JOY_RIGHT'): sel_col = min(len(kbd_grid[sel_row])-1, sel_col+1); moved=True
            
            if sel_col >= len(kbd_grid[sel_row]): sel_col = len(kbd_grid[sel_row])-1
            
            if moved:
                draw_keyboard_mode()
                last_move_time = now

        sel_char = kbd_grid[sel_row][sel_col]

        if is_pressed('KEY_A'):
            kc = get_keycode(sel_char)
            if kc:
                keyboard.send(kc)
            else:
                if key_hold_active: layout.write(sel_char.upper())
                else: layout.write(sel_char.lower())
            
            if key_hold_active: # Opcjonalnie wyłącz Shift po 1 znaku
                key_hold_active = False
                draw_keyboard_mode()
            time.sleep(0.2)

        if is_pressed('KEY_B'):
            keyboard.send(Keycode.BACKSPACE); time.sleep(0.15)
            
        if is_pressed('KEY_X'):
            key_hold_active = not key_hold_active
            draw_keyboard_mode()
            time.sleep(0.3)

    time.sleep(0.01)