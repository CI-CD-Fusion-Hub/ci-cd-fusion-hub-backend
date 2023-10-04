from fastapi import APIRouter

from utils.response import ok

router = APIRouter()


@router.get("/status", tags=["status"])
async def status():
    return ok(message="Service is healthy!")
