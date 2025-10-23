.PHONY: dev check build build-prod

ECR = 637947834915.dkr.ecr.us-east-1.amazonaws.com
REGION = us-east-1
IMAGE = san/mrssa

dev:
	uvicorn src.main:app --host 0.0.0.0 --port 8080 --reload

check:
	ruff check

build:
	docker buildx build --platform linux/amd64 --provenance=false -t $(IMAGE)-dev .

build-prod:
	docker buildx build --platform linux/amd64 --provenance=false -t $(IMAGE)-prod .

deploy:
	docker buildx build --platform linux/amd64 --provenance=false -t $(IMAGE)-prod .
	aws ecr get-login-password --region $(REGION) | docker login --username AWS --password-stdin $(ECR)
	docker tag $(IMAGE)-prod:latest $(ECR)/$(IMAGE)-prod:latest
	docker push $(ECR)/$(IMAGE)-prod
