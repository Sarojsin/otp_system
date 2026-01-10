from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import Optional
import uvicorn

from email_otp import EmailOTPSender
from phone_otp import PhoneOTPSender
from utils import verify_otp, clear_otp

# Request models
class EmailRequest(BaseModel):
    email: EmailStr

class PhoneRequest(BaseModel):
    phone: str

class VerifyOTPRequest(BaseModel):
    identifier: str  # email or phone
    otp: str

# Initialize FastAPI app
app = FastAPI(title="OTP Verification System")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:5500", "http://localhost:8000", "*"],  # Adjust for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize senders
email_sender = EmailOTPSender()
phone_sender = PhoneOTPSender()

@app.get("/")
async def root():
    return {"message": "OTP Verification System API"}

@app.post("/send-email-otp")
async def send_email_otp(request: EmailRequest):
    """Send OTP to email address"""
    result = await email_sender.send_otp(request.email)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    
    return result

@app.post("/send-phone-otp")
async def send_phone_otp(request: PhoneRequest):
    """Send OTP to phone number via SMS"""
    # Validate phone number format (simple validation)
    if not request.phone.replace("+", "").replace(" ", "").isdigit():
        raise HTTPException(status_code=400, detail="Invalid phone number format")
    
    result = phone_sender.send_otp(request.phone)
    
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])
    
    return result

@app.post("/verify-otp")
async def verify_otp_endpoint(request: VerifyOTPRequest):
    """Verify OTP for email or phone"""
    is_valid = verify_otp(request.identifier, request.otp)
    
    if is_valid:
        # Clear OTP after successful verification
        clear_otp(request.identifier)
        return {
            "success": True,
            "message": "OTP verified successfully",
            "identifier": request.identifier
        }
    else:
        return {
            "success": False,
            "message": "Invalid OTP or OTP expired",
            "identifier": request.identifier
        }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "OTP API"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=8000, reload=True)