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
	docker-compose $(ENV_CONFIG) rm -f -s interviewer
	$(HIDE_DOCKER_CLI_DETAILES) docker-compose $(ENV_CONFIG) build interviewer
	docker-compose $(ENV_CONFIG) up -d interviewer

logs:
	docker-compose $(ENV_CONFIG) logs -f

redis:
	docker-compose $(ENV_CONFIG) up -d redis

all: build up