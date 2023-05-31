from fastapi import APIRouter, HTTPException
from api.entrypoints import schemas
from api.domain import commands
from api.bootstrap import bus

polls_router = APIRouter()

# Poll Endpoints
@polls_router.post("/polls", responses={
    200: {"model": schemas.SuccessResponse},
    400: {"model": schemas.ErrorResponse},
    500: {"model": schemas.ServerErrorResponse},
})
async def create_poll(request: schemas.CreatePoll):
    cmd = commands.CreatePoll(**request.dict())
    if await bus.handle(cmd):
        return schemas.SuccessResponse()
    else:
        raise HTTPException(status_code=400, detail="Poll not created")

@polls_router.get("/polls/{poll_id}")
async def get_poll(poll_id: str):
    cmd = commands.GetPoll(id=poll_id)
    poll = await bus.handle(cmd)
    if poll:
        return poll
    else:
        raise HTTPException(status_code=404, detail="Poll not found")

@polls_router.delete("/polls/{poll_id}")
async def delete_poll(poll_id: str):
    cmd = commands.DeletePoll(id=poll_id)
    if await bus.handle(cmd):
        return schemas.SuccessResponse()
    else:
        raise HTTPException(status_code=400, detail="Poll not deleted")
