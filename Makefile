HIDE_DOCKER_CLI_DETAILES=COMPOSE_DOCKER_CLI_BUILD=1 DOCKER_BUILDKIT=1
ENV ?= dev
ENV_CONFIG=--env-file ./config/.env.$(ENV)

ps:
	docker-compose $(ENV_CONFIG) ps

build:
	$(HIDE_DOCKER_CLI_DETAILES) docker-compose $(ENV_CONFIG) build

up:
	docker-compose $(ENV_CONFIG) up -d

down:
	docker-compose $(ENV_CONFIG) down

restart:
	docker-compose $(ENV_CONFIG) stop interviewer
	$(HIDE_DOCKER_CLI_DETAILES) docker-compose $(ENV_CONFIG) build
	docker-compose $(ENV_CONFIG) start interviewer

logs:
	docker-compose $(ENV_CONFIG) logs -f

all: build up