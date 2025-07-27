"""
FastAPI main application for Minesweeper game.
"""

import logging
from datetime import datetime
from fastapi import FastAPI, Request, status
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import uvicorn

from .routes.game_routes import router as game_router
from .controllers.game_controller import game_controller
from .models.game_models import HealthResponse, ErrorResponse
from .utils.config import settings


# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="Minesweeper API",
    description="A modern web API for the classic Minesweeper game with leaderboard functionality",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Add trusted host middleware for security
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # Configure appropriately for production
)

# Include API routes
app.include_router(game_router)

# Mount static files for frontend
app.mount("/static", StaticFiles(directory="public"), name="static")


@app.get("/", 
         summary="Serve Frontend",
         description="Serve the main Minesweeper game interface")
async def serve_frontend():
    """Serve the main HTML file for the Minesweeper game."""
    return FileResponse("public/index.html")


@app.get("/style.css")
async def serve_css():
    """Serve the CSS file."""
    return FileResponse("public/style.css", media_type="text/css")


@app.get("/script.js")
async def serve_js():
    """Serve the JavaScript file."""
    return FileResponse("public/script.js", media_type="application/javascript")


@app.get("/favicon.ico", include_in_schema=False)
async def serve_favicon():
    """Return empty response for favicon requests to avoid 404 errors."""
    from fastapi.responses import Response
    return Response(status_code=204, headers={"Content-Length": "0"})


@app.get("/health",
         response_model=HealthResponse,
         summary="Health Check",
         description="Check the health status of the API and database")
async def health_check():
    """
    Perform a comprehensive health check of the application.
    
    Returns the current status, timestamp, and version information.
    """
    try:
        # Check database connectivity
        db_healthy = await game_controller.health_check()
        
        if db_healthy:
            return HealthResponse(
                status="healthy",
                timestamp=datetime.utcnow().isoformat(),
                version="1.0.0"
            )
        else:
            return JSONResponse(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                content=HealthResponse(
                    status="unhealthy - database connection failed",
                    timestamp=datetime.utcnow().isoformat(),
                    version="1.0.0"
                ).model_dump()
            )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=HealthResponse(
                status="unhealthy - internal error",
                timestamp=datetime.utcnow().isoformat(),
                version="1.0.0"
            ).model_dump()
        )


@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    """Handle 404 errors by serving the frontend for client-side routing."""
    # For API routes, return JSON error
    if request.url.path.startswith("/api/"):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=ErrorResponse(
                error="Not Found",
                detail=f"The requested endpoint {request.url.path} was not found"
            ).model_dump()
        )
    
    # For other routes, serve the frontend (SPA routing)
    return FileResponse("public/index.html")


@app.exception_handler(500)
async def internal_server_error_handler(request: Request, exc):
    """Handle internal server errors."""
    logger.error(f"Internal server error: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            error="Internal Server Error",
            detail="An unexpected error occurred"
        ).model_dump()
    )


@app.on_event("startup")
async def startup_event():
    """Application startup event handler."""
    logger.info("Starting Minesweeper API server...")
    logger.info(f"Debug mode: {settings.debug}")
    logger.info(f"Database URL: {settings.database_url}")
    logger.info("Server started successfully")


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event handler."""
    logger.info("Shutting down Minesweeper API server...")
    logger.info("Server shutdown complete")


def main():
    """Main entry point for running the application."""
    uvicorn.run(
        "server.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )


if __name__ == "__main__":
    main()
