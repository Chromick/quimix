"""Entry point da API na Vercel.

A Vercel só reconhece funções Python dentro de `api/`. Este módulo expõe o
`app` definido em `server.py`, que continua sendo a fonte única das rotas.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from server import app  # noqa: E402

__all__ = ["app"]
