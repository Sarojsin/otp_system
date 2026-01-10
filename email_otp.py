import os
from typing import Optional
from aiosmtplib import SMTP
from email.message import EmailMessage
from utils import generate_otp, store_otp
from dotenv import load_dotenv

load_dotenv()

class EmailOTPSender:
    def __init__(self):
        self.smtp_host = os.getenv('SMTP_HOST', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', 587))
        self.smtp_username = os.getenv('SMTP_USERNAME')
        self.smtp_password = os.getenv('SMTP_PASSWORD')
        self.from_email = os.getenv('FROM_EMAIL', 'noreply@example.com')
    
    async def send_otp(self, email: str) -> dict:
        """Send OTP to email address"""
        try:
            # Generate OTP
            otp = generate_otp()
            
            # Store OTP temporarily
            store_otp(email, otp)
            
            # Create email message
            msg = EmailMessage()
            msg["From"] = self.from_email
            msg["To"] = email
            msg["Subject"] = "Your OTP Code"
            
            # Email body
            body = f"""
            Hello,
            
            Your One-Time Password (OTP) for verification is:
            
            {otp}
            
            This OTP is valid for 5 minutes.
            
            If you didn't request this code, please ignore this email.
            
            Best regards,
            OTP Verification System
            """
            
            msg.set_content(body)
            
            # Send email
            if all([self.smtp_username, self.smtp_password]):
                async with SMTP(
                    hostname=self.smtp_host,
                    port=self.smtp_port,
                    use_tls=False,
                    start_tls=True
                ) as smtp:
                    await smtp.login(self.smtp_username, self.smtp_password)
                    await smtp.send_message(msg)
                
                return {
                    "success": True,
                    "message": "OTP sent successfully to email",
                    "email": email
                }
            else:
                # For development/demo purposes
                print(f"Development mode - OTP for {email}: {otp}")
                return {
                    "success": True,
                    "message": "OTP generated (demo mode - check console)",
                    "email": email,
                    "otp": otp  # Only for development!
                }
                
        except Exception as e:
            print(f"Error sending email: {str(e)}")
            return {
                "success": False,
                "message": f"Failed to send OTP: {str(e)}",
                "email": email
            }