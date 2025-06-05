from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.api import api_router
from app.core.config import settings, validate_settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_PREFIX}/openapi.json",
    docs_url=f"{settings.API_PREFIX}/docs",
    redoc_url=f"{settings.API_PREFIX}/redoc",
    debug=settings.DEBUG,
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def validate_config():
    try:
        config = validate_settings()
        
        critical_settings = [
            "SUPABASE_URL", "SUPABASE_KEY", "SECRET_KEY", "BUNNYCDN_API_KEY"
        ]
        
        print("\n✅ Configuration validation results:")
        print("-----------------------------------")
        for setting in critical_settings:
            value = getattr(config, setting, None)
            if value:
                if len(str(value)) > 8:
                    masked = f"{str(value)[:2]}...{str(value)[-2:]}"
                else:
                    masked = "***" 
                print(f"✓ {setting}: {masked}")
            else:
                print(f"✗ {setting}: MISSING")
        print("-----------------------------------")
        print("✅ Application will start with the above configuration.\n")
        
    except Exception as e:
        print(f"\n❌ Configuration validation failed: {str(e)}")
        import sys
        sys.exit(1)

app.include_router(api_router, prefix=settings.API_PREFIX)
app.include_router(api_router, prefix="/v1")


@app.get("/")
def root():
    return {"message": f"Welcome to {settings.PROJECT_NAME} API"}


@app.get("/health")
def health_check():
    return {"status": "ok"}
