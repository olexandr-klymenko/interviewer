HIDE_DOCKER_CLI_DETAILES=COMPOSE_DOCKER_CLI_BUILD=1 DOCKER_BUILDKIT=1

build:
	$(HIDE_DOCKER_CLI_DETAILES) docker-compose build

up:
	docker-compose up -d

down:
	docker-compose down

app_restart:
	docker-compose stop interviewer
	docker-compose start interviewer

restart: build app_restart

logs:
	docker-compose logs -f

all: build up