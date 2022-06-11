.DEFAULT_GOAL := help
DOCKER_PROD = ugc/docker-compose.yml
DOCKER_USER_DATA = user_data_api/docker-compose.yml
DOCKER_ELK = elk/docker-compose-elk.yml
UGC_STACK_NAME = "ugc"
USER_DATA_STACK_NAME = "user_data"
ELK_STACK_NAME = "elk"
#####---PROD---#####
help:
	$(info ------------------------------------------------------------------------------------------------------------------------------)
	$(info "#####---PROD---#####" (build, up, build_up, start, down, destroy, stop, restart))
	$(info ------------------------------------------------------------------------------------------------------------------------------)
	$(info ------------------------------------------------------------------------------------------------------------------------------)
	$(info "#####---USER_DATA---#####" (build, up, build_up, start, down, destroy, stop, restart))
	$(info ------------------------------------------------------------------------------------------------------------------------------)
ugc_build:
	docker-compose -p ${UGC_STACK_NAME} -f ${DOCKER_PROD} build
ugc_up:
	docker-compose -p ${UGC_STACK_NAME} -f ${DOCKER_PROD} up -d
ugc_build_up: ugc_build ugc_up
ugc_start:
	docker-compose -p ${UGC_STACK_NAME} -f ${DOCKER_PROD} start
ugc_down:
	docker-compose -p ${UGC_STACK_NAME} -f ${DOCKER_PROD} down
ugc_destroy:
	docker-compose -p ${UGC_STACK_NAME} -f ${DOCKER_PROD} down -v
	docker volume ls -f dangling=true
	docker volume prune --force
	docker image prune --force --filter="dangling=true"
ugc_stop:
	docker-compose -p ${UGC_STACK_NAME} -f ${DOCKER_PROD} stop
ugc_restart:
	docker-compose -p ${UGC_STACK_NAME} -f ${DOCKER_PROD} stop
	docker-compose -p ${UGC_STACK_NAME} -f ${DOCKER_PROD} up -d

#####---USER_DATA---#####
ud_build:
	docker-compose -p ${USER_DATA_STACK_NAME} -f ${DOCKER_USER_DATA} build
ud_up:
	docker-compose -p ${USER_DATA_STACK_NAME} -f ${DOCKER_USER_DATA} up -d
ud_build_up: ud_build ud_up
ud_start:
	docker-compose -p ${USER_DATA_STACK_NAME} -f ${DOCKER_USER_DATA} start
ud_down:
	docker-compose -p ${USER_DATA_STACK_NAME} -f ${DOCKER_USER_DATA} down
ud_destroy:
	docker-compose -p ${USER_DATA_STACK_NAME} -f ${DOCKER_USER_DATA} down -v
	docker volume ls -f dangling=true
	docker volume prune --force
	docker image prune --force --filter="dangling=true"
ud_stop:
	docker-compose -p ${USER_DATA_STACK_NAME} -f ${DOCKER_USER_DATA} stop
ud_restart:
	docker-compose -p ${USER_DATA_STACK_NAME} -f ${DOCKER_USER_DATA} stop
	docker-compose -p ${USER_DATA_STACK_NAME} -f ${DOCKER_USER_DATA} up -d

#####---ELK---#####
elk_build:
	docker-compose -p ${ELK_STACK_NAME} -f ${DOCKER_ELK} build
elk_up:
	docker-compose -p ${ELK_STACK_NAME} -f ${DOCKER_ELK} up -d
elk_build_up: ud_build ud_up
elk_start:
	docker-compose -p ${ELK_STACK_NAME} -f ${DOCKER_ELK} start
elk_down:
	docker-compose -p ${ELK_STACK_NAME} -f ${DOCKER_ELK} down
elk_destroy:
	docker-compose -p ${ELK_STACK_NAME} -f ${DOCKER_ELK} down -v
	docker volume ls -f dangling=true
	docker volume prune --force
	docker image prune --force --filter="dangling=true"
elk_stop:
	docker-compose -p ${ELK_STACK_NAME} -f ${DOCKER_ELK} stop
elk_restart:
	docker-compose -p ${ELK_STACK_NAME} -f ${DOCKER_ELK} stop
	docker-compose -p ${ELK_STACK_NAME} -f ${DOCKER_ELK} up -d

all_build: elk_build ugc_build ud_build
	docker network create ugc-network

all_up: elk_up ugc_up ud_up

all_build_up: all_build all_up

all_down: elk_down ugc_down ud_down

all_destroy: elk_destroy ugc_destroy ud_destroy
	docker network rm ugc-network

all_first_start: all_build_up
	docker exec mongocfg1 bash -c 'echo "rs.initiate({_id: \"mongors1conf\", configsvr: true, members: [{_id: 0, host: \"mongocfg1\"}, {_id: 1, host: \"mongocfg2\"}]})" | mongo'
	docker exec mongors1n1 bash -c 'echo "rs.initiate({_id: \"mongors1\", members: [{_id: 0, host: \"mongors1n1\"}, {_id: 1, host: \"mongors1n2\"}]})" | mongo'
	docker exec mongors2n1 bash -c 'echo "rs.initiate({_id: \"mongors2\", members: [{_id: 0, host: \"mongors2n1\"}, {_id: 1, host: \"mongors2n2\"}]})" | mongo'
	timeout 20
	docker exec mongos1 bash -c 'echo "sh.addShard(\"mongors1/mongors1n1\")" | mongo'
	docker exec mongos1 bash -c 'echo "sh.addShard(\"mongors2/mongors2n1\")" | mongo'
	docker exec mongors1n1 bash -c 'echo "use someDb" | mongo'
	docker exec mongos1 bash -c 'echo "sh.enableSharding(\"someDb\")" | mongo'
