from fastapi import APIRouter

from app.schemas.message import Message


router = APIRouter(prefix='/api', tags=['Test'])


@router.get('', response_model=Message)
async def hello():
    return {"detail": {"msg": "Hello from Romakot159"}}

