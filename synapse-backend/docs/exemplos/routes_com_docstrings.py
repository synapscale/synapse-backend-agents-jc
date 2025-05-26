"""Exemplo de rotas com docstrings."""

from fastapi import APIRouter
from fastapi.responses import FileResponse

router = APIRouter()


@router.get("/example")
async def example_route():
    """Rota de exemplo."""
    return {"message": "exemplo"}


@router.get("/download")
async def download_example():
    """Download de exemplo."""
    return FileResponse("example.txt")
