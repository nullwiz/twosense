from fastapi import APIRouter, HTTPException
from api.entrypoints import schemas
from api.domain import commands
from api.bootstrap import bus

options_router = APIRouter()


# Options Endpoints
@options_router.post("/options", responses={
    200: {"model": schemas.SuccessResponse},
    400: {"model": schemas.ErrorResponse},
    500: {"model": schemas.ServerErrorResponse},
})
async def create_option(request: schemas.CreateOption):
    cmd = commands.CreateOption(**request.dict())
    if await bus.handle(cmd):
        return schemas.SuccessResponse()
    else:
        raise HTTPException(status_code=400, detail="Option not created")

@options_router.get("/options/{option_id}")
async def get_option(option_id: str):
    cmd = commands.GetOption(id=option_id)
    option = await bus.handle(cmd)
    if option:
        return option
    else:
        raise HTTPException(status_code=404, detail="Option not found")

@options_router.delete("/options/{option_id}")
async def delete_option(option_id: str):
    cmd = commands.DeleteOption(id=option_id)
    if await bus.handle(cmd):
        return schemas.SuccessResponse()
    else:
        raise HTTPException(status_code=400, detail="Option not deleted")
