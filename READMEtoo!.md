## Overview

the solution to the change might have too many files! i am sorry, i tried 
to make it as abstract as possible, but it might have been overkill for the sake 
of this challenge, and could have used the time for tests instead.

This solution uses an command/event handler, bootstraps the application, and uses
the repository pattern for db abstraction, aswell as using the unit of work as context manager
for managing sessions. 

Events, for example when we add a location, are sent to a redis pubsub channel.
in this context it might not make much sense, but for other integrations could be really helpful. 

Classical mapping is used instead of declarative mapping for sqlalchemy, the reason
being that i find it easier in order to move the model elsewhere. 

In terms of the data pipeline, I would have loved to benchmark and try, for example, a data sanitization
step with some separate tool to see if we can reduce the overhead of the sanitization in 
the endpoint itself. 

I went for fastapi not only for validations, but also because of the docs.

## Setup
The makefile does everything.
just do "make setup" to run everything (dependencies, build, tests)
you can also do "make db" to clear the db and redis and start everything but the fastapi client,
in that case, you can do:

```
   uvicorn api.entrypoints.app:app --reload --port 5000
```

if you want to run with more workers, i have found that 4 workers seems to be the sweet spot:

```
   uvicorn api.entrypoints.app:app --port 5000--workers 4
```

At that point, you can go to http://localhost:5000/docs .

to access redis, you can go to 127.0.0.1:8001, but you wont be able to see the events
in the webUI.
You can, however, use redisinsight (the gui version) or the redis-cli client
and you subscribe to the channel, you will be able to see the events. 

## improvements, limitations 
with more time i would have prioritized:
- cleaning the data in a jupyter notebook and process it to have some idea what the outputs 
   should be like in the db to truly tell if the end result in the db is correct. 
- package setup
- lots of more tests, in order to achieve proper coverage and separated by e2e, unit, integrations.
- cleaning up the handlers.py file 



