.DEFAULT_GOAL := help
DOCKER_PROD = docker-compose.yml
#####---PROD---#####
help:
	$(info ------------------------------------------------------------------------------------------------------------------------------)
	$(info "#####---PROD---#####" (build, up, build_up, start, down, destroy, stop, restart))
	$(info ------------------------------------------------------------------------------------------------------------------------------)
ugc_build:
	docker-compose -f ${DOCKER_PROD} build
ugc_up:
	docker-compose -f ${DOCKER_PROD} up -d
ugc_build_up: ugc_build ugc_up
ugc_start:
	docker-compose -f ${DOCKER_PROD} start
ugc_down:
	docker-compose -f ${DOCKER_PROD} down
ugc_destroy:
	docker-compose -f ${DOCKER_PROD} down -v
	docker  volume ls -f dangling=true
	docker volume prune --force
	docker rmi $(shell docker images --filter "dangling=true" -q --no-trunc)
ugc_stop:
	docker-compose -f ${DOCKER_PROD} stop
ugc_restart:
	docker-compose -f ${DOCKER_PROD} stop
	docker-compose -f ${DOCKER_PROD} up -d