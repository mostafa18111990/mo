from fastapi import APIRouter
from ..services.sectors import list_sectors, get_sector

router = APIRouter()


@router.get("")
def get_sectors():
    return list_sectors()


@router.get("/{code}")
def get_sector_detail(code: str):
    return get_sector(code)
