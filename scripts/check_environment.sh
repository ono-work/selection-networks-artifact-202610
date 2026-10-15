#!/usr/bin/env sh
set -eu

echo "Python:"
python3 --version

echo
echo "pytest:"
if command -v pytest >/dev/null 2>&1; then
  pytest --version
else
  echo "pytest not found"
  echo "Recommended command: python3 -m pip install -e \".[test]\""
fi

echo
echo "clingo:"
if [ -x .venv/bin/python ] && .venv/bin/python -m clingo --version >/dev/null 2>&1; then
  echo "command: .venv/bin/python -m clingo"
  .venv/bin/python -m clingo --version | head -n 1
else
  echo "clingo not found at canonical command: .venv/bin/python -m clingo"
  echo "Recommended command: .venv/bin/python -m pip install clingo"
fi

echo
echo "No global or sudo installation was attempted."
