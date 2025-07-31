# main.py
import os
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from emi_calculator import router as emi_router

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(title="EMI Calculator API", version="1.0")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(emi_router)

# Global error handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"Success": False, "Errorcode": "500", "Message": "Internal server error"}
    )

@app.get("/")
async def root():
    return {"message": "EMI Calculator API is running."}
