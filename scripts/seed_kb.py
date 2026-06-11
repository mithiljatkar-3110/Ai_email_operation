"""CLI entry point: python scripts/seed_kb.py"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.scripts.seed_kb import main

if __name__ == "__main__":
    raise SystemExit(main())
