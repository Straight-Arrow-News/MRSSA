.PHONY: dev check build build-prod

dev:
	uvicorn src.main:app --host 0.0.0.0 --port 8080 --reload

check:
	ruff check

build:
	docker buildx build --platform linux/amd64 --provenance=false -t san/mrssa-dev .

build-prod:
	docker buildx build --platform linux/amd64 --provenance=false -t san/mrssa-prod .