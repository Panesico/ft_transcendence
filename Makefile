SHELL	= /bin/sh

NAME	= transcendence

all:
	cd srcs && docker compose up --build

down:
	cd srcs && docker compose down -v
stop:
	cd srcs && docker compose stop
logs:
	cd srcs && docker-compose logs -f

prune:
	docker image prune
routine:
	docker system prune -a
reset:
	docker stop $$(docker ps -qa); \
	docker rm $$(docker ps -qa); \
	docker rmi -f $$(docker images -qa); \
	docker volume rm $$(docker volume ls -q); \
	docker network rm $$(docker network ls -q) 2>/dev/null

postgres:
	docker exec -it postgres /bin/sh
gateway:
	docker exec -it gateway /bin/sh
gateway_restart:
	docker restart gateway
authentif:
	docker exec -it authentif /bin/sh
authentif_restart:
	docker restart authentif
profileapi:
	docker exec -it profileapi /bin/sh
profileapi_restart:
	docker restart profileapi



.phony: all down stop logs prune routine reset postgres \
	gateway gateway_restart authentif authentif_restart \
	profileapi profileapi_restart
