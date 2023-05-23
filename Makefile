setup: buildlocal build up build-local-db test simulate

rundev: buildlocal build build-local-db up-db

test: 
	pytest -v 

simulate:
	API_HOST=http://localhost:5000 poetry run python simulation/simulate.py  
build: 
	docker-compose build 

buildlocal:
	pip install -r requirements.txt

build-local-db:
	python api/db/manage_postgres_tables.py --drop
	python api/db/redis_flushall.py

up:
	docker-compose up -d

up-db:
	docker-compose up -d db redis redisinsight
