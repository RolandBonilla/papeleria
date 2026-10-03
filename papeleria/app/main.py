"""Punto de entrada: API REST (/api) y frontend estático servidos por FastAPI."""
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api import (routes_auth, routes_clients, routes_inventory, routes_products,
                     routes_reports, routes_sales)
from app.config import FRONTEND_DIR
from app.database.init_db import init_database
from app.exceptions import BusinessError


@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_database()  # es idempotente: crea tablas y carga datos solo si hace falta
    yield


app = FastAPI(
    title="Sistema de Control de Inventario y Ventas para una Papelería",
    version="1.0.0",
    lifespan=lifespan,
)


@app.exception_handler(BusinessError)
async def business_error_handler(_request: Request, exc: BusinessError) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content={"detail": str(exc)})


for module in (routes_auth, routes_products, routes_clients, routes_sales,
               routes_inventory, routes_reports):
    app.include_router(module.router)

# Debe ir al final para que /api/* tenga prioridad sobre los archivos estáticos.
app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
