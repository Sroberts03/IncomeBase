from fastapi import FastAPI
from dotenv import load_dotenv
import os
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.container import container
from app.api.v1.file_routes import router as file_router
from app.api.v1.lender_routes import router as lender_router

# 2. Define the Lifespan Logic
@asynccontextmanager
async def lifespan(app: FastAPI):
    # STARTUP: Create Singletons (Agents, DAOs, Handlers)
    print("🚀 Initializing Summit West Engine...")
    await container.initialize() 
    yield
    # SHUTDOWN: Clean up resources if needed
    print("💤 Shutting down...")

# 3. Initialize App with Lifespan
app = FastAPI(
    title="IncomeBase API",
    description="AI-powered income reconstruction for self-employed borrowers",
    version="0.1.0",
    lifespan=lifespan 
)

# 4. CORS Middleware
load_dotenv()
origins = [
    os.getenv("FRONTEND_ORIGIN"),
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 5. Register Routers
app.include_router(file_router)
app.include_router(lender_router)

# 6. Health Checks
@app.get("/", tags=["Health"])
async def root():
    return {
        "app": "IncomeBase",
        "status": "online",
        "organization": "Summit West Technologies"
    }

@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy"}