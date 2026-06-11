"""CLI entry point: python scripts/replay.py --speed 1"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.scripts.replay import main

if __name__ == "__main__":
    raise SystemExit(main())
