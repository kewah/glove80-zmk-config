# Project guidance

Personal MoErgo Glove80 ZMK configuration ported from the Corne Graphite keymap.

- Firmware uses the pinned MoErgo ZMK fork, not generic upstream ZMK.
- Build via GitHub Actions; `build.yaml` produces separate left/right UF2 files.
- Edit `config/glove80.keymap` and always update `README.md` with layout changes.
- Keep unused keys `&none` unless a layout change is explicitly requested.
- Preserve Corne hold-tap, sticky, macro, and combo behavior/timing.
- Run `python3 tests/verify_port.py` before committing. Intentional future layout
  changes need corresponding test updates, not silent changes to the source fixture.
- `reference/corne_choc_pro.keymap` is a frozen migration reference from Corne
  commit `48767f99d8f37bef08a9b71a929d394685f63558`.
- Never raise the Glove80 RGB brightness cap above MoErgo's 80% hardware limit.
