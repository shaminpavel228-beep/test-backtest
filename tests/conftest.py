# Ensure project root is on sys.path so tests can import `scripts` when run by pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
