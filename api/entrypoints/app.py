from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
import asyncio
from api.entrypoints import schemas
from api.domain import commands
from api import bootstrap
from api.entrypoints import auth_router, options_router, polls_router, users_router

import logging
import uvicorn

print("calling bootstrap")
bus = bootstrap.bootstrap()
logger = logging.getLogger(__name__)

app = FastAPI()


@app.get("/ping")
async def root():
    return "pong"

@app.get("/health")
async def health():
    # Check that databases are up can commit.
    cmd = commands.HealthCheck()
    if await bus.handle(cmd):
        return {"message": "Healthy"}
    else:
        raise HTTPException(status_code=500, detail="Unhealthy")

@app.websocket("/ws")
async def websocket_endpoint(websocket : WebSocket):
    await websocket.accept()
    while True:
        await websocket.send_json({"message": "Hello World"})
        await asyncio.sleep(1)

# General endpoints 
@app.put("/vote", responses={
    200: {"model": schemas.SuccessResponse},
    400: {"model": schemas.ErrorResponse},
    500: {"model": schemas.ServerErrorResponse},
})
async def cast_vote(request: schemas.CastVote):
    cmd = commands.CastVote(**request.dict())
    if await bus.handle(cmd):
        return schemas.SuccessResponse()
    else:
        raise HTTPException(status_code=400, detail="Vote not cast")

app.include_router(auth_router.auth_router)
app.include_router(options_router.options_router)
app.include_router(polls_router.polls_router)
app.include_router(users_router.users_router)

if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=5000)
