from fastapi import APIRouter, HTTPException
from api.entrypoints import schemas
from api.domain import commands 
from api.bootstrap import bus


users_router = APIRouter()


# User Endpoints
@users_router.post("/users", responses={
    200: {"model": schemas.SuccessResponse},
    400: {"model": schemas.ErrorResponse},
    500: {"model": schemas.ServerErrorResponse},
})
async def create_user(request: schemas.CreateUser):
    cmd = commands.CreateUser(**request.dict())
    if await bus.handle(cmd):
        return schemas.SuccessResponse()
    else:
        raise HTTPException(status_code=400, detail="User not created")


@users_router.get("/users/{user_id}")
async def get_user(user_id: str):
    cmd = commands.GetUser(id=user_id)
    user = await bus.handle(cmd)
    if user:
        return user
    else:
        raise HTTPException(status_code=404, detail="User not found")

@users_router.delete("/users/{user_id}")
async def delete_user(user_id: str):
    cmd = commands.DeleteUser(id=user_id)
    if await bus.handle(cmd):
        return schemas.SuccessResponse()
    else:
        raise HTTPException(status_code=400, detail="User not deleted")
