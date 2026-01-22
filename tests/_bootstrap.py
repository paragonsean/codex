import os
import sys


def _repo_root() -> str:
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


ROOT_DIR = _repo_root()
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
