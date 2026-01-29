from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import briefing, themes, market

app = FastAPI(
    title="Taraga API",
    description="Wall Street to Yeouido - US to Korean Market Analysis",
    version="1.0.0",
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
