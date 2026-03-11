"""
Vercel entrypoint for FastAPI. Project root is workspace root.
"""
import sys
from pathlib import Path

_root = Path(__file__).resolve().parent
sys.path.insert(0, str(_root / "python"))

from api.main import app
