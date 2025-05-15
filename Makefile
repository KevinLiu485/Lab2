PIP ?= pip
PYTHON ?= python
ENTRY ?= src/web.py

env: 
	$(PIP) install --upgrade 'openai>=1.0'
	$(PIP) install gradio

run:
	$(PYTHON) $(ENTRY)