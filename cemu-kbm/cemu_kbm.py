"""
cemu-kbm: Keyboard + Mouse -> virtual Xbox 360 controller for Cemu (Wii U Minecraft)
Requires: ViGEmBus driver, `pip install -r requirements.txt`. Windows only.
"""
import ctypes
import time
from ctypes import wintypes

import vgamepad as vg
from pynput import mouse

# ---------------- CONFIG ----------------
SENSITIVITY = 0.06     # raise for faster camera, lower for slower
INVERT_Y = False
POLL_HZ = 120
TOGGLE_KEY = 0x77      # F8

# Virtual-key codes: https://learn.microsoft.com/windows/win32/inputdev/virtual-key-codes
KEY_FORWARD, KEY_LEFT, KEY_BACK, KEY_RIGHT = 0x57, 0x41, 0x53, 0x44  # W A S D

B = vg.XUSB_BUTTON
BUTTON_KEYS = {
    0x20: B.XUSB_GAMEPAD_A,              # Space  -> Jump
    0x51: B.XUSB_GAMEPAD_B,              # Q      -> Drop item
    0x45: B.XUSB_GAMEPAD_X,              # E      -> Inventory
    0x52: B.XUSB_GAMEPAD_Y,              # R      -> Crafting
    0x10: B.XUSB_GAMEPAD_LEFT_THUMB,     # Shift  -> Sneak
    0x11: B.XUSB_GAMEPAD_LEFT_THUMB,     # Ctrl   -> Sprint (L3)
    0x46: B.XUSB_GAMEPAD_RIGHT_THUMB,    # F      -> Change view
    0x1B: B.XUSB_GAMEPAD_START,          # Esc    -> Pause
    0x09: B.XUSB_GAMEPAD_BACK,           # Tab    -> Back/Select
    0x26: B.XUSB_GAMEPAD_DPAD_UP,        # Arrow keys -> D-pad
    0x28: B.XUSB_GAMEPAD_DPAD_DOWN,
    0x25: B.XUSB_GAMEPAD_DPAD_LEFT,
    0x27: B.XUSB_GAMEPAD_DPAD_RIGHT,
    0x5A: B.XUSB_GAMEPAD_LEFT_SHOULDER,  # Z -> prev hotbar slot
    0x58: B.XUSB_GAMEPAD_RIGHT_SHOULDER, # X -> next hotbar slot
}
# ----------------------------------------

user32 = ctypes.windll.user32
user32.GetAsyncKeyState.restype = ctypes.c_short


def key_down(vk):
    return bool(user32.GetAsyncKeyState(vk) & 0x8000)


def get_cursor():
    pt = wintypes.POINT()
    user32.GetCursorPos(ctypes.byref(pt))
    return pt.x, pt.y


class State:
    left_click = False
    right_click = False
    scroll_pending = 0  # +1 up, -1 down


state = State()


def on_click(x, y, button, pressed):
    if button == mouse.Button.left:
        state.left_click = pressed
    elif button == mouse.Button.right:
        state.right_click = pressed


def on_scroll(x, y, dx, dy):
    state.scroll_pending += 1 if dy > 0 else -1


def clamp(v, lo=-1.0, hi=1.0):
    return max(lo, min(hi, v))


def main():
    pad = vg.VX360Gamepad()
    listener = mouse.Listener(on_click=on_click, on_scroll=on_scroll)
    listener.start()

    cx = user32.GetSystemMetrics(0) // 2
    cy = user32.GetSystemMetrics(1) // 2

    enabled = False
    toggle_was_down = False
    scroll_hold = 0
    scroll_btn_current = B.XUSB_GAMEPAD_LEFT_SHOULDER
    dt = 1.0 / POLL_HZ
    all_buttons = set(BUTTON_KEYS.values())

    print("Running. Press F8 to toggle capture. Ctrl+C to quit.")
    try:
        while True:
            start = time.perf_counter()

            t = key_down(TOGGLE_KEY)
            if t and not toggle_was_down:
                enabled = not enabled
                print("Capture", "ON" if enabled else "OFF")
                if enabled:
                    user32.SetCursorPos(cx, cy)
                else:
                    pad.reset()
                    pad.update()
            toggle_was_down = t

            if enabled:
                # Left stick: WASD
                lx = (1 if key_down(KEY_RIGHT) else 0) - (1 if key_down(KEY_LEFT) else 0)
                ly = (1 if key_down(KEY_FORWARD) else 0) - (1 if key_down(KEY_BACK) else 0)
                if lx and ly:
                    lx *= 0.7071
                    ly *= 0.7071
                pad.left_joystick_float(x_value_float=lx, y_value_float=ly)

                # Right stick: mouse movement
                mx, my = get_cursor()
                dx, dy = mx - cx, my - cy
                user32.SetCursorPos(cx, cy)
                rx = clamp(dx * SENSITIVITY)
                ry = clamp(-dy * SENSITIVITY)
                if INVERT_Y:
                    ry = -ry
                pad.right_joystick_float(x_value_float=rx, y_value_float=ry)

                # Triggers: mouse buttons
                pad.right_trigger_float(1.0 if state.left_click else 0.0)
                pad.left_trigger_float(1.0 if state.right_click else 0.0)

                # Buttons
                pressed = {btn for vk, btn in BUTTON_KEYS.items() if key_down(vk)}
                if state.scroll_pending != 0:
                    scroll_hold = 3
                    scroll_btn_current = (B.XUSB_GAMEPAD_LEFT_SHOULDER
                                          if state.scroll_pending > 0
                                          else B.XUSB_GAMEPAD_RIGHT_SHOULDER)
                    state.scroll_pending = 0
                if scroll_hold > 0:
                    pressed.add(scroll_btn_current)
                    scroll_hold -= 1

                for btn in all_buttons:
                    if btn in pressed:
                        pad.press_button(button=btn)
                    else:
                        pad.release_button(button=btn)

                pad.update()

            time.sleep(max(0, dt - (time.perf_counter() - start)))
    except KeyboardInterrupt:
        pass
    finally:
        pad.reset()
        pad.update()
        listener.stop()


if __name__ == "__main__":
    main()
