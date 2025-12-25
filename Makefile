ruff:
	ruff check
	ruff format

run-steel-browser-api:
	sudo docker run --name steel-browser-api -d -p 3000:3000 -p 9223:9223 ghcr.io/steel-dev/steel-browser-api:latest