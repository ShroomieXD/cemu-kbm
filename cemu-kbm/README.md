# cemu-kbm

Play **Wii U Minecraft in Cemu with keyboard and mouse**. Cemu has no plugin system, so this small Python program turns your keyboard and mouse into a **virtual Xbox 360 controller** that Cemu reads like a normal gamepad.

> Windows only. Not affiliated with Cemu, Nintendo, or Mojang. Use only with games you legally own.

## Setup

1. Install the [ViGEmBus driver](https://github.com/nefarius/ViGEmBus/releases). (The project is retired by its author but still works.)
2. Install [Python 3.9+](https://www.python.org/downloads/).
3. Clone and install:
   ```
   git clone https://github.com/YOUR_USERNAME/cemu-kbm.git
   cd cemu-kbm
   pip install -r requirements.txt
   ```
4. Run it:
   ```
   python cemu_kbm.py
   ```
5. In Cemu: **Options → Input settings**, choose Wii U GamePad (or Pro Controller), set API to **XInput**, select the virtual controller, and click **Auto-map**.
6. Press **F8** to toggle capture on/off.

## Default controls

| Input | Action |
|---|---|
| W A S D | Move |
| Mouse | Look |
| Left / Right click | Attack or mine / Place or use |
| Space | Jump |
| Shift / Ctrl | Sneak / Sprint |
| E / R / Q | Inventory / Crafting / Drop |
| Scroll wheel (or Z / X) | Change hotbar slot |
| Arrow keys | D-pad |
| Esc / Tab | Start / Select |
| F8 | Toggle capture |

Edit the `CONFIG` section at the top of `cemu_kbm.py` to change sensitivity or remap keys.

## Limitations

- The mouse drives the right stick, so it feels like stick aiming, not native PC mouse look.
- Menus can't be clicked with the mouse; use the arrow keys.
- The GamePad touchscreen isn't emulated.
- The cursor is recentered every frame while capture is on. Use fullscreen if it drifts.

## Troubleshooting

- **Controller not listed in Cemu:** make sure ViGEmBus is installed and the script is running.
- **Wrong buttons:** adjust bindings in Cemu's input settings.
- **Camera too fast/slow:** change `SENSITIVITY`.

## License

MIT
