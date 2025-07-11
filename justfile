default:
  @just --list

install:
	poetry install

analyze:
	ruff check .
	ruff format .
	mypy .

test:
	pytest .

run:
	python -m apps.main
