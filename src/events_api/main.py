from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.events_api.adapters.inbound.http.routers.event_router import router as event_router
from src.events_api.domain.exceptions import DomainException
from src.events_api.infrastructure.settings import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Ciclo de vida: código antes do yield roda na inicialização."""
    print(f"🚀 Events API | ambiente: {settings.environment}")
    yield
    print("👋 Events API encerrando...")


app = FastAPI(
    title="Events API",
    version="1.0.0",
    lifespan=lifespan,
    docs_url=f"{settings.api_prefix}/docs",
    redoc_url=f"{settings.api_prefix}/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.environment == "development" else [],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(DomainException)
async def domain_exception_handler(request: Request, exc: DomainException) -> JSONResponse:
    """Converte exceções de domínio em respostas HTTP padronizadas."""
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc), "error_type": type(exc).__name__},
    )


app.include_router(event_router, prefix=settings.api_prefix)


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check para load balancers."""
    return {"status": "healthy", "environment": settings.environment}