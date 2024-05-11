from fastapi import APIRouter, FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi_jwt_auth.exceptions import AuthJWTException

app = FastAPI(
    title="WarehouseMS",
    description="Warehouse Management System",
    version="1.0"
)


root_router = APIRouter(prefix="/api")