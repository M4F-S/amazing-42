PYTHON  = python3
VENV    = .venv
BIN     = $(VENV)/bin
MAIN    = a_maze_ing.py
CONFIG  = config.txt
WHEEL   = mazegen-1.0.1-py3-none-any.whl

MYPY_FLAGS = --warn-return-any --warn-unused-ignores \
             --ignore-missing-imports --disallow-untyped-defs \
             --check-untyped-defs

.PHONY: install run debug build lint lint-strict test clean

install: $(VENV)
	$(BIN)/pip install --quiet --upgrade pip
	$(BIN)/pip install --quiet -r requirements.txt
	@if [ -f $(WHEEL) ]; then $(BIN)/pip install --quiet --force-reinstall $(WHEEL); fi

$(VENV):
	$(PYTHON) -m venv $(VENV)

run: install
	$(BIN)/python $(MAIN) $(CONFIG)

debug: install
	$(BIN)/python -m pdb $(MAIN) $(CONFIG)

build: install
	$(BIN)/pip install --quiet build
	$(BIN)/python -m build

lint: install
	$(BIN)/pip install --quiet flake8 mypy
	$(BIN)/flake8 .
	$(BIN)/mypy . $(MYPY_FLAGS)

lint-strict: install
	$(BIN)/pip install --quiet flake8 mypy
	$(BIN)/flake8 .
	$(BIN)/mypy . --strict

test: install
	$(BIN)/python tester/run_all.py

clean:
	rm -rf $(VENV) build dist *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .mypy_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	rm -f maze.txt
