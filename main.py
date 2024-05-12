from fastapi import APIRouter, FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi_jwt_auth.exceptions import AuthJWTException

from src.apps.users.routers import user_router

app = FastAPI(
    title="WarehouseMS",
    description="Warehouse Management System",
    version="1.0"
)


root_router = APIRouter(prefix="/api")

root_router.include_router(user_router)

app.include_router(root_router)