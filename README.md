# AI Card Game

Two ways to play:
- Terminal (no graphics): `python main.py`
- Pygame UI (graphics): `python run_ui.py`

## Quick start (Windows, PowerShell)

Pygame currently ships wheels for specific Python versions. If you are on Python 3.14, install Python 3.12 (or 3.11) and use a virtual environment.

1) Install Python 3.12 from https://www.python.org/downloads/release/python-312*
   - Check "Add python.exe to PATH"
   - Install the "py launcher" if offered

2) In this folder, create and activate a venv with Python 3.12:

```powershell
# Verify 3.12 is available
py -0p

# Create venv (uses Python 3.12)
py -3.12 -m venv .venv

# Activate it
. .venv\Scripts\Activate.ps1

# Upgrade pip and install deps
python -m pip install --upgrade pip
pip install -r requirements.txt
```

3) Run it:

```powershell
# Terminal version
python main.py

# Pygame UI version
python run_ui.py
```

## Why did `pip install pygame` fail?
- You are using Python 3.14 (see `py -0p` output). Pygame 2.6.x does not ship wheels for 3.14 yet, so pip tries to build from source.
- Building from source on Windows needs extra toolchains and `distutils` compatibility, which 3.12+ removes. Hence the error `No module named 'setuptools._distutils.msvccompiler'`.
- Using Python 3.12/3.11 avoids building from source because prebuilt wheels are available.

## Notes
- The graphics window starts in "setup" mode; press SPACE to deal the cards.
- During the AI turn, you may see debug output in the terminal—this is expected.
