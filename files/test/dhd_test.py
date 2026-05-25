#!/usr/bin/env python3
from classes.DHD import DHDv2
from time import sleep

# Initiate the DHD object.
dhd_port = "/dev/serial/by-id/usb-Adafruit_ItsyBitsy_32u4_5V_16MHz_HIDPC-if00"
dhd_serial_baud_rate = 115200
dhd = DHDv2(dhd_port, dhd_serial_baud_rate)

# Brightness + clear
dhd.setBrightnessCenter(100)
dhd.setBrightnessSymbols(3)
dhd.setAllPixelsToColor(0, 0, 0)
dhd.latch()

# Run through all the DHD key lights (by LED ID)
for led_id in reversed(range(1, 39)):
    dhd.setPixel_use_LED_id(led_id, 250, 117, 0)
    dhd.latch()
    sleep(0.15)
    dhd.setPixel_use_LED_id(led_id, 0, 0, 0)
    dhd.latch()

# Centre button (LED ID 0)
dhd.setPixel_use_LED_id(0, 255, 0, 0)
dhd.latch()
sleep(2)
dhd.setAllPixelsToColor(0, 0, 0)
dhd.latch()

# Key -> LED ID map (your original map already matches LED IDs: 1..38 and center 0)
key_led_id_map = {
    '8':1, 'C':2, 'V':3, 'U':4, 'a':5, '3':6, '5':7, 'S':8, 'b':9, 'K':10, 'X':11, 'Z':12,
    'E':14, 'P':15, 'M':16, 'D':17, 'F':18, '7':19, 'c':20, 'W':21, '6':22, 'G':23, '4':24,
    'B':25, 'H':26, 'R':27, 'L':28, '2':29, 'N':30, 'Q':31, '9':32, 'J':33, '0':34, 'O':35,
    'T':36, 'Y':37, '1':38, 'I':39, 'A':0
}

def ask_for_input():
    """
    Toggle LEDs by LED ID (NOT pixel index). This keeps inner/outer ring correct.
    """
    def key_press():
        import sys, tty, termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

    active = set()  # active LED IDs

    while True:
        key = key_press()

        if key not in key_led_id_map:
            # ignore unknown keys
            continue

        led_id = key_led_id_map[key]

        if led_id not in active:
            active.add(led_id)
            if led_id == 0:
                dhd.setPixel_use_LED_id(0, 255, 0, 0)
            else:
                dhd.setPixel_use_LED_id(led_id, 250, 117, 0)
            dhd.latch()
        else:
            active.remove(led_id)
            dhd.setPixel_use_LED_id(led_id, 0, 0, 0)
            dhd.latch()

ask_for_input()