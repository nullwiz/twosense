## Overview

The solution to the challange might have too many files! I am sorry, i tried 
to make it as abstract as possible, but it might have been overkill for the sake 
of this challenge, and could have used the time for tests instead.

## Setup
The makefile does everything.
just do "make setup" to run everything (dependencies, build, tests, simulation). I made it so you dont have to activate
the venv for doing it. 

You can also do "make up-db" to clear the db and redis and start everything but the fastapi client,
in that case, you do:

```python
   source .venv/bin/activate
   uvicorn api.entrypoints.app:app --reload --port 5000
```

if you want to run with more workers, you can specify them with:

```python
   uvicorn api.entrypoints.app:app --port 5000--workers 4
```
At that point, you can go head over to http://localhost:5000/docs .

To access redis, you can go to 127.0.0.1:8001, but you wont be able to see the events
in the webUI: 
```
host: redis, port:6379, name: <you-can-put-whatever>
```
You can, however, use redisinsight (the gui version) or the redis-cli client
and you subscribe to the channel, you will be able to see the events. 
The db is postgres and should be exposed, the table is "locations"


## Limitations & Improvements
With more time i would have prioritized:

- cleaning the data in a jupyter notebook and process it to have some idea what the outputs 
   should be like in the db to truly tell if the end result in the db is correct. 
- proper package setup
- lots of more tests, in order to achieve proper coverage and separated by e2e, unit, integrations.
- cleaning up the handlers.py file 
- logging 
- 5 data points for user b1 are left over in redis, and one for a1: this is because redis is used as buffer,
   and as new requests come in they are pushed to the db. Since no more requests came, the buffer
   is still in redis, but if new come, they will get pushed. 



# Benchmarks

## docker + uvicorn
1 worker  2:10
4 workers  w/ docker: 2:15

## local, dockerized db + uvicorn
1 worker : 1:35
4 workers : 1:49

## local, dockerized db + gunicorn
1 worker :  1:51
4 workers : 1:51

would have loved to try with more concurrent requests and see how it performs.