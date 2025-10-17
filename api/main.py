import logging

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from api.core.security import verify_token
from api.middleware.logging import RequestLoggingMiddleware
from api.routes.auth import router as auth_router
from api.routes.books import router as books_router
from api.routes.categories import router as categories_router
from api.routes.ml import router as ml_router
from api.routes.stats import router as stats_router

app = FastAPI(title="Books API", version="1.0.0")

logging.basicConfig(level=logging.INFO, format="%(message)s")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RequestLoggingMiddleware)

instrumentator = Instrumentator(
    should_group_status_codes=True,
    excluded_handlers=["/metrics", "/docs", "/openapi.json"],
)
instrumentator.instrument(app)


@app.on_event("startup")
async def _startup() -> None:
    instrumentator.expose(app, include_in_schema=False)

@app.get("/api/v1/health")
def health():
    return {"status": "ok"}

app.include_router(auth_router, prefix="/api/v1")
app.include_router(books_router, prefix="/api/v1", dependencies=[Depends(verify_token)])
app.include_router(categories_router, prefix="/api/v1", dependencies=[Depends(verify_token)])
app.include_router(stats_router, prefix="/api/v1", dependencies=[Depends(verify_token)])
app.include_router(ml_router, prefix="/api/v1", dependencies=[Depends(verify_token)])
