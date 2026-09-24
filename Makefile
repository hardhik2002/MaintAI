.PHONY: setup data eda train api simulator frontend test lint

setup:
	python -m venv .venv
	.venv/Scripts/python -m pip install -e ".[dev]"
	cd frontend && npm install

data:
	.venv/Scripts/python scripts/download_data.py

eda:
	.venv/Scripts/python -m maintai_ml.eda

train:
	.venv/Scripts/python -m maintai_ml.train

api:
	.venv/Scripts/uvicorn backend.app.main:app --reload

simulator:
	.venv/Scripts/python -m simulator.main

frontend:
	cd frontend && npm run dev

test:
	.venv/Scripts/pytest
	cd frontend && npm test

lint:
	.venv/Scripts/ruff check backend ml/src ml/tests simulator scripts

