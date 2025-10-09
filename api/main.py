from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes.books import router as books_router
from api.routes.categories import router as categories_router
from api.routes.stats import router as stats_router

app = FastAPI(title="Books API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/v1/health")
def health():
    return {"status": "ok"}

app.include_router(books_router, prefix="/api/v1")
app.include_router(categories_router, prefix="/api/v1")
app.include_router(stats_router, prefix="/api/v1")
