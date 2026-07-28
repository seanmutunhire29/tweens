# Makefile for building Tailwind assets and running the app.

VENV ?= .venv
PYTHON ?= python3
PIP := $(VENV)/bin/pip
FLASK := $(VENV)/bin/flask

.PHONY: build watch clean run setup

build: setup
	npm run build

watch: setup
	npm run watch

setup: $(VENV)/bin/pip

$(VENV)/bin/pip:
	$(PYTHON) -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

run: setup
	$(FLASK) --app flask_app.app --debug run

clean:
	rm -f public/css/tailwind.css
