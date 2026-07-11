"""
FastAPI application entry point.

Mounts all routers and loads the dataset on startup
so every request is fast — no repeated file reads.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.core.config import get_settings
from backend.core.logging import configure_logging, get_logger
from backend.api.routes import health, claims, pipeline, evaluation
from backend.api.dependencies import get_bundle

logger = get_logger(__name__)


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging(settings.log_level)

    app = FastAPI(
        title="Multi-Modal Evidence Review API",
        description="Automated damage claims adjudication system",
        version="1.0.0",
    )

    # Allow frontend to call the API
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Load dataset once when server starts
    @app.on_event("startup")
    async def startup_event():
        logger.info("Server starting up...")
        try:
            get_bundle()
            logger.info("Dataset loaded successfully.")
        except Exception as exc:
            logger.warning("Could not preload dataset: %s", exc)

    # Mount all routers
    app.include_router(health.router, tags=["Health"])
    app.include_router(claims.router, tags=["Claims"])
    app.include_router(pipeline.router, tags=["Pipeline"])
    app.include_router(evaluation.router, tags=["Evaluation"])

    return app


app = create_app()