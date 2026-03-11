"""
Vercel Function entrypoint.
This file maps to the /api/* routes on Vercel.
"""
import sys
from pathlib import Path

_project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_project_root / "python"))

from api.main import app  # noqa: E402

