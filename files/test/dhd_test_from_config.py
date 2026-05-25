#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
DHD LED Test using milkyway-config.json

- Uses the same DHD settings as the Stargate (serial port, colors)
- For tests, forces brightness to ~75% of max (about 191/255)
- Does NOT modify any original project files
- Tests included:
  1. Center pixel test
  2. Brightness sweep (symbols)
  3. Full-ring gradient
  4. Ring chase (snake effect)
  5. Random strobe
"""

import os
import sys
import colorsys
import time
import json
import random

# ----------------------------------------------------------------------
# Global test brightness (~75% of 255)
# ----------------------------------------------------------------------
TEST_BRIGHTNESS = int(255 * 0.75)  # 191


# ----------------------------------------------------------------------
# 1. Fix sys.path so that "classes" can be imported
# ----------------------------------------------------------------------

THIS_DIR = os.path.dirname(os.path.abspath(__file__))       # …/sg1_v4/test
PROJECT_ROOT = os.path.dirname(THIS_DIR)                    # …/sg1_v4

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Import using the same structure as the main Stargate code
from classes.StargateMilkyWay.dialers import DHDv2  # type: ignore


# ----------------------------------------------------------------------
# 2. Simple logger compatible with Stargate logging calls
# ----------------------------------------------------------------------

class DummyLog:
    def log(self, msg: str):
        print(f"[LOG] {msg}")


# ----------------------------------------------------------------------
# 3. Load milkyway-config.json
# ----------------------------------------------------------------------

CONFIG_PATH = os.path.join(PROJECT_ROOT, "config", "milkyway-config.json")

def load_config() -> dict:
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


# ----------------------------------------------------------------------
# 4. Create DHDv2 instance using the config
# ----------------------------------------------------------------------

def create_dhd():
    cfg = load_config()
    log = DummyLog()

    # Serial port and baud rate
    port = cfg["dhd_serial_port"]["value"]
    baud = cfg["dhd_serial_baud_rate"]["value"]

    log.log(f"Using DHD port: {port}")
    log.log(f"Using baud rate: {baud}")

    dhd = DHDv2(port, baud, log)

    # Brightness from config (for info only)
    brightness_center_cfg = cfg["dhd_brightness_center"]["value"]
    brightness_symbols_cfg = cfg["dhd_brightness_symbols"]["value"]
    log.log(
        f"Config brightness: center={brightness_center_cfg}, "
        f"symbols={brightness_symbols_cfg}"
    )

    # Force test brightness to ~75% of max
    dhd.set_brightness_center(TEST_BRIGHTNESS)
    dhd.set_brightness_symbols(TEST_BRIGHTNESS)
    log.log(f"TEST brightness set to {TEST_BRIGHTNESS} (~75% of 255)")

    # Colors from config
    center_color = (
        cfg["dhd_color_center_red"]["value"],
        cfg["dhd_color_center_green"]["value"],
        cfg["dhd_color_center_blue"]["value"],
    )
    symbols_color = (
        cfg["dhd_color_symbols_red"]["value"],
        cfg["dhd_color_symbols_green"]["value"],
        cfg["dhd_color_symbols_blue"]["value"],
    )

    dhd.set_color_center(center_color)
    dhd.set_color_symbols(symbols_color)
    log.log(f"Set center color:  {center_color}")
    log.log(f"Set symbols color: {symbols_color}")

    # Clear LEDs on startup
    dhd.clear_all_pixels()
    dhd.latch()

    return dhd, log


# ----------------------------------------------------------------------
# 5. LED Tests
# ----------------------------------------------------------------------

def test_center_pixel(dhd: DHDv2, log: DummyLog):
    log.log("Test 1: Center pixel ON (using config color)")
    dhd.clear_all_pixels()
    dhd.set_center_on()
    time.sleep(2)
    dhd.clear_all_pixels()
    dhd.latch()
    time.sleep(0.5)


def test_brightness_sweep(dhd: DHDv2, log: DummyLog):
    log.log("Test 2: Brightness sweep (symbols)")

    dhd.clear_all_pixels()
    test_color = (255, 100, 0)  # Color used during brightness stepping

    # Sweep up to TEST_BRIGHTNESS (75% of max), not 255
    steps = [10, 40, 80, 120, 160, TEST_BRIGHTNESS]

    for b in steps:
        log.log(f"  brightness_symbols = {b}")
        dhd.set_brightness_symbols(b)
        dhd.set_all_pixels_to_color(*test_color)
        dhd.latch()
        time.sleep(1.0)

    # Restore base test brightness
    dhd.set_brightness_symbols(TEST_BRIGHTNESS)
    dhd.clear_all_pixels()
    dhd.latch()
    time.sleep(0.5)
    

def test_individual_leds(dhd: DHDv2, log: DummyLog):
    """
    Test 6: Individual LED RGB test

    Each LED is turned on one by one:
      - Red for 1.5s
      - Green for 1.5s
      - Blue for 1.5s
    Then we move to the next LED, until all LEDs on the DHD are tested.
    """

    log.log("Test 6: Individual LED RGB test")

    count = dhd.get_pixel_count()
    if count <= 0:
        log.log("  ERROR: get_pixel_count() == 0. Aborting.")
        return

    # Loop through all LEDs on the DHD
    for idx in range(count):
        # For each LED, show R, G, B for 1.5s each
        for (r, g, b, color_name) in [
            (255, 0,   0,   "RED"),
            (0,   255, 0,   "GREEN"),
            (0,   0,   255, "BLUE"),
        ]:
            log.log(f"  LED {idx}: {color_name}")
            dhd.clear_all_pixels()
            dhd.set_pixel_use_led_id(idx, r, g, b)
            dhd.latch()
            time.sleep(1.5)

    # Cleanup at the end
    dhd.clear_all_pixels()
    dhd.latch()
    time.sleep(0.5)

    
def test_gradient(dhd: DHDv2, log: DummyLog):
    log.log("Test 3: Full-ring hue rainbow gradient")

    count = dhd.get_pixel_count()
    log.log(f"  Pixel count reported by DHD: {count}")

    if count <= 0:
        log.log("  ERROR: get_pixel_count() == 0. Aborting gradient test.")
        return

    dhd.clear_all_pixels()

    for i in range(count):
        # Hue from 0.0 to 1.0 – full 360°
        h = i / max(1, count - 1)   # 0.0 .. 1.0
        s = 1.0                     # full saturation
        v = 1.0                     # full brightness (scaled by TEST_BRIGHTNESS)

        r_f, g_f, b_f = colorsys.hsv_to_rgb(h, s, v)
        r = int(r_f * 255)
        g = int(g_f * 255)
        b = int(b_f * 255)

        dhd.set_pixel_use_led_id(i, r, g, b)

    dhd.latch()
    time.sleep(6)

    dhd.clear_all_pixels()
    dhd.latch()
    time.sleep(0.5)


def test_ring_chase(dhd: DHDv2, log: DummyLog):
    log.log("Test 4: Ring chase (one rotation per color)")

    count = dhd.get_pixel_count()
    if count <= 0:
        log.log("  ERROR: get_pixel_count() == 0. Aborting.")
        return

    tail = 4  # fading trail

    colors = [
        (255, 0, 0),     # red
        (0, 255, 0),     # green
        (0, 0, 255),     # blue
        (240, 200, 0),   # yellow
        (180, 180, 180)  # white
    ]

    # --- Now one full loop for each color ---
    for color in colors:

        log.log(f"  Ring chase color: {color}")

        for head in range(count):
            dhd.clear_all_pixels()

            for i in range(tail):
                idx = (head - i) % count
                fade = max(0.2, 1.0 - i / tail)
                r = int(color[0] * fade)
                g = int(color[1] * fade)
                b = int(color[2] * fade)

                dhd.set_pixel_use_led_id(idx, r, g, b)

            dhd.latch()
            time.sleep(0.05)

    dhd.clear_all_pixels()
    dhd.latch()
    time.sleep(0.5)


def test_random_strobe(dhd: DHDv2, log: DummyLog):
    log.log("Test 5: Random strobe")

    count = dhd.get_pixel_count()
    iterations = 80

    for _ in range(iterations):
        dhd.clear_all_pixels()

        for _ in range(random.randint(4, 10)):
            idx = random.randint(0, max(0, count - 1))
            color = random.choice([
                (255, 0, 0),       # red
                (0, 255, 0),       # green
                (0, 0, 255),       # blue
                (255, 255, 0),     # yellow
                (255, 255, 255),   # white
            ])
            dhd.set_pixel_use_led_id(idx, *color)

        dhd.latch()
        time.sleep(0.05)

    dhd.clear_all_pixels()
    dhd.latch()
    time.sleep(0.5)


# ----------------------------------------------------------------------
# 6. main()
# ----------------------------------------------------------------------

def main():
    print("=== DHD LED Test using milkyway-config.json ===")
    print("Make sure stargate.service is stopped (serial must be free).")

    dhd, log = create_dhd()

    try:
        test_center_pixel(dhd, log)
        test_brightness_sweep(dhd, log)
        test_individual_leds(dhd, log)
        test_gradient(dhd, log)
        test_ring_chase(dhd, log)
        test_random_strobe(dhd, log)

        log.log("All tests completed.")
    finally:
        log.log("Clearing DHD...")
        dhd.clear_all_pixels()
        dhd.latch()
        time.sleep(0.5)


if __name__ == "__main__":
    main()


# ===== BACKEND FOR WEB-TRIGGERED LED TEST =====

class dhd_led_test_backend:
    """Backend used when the test is triggered from the web UI (debug.htm)."""

    @staticmethod
    def run_dhd_test(dhd, log, mode="full"):
        log.log(f"=== DHD LED TEST BACKEND START (mode={mode}) ===")

        try:
            # Force brightness for web-triggered tests as well
            try:
                dhd.set_brightness_center(TEST_BRIGHTNESS)
                dhd.set_brightness_symbols(TEST_BRIGHTNESS)
                log.log(
                    f"DHD LED TEST: brightness set to {TEST_BRIGHTNESS} (~75% of 255)"
                )
            except Exception as e_b:
                log.log(f"DHD LED TEST: could not set brightness: {e_b}")

            if mode == "center":
                test_center_pixel(dhd, log)

            elif mode == "brightness":
                test_brightness_sweep(dhd, log)

            elif mode == "gradient":
                test_gradient(dhd, log)

            elif mode == "ring_chase":
                test_ring_chase(dhd, log)

            elif mode == "random_strobe":
                test_random_strobe(dhd, log)

            elif mode == "individual":
                test_individual_leds(dhd, log)

            else:
                # "full" or unknown -> run complete suite
                test_center_pixel(dhd, log)
                test_brightness_sweep(dhd, log)
                test_gradient(dhd, log)
                test_ring_chase(dhd, log)
                test_random_strobe(dhd, log)
                test_individual_leds(dhd, log)

            log.log("=== DHD LED TEST BACKEND DONE ===")

        except Exception as e:
            log.log(f"DHD TEST BACKEND ERROR: {e}")

        finally:
            # Always clear LEDs at the end, even on error.
            try:
                dhd.clear_all_pixels()
                dhd.latch()
            except Exception as e2:
                log.log(f"DHD TEST BACKEND CLEANUP ERROR: {e2}")
