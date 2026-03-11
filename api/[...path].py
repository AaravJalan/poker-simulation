"""
Vercel Function catch-all for /api/*.

This ensures routes like /api/health, /api/friends, etc. always hit FastAPI.
"""
import sys
from pathlib import Path

_project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_project_root / "python"))

from api.main import app  # noqa: E402

