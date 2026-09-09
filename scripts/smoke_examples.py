"""Render every numbered example in a hidden Tk window (requires a display)."""
from pathlib import Path
import subprocess
import sys


def main():
    root = Path(__file__).resolve().parents[1]
    examples = sorted(root.glob("[0-9]*. *.py"))
    if not examples:
        raise SystemExit("No numbered examples found")
    for example in examples:
        subprocess.run(
            [sys.executable, str(example), "--smoke", "--seconds", "1", "--fps", "5"],
            cwd=root, check=True, timeout=120,
        )
    print(f"All {len(examples)} examples passed.")


if __name__ == "__main__":
    main()
