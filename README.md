# Glove80 ZMK Config

Personal **Graphite** layout for the MoErgo Glove80, ported from
[kewah/corne-zmk-config](https://github.com/kewah/corne-zmk-config) at commit
`48767f99d8f37bef08a9b71a929d394685f63558`. Designed for macOS, without changing
existing Corne shortcuts, sticky behavior, hold-tap settings, or combo timing.

## Firmware approach

MoErgo recommends its [Layout Editor](https://my.glove80.com) for most users,
but also documents [building your own configuration repository](https://docs.moergo.com/glove80-user-guide/appendix-zmk/).
This repository follows the official
[West-based template](https://github.com/moergo-sc/glove80-zmk-config-west), so the
Corne's external tri-state module can be included through `config/west.yml`.

- Use **MoErgo's Glove80 ZMK distribution**, not generic upstream ZMK.
- Firmware and tri-state dependencies are pinned to commits in `config/west.yml`.
- GitHub Actions builds **separate left/right UF2 files**. These are NOT the
  combined, interchangeable UF2 produced by the Layout Editor/Nix template.
- Keep MoErgo's board defaults, including macOS-compatible consumer reports,
  split Bluetooth settings, and the RGB brightness cap (never exceed 80%).
- No local firmware toolchain is required.

## Physical placement

The inner five finger columns of physical rows **3, 4, and 5** carry the original
Corne top, home, and bottom alpha rows. On stock QWERTY keycaps, these are the
Q/A/Z rows. The two rows above and extra finger row below are unassigned.
Escape remains outside the left home row; Shift remains directly below Escape.
The remaining outside finger keys are unassigned.

Thumb placement is anchored to the **original factory key positions** to avoid
ambiguity about inner/outer on the curved thumb clusters. The first build had
these thumb ends reversed; this corrected layout uses:

| Half | Factory key position | New binding | Matrix position |
| --- | --- | --- | --- |
| Left | Shift | SYM | 52 |
| Left | Ctrl | Disabled | 53 |
| Left | Layer/Lower | Disabled | 54 |
| Left | Backspace | EXT/MOD | 69 |
| Left | Delete | Backspace / Shift+Backspace = Delete | 70 |
| Left | Alt | Disabled | 71 |
| Right | GUI/Command | Disabled | 55 |
| Right | Ctrl | Disabled | 56 |
| Right | Shift | NUM | 57 |
| Right | Alt | Disabled | 72 |
| Right | Enter | Enter | 73 |
| Right | Space | Space | 74 |

In the row order used by MoErgo's factory keymap:

```text
factory upper: LShift LCtrl Lower  |  GUI RCtrl RShift
new upper:       SYM    —     —    |   —    —     NUM

factory lower:  BSPC   DEL  LAlt   |  RAlt ENTER SPACE
new lower:     EXT/MOD BSPC   —    |   —   ENTER SPACE
```

SYM/NUM use the two factory Shift thumb keys, not the dedicated finger Shift
beside the bottom alpha row. Lower Enter and Space retain their factory positions.

Unused thumbs are disabled on **every** layer. Backspace becomes Delete when
Shift is active. Enter becomes Shift+Enter on MOD and EXT. On NUM, the SYM thumb
still sends `.` and the EXT/MOD thumb still sends `0`, just as on the Corne.

The Corne's encoder controls cannot be ported to hardware with no encoders;
media/volume/brightness controls remain available on MF.

## Layers and timing

| Layer | Access |
| --- | --- |
| BASE (0) | Default Graphite |
| MOD (1) | Tap EXT/MOD: sticky next-key layer |
| EXT (2) | Hold EXT/MOD: navigation/editing |
| SYM (3) | Tap SYM: sticky next-key layer; hold for a sequence |
| NUM (4) | Tap NUM: sticky next-key layer; hold for a sequence |
| MF (5) | Hold SYM + NUM together |
| BT (6) | Hold EXT/MOD + NUM together |

Preserved from the **actual Corne keymap**:

| Behavior | Settings |
| --- | --- |
| MOD hybrid modifiers | Tap-preferred; tapping term 300 ms; quick-tap 175 ms; retro-tap |
| EXT/MOD | Balanced; tapping term 200 ms; quick-tap 175 ms; retro-tap |
| SYM/NUM sticky layers | 1000 ms; quick-release; ignore-modifiers |
| Sticky modifiers (`sk`) | ZMK default 1000 ms; ignore-modifiers |
| Sticky MOD (`sl`) | ZMK default 1000 ms; quick-release |
| Navigation/symbol combos | 50 ms, restricted to their original layers |
| MF/BT thumb combos | 100 ms, BASE only |
| Settings save debounce | 10000 ms |

On **MOD**, starred modifiers tap for sticky and hold for normal held modifiers.
On **EXT, SYM and NUM**, daggered modifiers use the Corne's existing sticky-key
behavior (`sk`), not the custom hybrid behavior. This corrects an inconsistency
in the Corne README without changing the actual working configuration.

Tap SYM/NUM, then enter modifiers, then the shortcut key: modifier presses do
not consume the sticky layer. Sticky modifiers stack. Hyper is Ctrl+Alt+Cmd+Shift.
Macro definitions and their default timing are unchanged.

## Layer maps

Diagrams show only the five alpha columns per half, in **keyboard viewing
order** (left outer → inner, right inner → outer). `—` means disabled;
`·` means transparent, falling through to a lower active layer.
`*` means hybrid modifier; `†` means sticky modifier.

### BASE

```text
 B    L    D    W    Z       |   '/"  F    O    U    J
 N    R    T    S    G       |    Y   H    A    E    I
 Q    X    M    C    V       |    K   P   ,/?  ./!   /\
```

Outside left: Escape on home; held Shift on bottom.
Shift morphs apostrophe/comma/dot/slash to double quote/question mark/exclamation/backslash.

### MOD (tap EXT/MOD)

```text
 Cmd+[ Ctrl+Tab QSWAP Cmd+W Cmd+Z |    ·    ·     ·    ·    ·
 Shift* Alt*   Ctrl*  Cmd*  Cmd+R |    ·  Hyper*  ·    ·   TMX
 Cmd+] Cmd+X   Cmd+A  Cmd+C Cmd+V |    ·    ·     ·    ·    ·
```

Outside left home: Escape. Enter thumb: Shift+Enter. Backspace/Space unchanged.
QSWAP instantly switches to the previous app, releasing Cmd immediately.

### EXT (hold EXT/MOD)

```text
 Cmd+[ TSWAP  SWAP   Cmd+W Cmd+Z |  RAlt Home End   —    PgUp
 Shift† Alt† Ctrl†  Cmd†  Cmd+R |  Left Down Up   Right TMX
 Cmd+] Cmd+X Cmd+A  Cmd+C Cmd+V |    —  Tab  Del    —    PgDn
```

Outside left home: Cmd+Grave (cycle windows). Enter thumb: Shift+Enter.
Backspace/Space unchanged. Delete is on the base comma position.

- SWAP holds Cmd across Tab taps; TSWAP holds Ctrl across Tab taps.
- Sticky Shift can reverse-cycle without releasing Cmd/Ctrl. Leaving EXT or
  pressing a non-ignored key ends the switcher.
- TMX sends the tmux prefix Ctrl+Space (also on MOD).
- Right Alt is retained for VoiceInk.

### SYM (tap or hold SYM)

```text
   —     ^      &      |      —    |   ~     @     `     #     $
 Shift† Alt†  Ctrl†  Cmd†  Hyper† |   -     (     <     [     :
   —     —      —      —      —    |   _     )     >     ]     ;
```

Backspace/Enter/Space unchanged. Both braces remain available through combos.

### NUM (tap or hold NUM)

```text
 /    7    8    9    %      |    —      —     —     —      —
 -    1    2    3    +      |  Hyper† Cmd†  Ctrl† Alt†  Shift†
 :    4    5    6    *      |    _      =     ,     —      —
```

Factory left Shift thumb (normally SYM): `.`.
Factory Backspace thumb (normally EXT/MOD): `0`.
Backspace/Enter/Space unchanged.

### MF (hold SYM + NUM)

```text
  —    Mute  Vol- Vol+  —    |  F12 F7 F8 F9  —
 Stop  Play  Prev Next  —    |  F10 F1 F2 F3  —
  —     —    Bri- Bri+  —    |  F11 F4 F5 F6  —
```

Thumbs transparent. Brightness/media commands retain their Corne positions.

### BT (hold EXT/MOD + NUM)

```text
 BT CLR OUT USB OUT BLE   —     —  | RGB TOG RGB HUI RGB HUD RGB BRI RGB BRD
 BT PRV  BT 0     BT 1   BT 2 BT NXT| RGB EFF RGB SAI RGB SAD    —       —
   —     BT 3     BT 4     —     —  |    —       —       —       —       —
```

Thumbs disabled while the maintenance layer is active.
`BT CLR` clears the selected host profile; BT 0–4 select profiles.
Output selection stays explicit, just like the Corne (BT selection alone does
not force BLE output). RGB controls retain their original meanings.

### Combos

| Layer | Positions / chord | Result |
| --- | --- | --- |
| EXT | H + A (41 + 42): Down + Up | Option+Left (word left) |
| EXT | A + E (42 + 43): Up + Right | Option+Right (word right) |
| SYM | H + A (41 + 42): `(` + `<` | `{` |
| SYM | P + comma (59 + 60): `)` + `>` | `}` |
| BASE | SYM + NUM (52 + 57): factory left + right Shift | Hold MF |
| BASE | EXT/MOD + NUM (69 + 57): factory Backspace + right Shift | Hold BT |

Tri-state switchers ignore position **35**, the left home-row sticky Shift.
Combo and ignored-key positions were remapped to Glove80's 80-key matrix.

## Build and download

Push to GitHub → **Actions → Build → successful run → firmware artifact**.
Unzip the download:

- `glove80-left.uf2`: **left half only**
- `glove80-right.uf2`: **right half only**

CLI alternative, from this repository:

```sh
gh run list --workflow build.yml
gh run download <successful-run-id> --name firmware --dir firmware
```

## Flash on macOS

Follow [MoErgo's firmware loading guide](https://docs.moergo.com/glove80-user-guide/customizing-key-layout/#loading-new-zmk-firmware-onto-your-glove80).
Have a spare keyboard available. Flash **right first, then left**:

1. Turn the half off; connect it directly to your Mac with a USB data cable.
2. Hold the physical **C6R6 + C3R3** keys on that half while turning it on.
   Use the positional diagram in MoErgo's guide, not the customized key output.
   Stock keycap labels: right **PgDn + I**; left **Magic + E**.
3. The bootloader volume appears as `GLV80RHBOOT` or `GLV80LHBOOT`.
4. Copy the matching half's UF2 file to that volume; it disappears on success.
5. Repeat for the other half. Both halves must run the same firmware revision.

The power-up bootloader chord is hardware-based and remains available even
though this layout has no Magic key or software bootloader key.
**Do not copy the left UF2 to the right half or vice versa.**

## Connect to macOS / recover Bluetooth

- **USB:** use the **left** half as the host connection. If needed, hold
  EXT/MOD + NUM and press OUT USB (base `L` position).
- **Bluetooth:** hold EXT/MOD + NUM, select BT 0 (base `R` position), and press
  OUT BLE (base `D` position). Pair **Glove80** in macOS Bluetooth settings.
- Keep macOS's host input layout at **US/ABC**, not Graphite: Graphite is already
  implemented in firmware. These symbol keycodes assume a US host layout.
- If pairing fails, forget Glove80 in macOS; select the intended BT profile and
  press BT CLR (base `B` position), then pair again.
- After changing firmware versions/advanced settings, MoErgo generally recommends
  a [configuration factory reset on BOTH halves](https://docs.moergo.com/glove80-user-guide/troubleshooting/#configuration-factory-reset-and-re-pairing-left-and-right-halves).
  With both halves initially off, hold physical **C6R6 + C3R2** while powering
  each half on; keep holding for 5 seconds, then turn it off. Stock labels:
  left **Magic + 3**, right **PgDn + 8**. This erases Bluetooth/RGB settings,
  including split pairing, but keeps the flashed layout.
  Power both halves on together, allow them to re-pair, and wait at least one
  minute for persistence. Check both halves by typing; the BT-layer RGB toggle
  replaces the stock Magic+T check if you want to inspect the lights.

## Files and verification

| File | Purpose |
| --- | --- |
| `config/glove80.keymap` | 7 layers, 80 bindings each, behaviors/macros/combos |
| `config/glove80.conf` | Keyboard name and preserved Corne settings |
| `config/west.yml` | Pinned MoErgo firmware + tri-state module |
| `build.yaml` | Left/right build matrix |
| `.github/workflows/build.yml` | Regression checks, then firmware build |
| `reference/corne_choc_pro.keymap` | Frozen source keymap for migration checks |
| `tests/verify_port.py` | Exact binding/behavior/timing preservation checks |

```sh
python3 tests/verify_port.py
```

These checks validate the migration; GitHub Actions compilation validates the
firmware. Physical comfort, Bluetooth operation, and switcher feel must still
be checked on the keyboard. Future intentional layout changes should update
the tests and this README; do not rewrite the frozen Corne reference.
