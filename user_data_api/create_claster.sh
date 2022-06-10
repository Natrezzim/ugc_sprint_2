#!/usr/bin/env bash
#DEPRECIATED
docker exec mongocfg1 bash -c 'echo "rs.initiate({_id: \"mongors1conf\", configsvr: true, members: [{_id: 0, host: \"mongocfg1\"}, {_id: 1, host: \"mongocfg2\"}]})" | mongo'
docker exec mongors1n1 bash -c 'echo "rs.initiate({_id: \"mongors1\", members: [{_id: 0, host: \"mongors1n1\"}, {_id: 1, host: \"mongors1n2\"}]})" | mongo'
docker exec mongors2n1 bash -c 'echo "rs.initiate({_id: \"mongors2\", members: [{_id: 0, host: \"mongors2n1\"}, {_id: 1, host: \"mongors2n2\"}]})" | mongo'
sleep 20
docker exec mongos1 bash -c 'echo "sh.addShard(\"mongors1/mongors1n1\")" | mongo'
docker exec mongos1 bash -c 'echo "sh.addShard(\"mongors2/mongors2n1\")" | mongo'
docker exec mongors1n1 bash -c 'echo "use someDb" | mongo'
docker exec mongos1 bash -c 'echo "sh.enableSharding(\"someDb\")" | mongo'
