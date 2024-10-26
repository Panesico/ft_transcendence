SHELL	= /bin/sh

NAME	= transcendence

all:
	@if [ ! -d "volumes/certs" ] || [ ! -f "volumes/certs/cert.pem" ] || \
		[ ! -f "volumes/certs/key.pem" ]; then \
		$(MAKE) certs; \
	fi; \
	cd srcs && docker compose up --build

init:
	bash -c "mkdir -p ./volumes/{postgres_db,frontend}"
	touch ./srcs/.env
	echo "Please, fill the .env file with the following variables: DJANGO_SECRET_KEY, DJANGO_SUPERUSER_USERNAME, DJANGO_SUPERUSER_EMAIL, DJANGO_SUPERUSER_PASSWORD, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD, CERTFILE"

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

certs:
	mkdir -p volumes/certs && cd volumes/certs && openssl req -x509 -nodes \
		-newkey rsa:4096 -days 365 \
		-keyout key.pem -out cert.pem \
		-subj "/C=ES/L=Malaga/O=42 Malaga/CN=localhost" \
		-addext "subjectAltName=DNS:localhost,DNS:gateway,DNS:authentif,\
		DNS:profileapi,DNS:play,DNS:calcgame,DNS:blockchain"

postgres:
	docker exec -it postgres sh \
		-c "psql -U postgres_main_user -d transcendence_db"
deletenotifications:
	docker exec -it postgres sh \
		-c "psql -U postgres_main_user -d transcendence_db -c 'DELETE FROM profileapi_notification;'"

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
calcgame:
	docker exec -it calcgame /bin/sh
blockchain:
	docker exec -it blockchain bash
blockchain_restart:
	docker restart blockchain



.phony: all down stop logs prune routine reset certs postgres \
	gateway gateway_restart authentif authentif_restart \
	profileapi profileapi_restart calcgame blockchain
