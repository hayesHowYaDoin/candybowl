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

pre-commit:
    pre-commit run --all-files

run:
	python -m apps.main
