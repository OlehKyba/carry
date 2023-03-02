build:
	docker compose build carry-image
run:
	docker compose run --rm bot; docker compose stop
