PIP ?= pip
PYTHON ?= python
ENTRY ?= src/streamlit.py

env: 
	$(PIP) install --upgrade 'openai>=1.0'
	$(PIP) install streamlit

run:
	streamlit run $(ENTRY)