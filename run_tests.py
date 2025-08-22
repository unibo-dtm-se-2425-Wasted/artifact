import unittest
import sys
import os

# Aggiunge la directory corrente (artifact/) al PYTHONPATH
sys.path.insert(0, os.path.abspath('.'))

# Cerca tutti i test nella cartella test/
loader = unittest.TestLoader()
tests = loader.discover('test')  # test è la cartella dei test
test_runner = unittest.TextTestRunner()

print("Running tests...\n")
result = test_runner.run(tests)
