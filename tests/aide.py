import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
PLUGIN = RACINE / "plugin"
sys.path.insert(0, str(RACINE / "teardown"))
