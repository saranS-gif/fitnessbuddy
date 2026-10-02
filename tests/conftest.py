import os
import pytest

# Ensure tests run in test mode with fast intelligent rule fallbacks and SQLite in-memory
os.environ["TESTING"] = "1"
