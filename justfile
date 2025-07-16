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

run arg="":
	if {{arg}} == "backend" {
		cd backend
		python -m apps.backend

	python -m apps.main
