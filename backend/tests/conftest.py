import sys
from pathlib import Path

# Make the backend package importable the same way server.py runs it
# (scripts executed from backend/ resolve `import config` directly).
BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_DIR))
