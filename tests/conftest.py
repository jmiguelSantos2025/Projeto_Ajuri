import sys
from pathlib import Path

# Deixa o pacote de serviços (src/services) importável nos testes.
SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
