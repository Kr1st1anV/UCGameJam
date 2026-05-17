"""Project root for assets — works in source tree and PyInstaller builds."""
import os
import sys


def app_root() -> str:
    if getattr(sys, "frozen", False):
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))


ROOT_DIR = app_root()
