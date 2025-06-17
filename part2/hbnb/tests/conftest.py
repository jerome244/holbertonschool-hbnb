# tests/conftest.py
import sys
import os

# Add project root (one level up) to sys.path so 'app' module can be imported
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
