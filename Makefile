.PHONY: all clean lint type test test-cov

CMD:=poetry run
PYMODULE:=gchqnet
MANAGEPY:=$(CMD) ./manage.py
SETTINGS_MODULE:=gchqnet.core.settings.test

all: type test format lint

fix: format lint-fix

lint: 
	$(CMD) ruff check $(PYMODULE)

lint-fix: 
	$(CMD) ruff check --fix $(PYMODULE)

check:
	$(MANAGEPY) check

dev:
	$(MANAGEPY) runserver

format:
	find $(PYMODULE) -name "*.html" | xargs $(CMD) djhtml
	$(CMD) ruff format $(PYMODULE)

format-check:
	find $(PYMODULE) -name "*.html" | xargs $(CMD) djhtml --check
	$(CMD) ruff format --check $(PYMODULE)

type: 
	$(CMD) mypy --no-incremental $(PYMODULE)

test: | $(PYMODULE)
	DJANGO_SETTINGS_MODULE=$(SETTINGS_MODULE) $(CMD) pytest -vv --cov=$(PYMODULE) $(PYMODULE)

test-cov:
	DJANGO_SETTINGS_MODULE=$(SETTINGS_MODULE) $(CMD) pytest -vv --cov=$(PYMODULE) $(PYMODULE) --cov-report html

clean:
	git clean -Xdf # Delete all files in .gitignore
