# Simple Python App Scaffold

A small Python command-line app scaffold using the standard library.

## Setup

This project uses `venv` because `uv` was not found on the local PATH.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Run

```powershell
python main.py --name "Codex"
```

## CLI

```powershell
python main.py --help
```

The CLI accepts an optional `--name` argument and prints a greeting.
