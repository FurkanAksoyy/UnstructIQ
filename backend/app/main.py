from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api import routes  # YENİ SATIR

# FastAPI instance
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="AI-powered data structuring and visualization platform"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes - YENİ SATIRLAR
app.include_router(routes.router, prefix="/api", tags=["API"])

# Health Check Endpoint
@app.get("/")
async def root():
    return {
        "message": "Welcome to UnstructIQ API",
        "version": settings.VERSION,
        "status": "running"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "upload_dir": settings.UPLOAD_DIR,
        "processed_dir": settings.PROCESSED_DIR
    }