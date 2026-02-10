from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from routers import briefing, themes, market
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Taraga API",
    description="Wall Street to Yeouido - US to Korean Market Analysis",
    version="1.0.0",
)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler to catch unhandled exceptions
    and return a consistent error response
    """
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "message": str(exc),
            "path": str(request.url),
        },
    )

# CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(briefing.router, prefix="/api/v1/briefing", tags=["Briefing"])
app.include_router(themes.router, prefix="/api/v1/themes", tags=["Themes"])
app.include_router(market.router, prefix="/api/v1/market", tags=["Market"])


@app.get("/")
def root():
    """Root endpoint"""
    return {
        "message": "🌉 Welcome to Taraga API - Wall Street to Yeouido Bridge",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
