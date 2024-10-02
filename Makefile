SHELL	= /bin/sh

NAME	= transcendence

all:
	mkdir -p volumes/certs && cd volumes/certs && openssl req -x509 -nodes \
		-newkey rsa:4096 -days 365 \
		-keyout key.pem -out cert.pem \
		-subj "/C=ES/L=Malaga/O=42 Malaga/CN=localhost" \
		-addext "subjectAltName=DNS:localhost,DNS:gateway,DNS:authentif,\
		DNS:profileapi,DNS:play,DNS:gamecalc"
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
	# docker exec -it postgres /bin/sh
	docker exec -it postgres sh -c "psql -U postgres_main_user -d transcendence_db"

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
