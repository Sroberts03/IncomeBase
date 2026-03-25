from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# 1. Initialize the App
app = FastAPI(
    title="IncomeBase API",
    description="AI-powered income reconstruction for self-employed borrowers",
    version="0.1.0"
)

# 2. Configure CORS (Cross-Origin Resource Sharing)
# This is MANDATORY for your Vite (React) frontend to talk to this backend
origins = [
    "http://localhost:5173", 
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allows GET, POST, DELETE, etc.
    allow_headers=["*"],  # Allows custom headers like Authorization
)

# 3. Include Routers (The "Plug-ins")
# This keeps main.py clean by importing routes from other files
#app.include_router(
    #prefix="/api/v1/underwriting", 
    #tags=["Underwriting Engine"]
#)

# 4. Root/Health Check Endpoints
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