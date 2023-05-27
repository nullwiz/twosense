setup: down build up build-local-db test simulate
setup-mongo : down build up build-local-mongo test simulate
setup-mongo-dev : down build up-db-mongo build-local-db-mongo test simulate
rundev: down build up-db build-local-db 

test: 
	. .venv/bin/activate && pytest -v 

down:
	docker compose down 

simulate:
	API_HOST=http://localhost:5000 poetry run python simulation/simulate.py  

build: 
	docker-compose build 

env:
	python3 -m venv .venv
	. .venv/bin/activate && pip install -r requirements.txt
	
build-local-db:
	. .venv/bin/activate && PYTHONPATH=${PWD} python api/db/manage_postgres_tables.py --drop
	. .venv/bin/activate && PYTHONPATH=${OWD} python api/db/redis_flushall.py

build-local-mongo:
	. .venv/bin/activate && PYTHONPATH=${PWD} python api/db/manage_mongo_collections.py
	. .venv/bin/activate && PYTHONPATH=${OWD} python api/db/redis_flushall.py

up:
	docker-compose up -d

up-db: 
	docker-compose up -d postgres redis redisinsight
up-db-mongo: 
	docker-compose up -d mongo redis redisinsight
