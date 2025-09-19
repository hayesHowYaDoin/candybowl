default:
	@just --list

install:
	poetry install
	cd frontend && npm install

analyze:
	ruff check .
	ruff format .
	mypy .

test:
	pytest .

pre-commit:
    pre-commit run --all-files

run arg="":
	#!/usr/bin/env bash
	if [[ "{{arg}}" == "backend" ]]; then
		cd backend && python -m apps.main
	elif [[ "{{arg}}" == "frontend" ]]; then
		cd frontend && npm install && npm run dev
	else
		python -m apps.main
	fi
