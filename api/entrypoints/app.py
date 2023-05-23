from fastapi import FastAPI, HTTPException
from api.entrypoints import schemas
from api.domain import commands
from api import bootstrap
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


@app.put("/location", responses={
    200: {"model": schemas.SuccessResponse},
    400: {"model": schemas.ErrorResponse},
    500: {"model": schemas.ServerErrorResponse},
})
async def put_location(location: schemas.PutLocation):
    cmd = commands.PutLocation(
        location.timestamp,
        location.lat,
        location.long,
        location.accuracy,
        location.speed,
        location.user_id,
    )
    try:
        await bus.handle(cmd)
    # We shouldn't get any exceptions here, but if we do, we want to log them
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail="Server error")

if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=5000)
