from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

import config
import database
import models
from dependencies import limiter
from routers import auth, inventory, recipes, shopping, users, utils
from seed_data import seed_database


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create tables and seed data
    models.Base.metadata.create_all(bind=database.engine)
    seed_database()
    yield


app = FastAPI(title="Gustovify API", version="1.4", lifespan=lifespan)

# Rate Limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS — config'ten okunan origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

# Validation error handler — kullanici dostu Turkce hata mesajlari
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for error in exc.errors():
        field = " -> ".join(str(loc) for loc in error["loc"] if loc != "body")
        errors.append(f"{field}: {error['msg']}")
    return JSONResponse(
        status_code=422,
        content={"detail": "Gecersiz veri: " + "; ".join(errors)},
    )


# Router'ları ekle
app.include_router(auth.router)
app.include_router(recipes.router)
app.include_router(inventory.router)
app.include_router(shopping.router)
app.include_router(users.router)
app.include_router(utils.router)


@app.get("/")
def read_root():
    return {"status": "online", "message": "Gustovify Veritabanı Bağlantısı Aktif"}
