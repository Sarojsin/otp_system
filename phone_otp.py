import os
from typing import Optional
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from utils import generate_otp, store_otp
from dotenv import load_dotenv

load_dotenv()

class PhoneOTPSender:
    def __init__(self):
        self.account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        self.auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        self.from_number = os.getenv('TWILIO_PHONE_NUMBER')
        
    def send_otp(self, phone_number: str) -> dict:
        """Send OTP via SMS to phone number"""
        try:
            # Generate OTP
            otp = generate_otp()
            
            # Store OTP temporarily
            store_otp(phone_number, otp)
            
            # Send SMS using Twilio
            if all([self.account_sid, self.auth_token, self.from_number]):
                client = Client(self.account_sid, self.auth_token)
                
                message = client.messages.create(
                    body=f"Your OTP code is: {otp}. Valid for 5 minutes.",
                    from_=self.from_number,
                    to=phone_number
                )
                
                return {
                    "success": True,
                    "message": "OTP sent successfully via SMS",
                    "phone": phone_number,
                    "message_id": message.sid
                }
            else:
                # For development/demo purposes
                print(f"Development mode - OTP for {phone_number}: {otp}")
                return {
                    "success": True,
                    "message": "OTP generated (demo mode - check console)",
                    "phone": phone_number,
                    "otp": otp  # Only for development!
                }
                
        except TwilioRestException as e:
            error_msg = str(e)
            if e.code == 21606:
                error_msg = f"The 'From' number {self.from_number} is not a valid Twilio number or verified Caller ID. Please check your Twilio Dashboard."
            elif e.code == 21659:
                error_msg = f"Twilio number {self.from_number} cannot send SMS to the destination country. Check your geo-permissions in Twilio."
            
            print(f"Twilio error: {error_msg}")
            return {
                "success": False,
                "message": f"Twilio Error: {error_msg}",
                "phone": phone_number
            }
        except Exception as e:
            print(f"Error sending SMS: {str(e)}")
            return {
                "success": False,
                "message": f"Failed to send OTP: {str(e)}",
                "phone": phone_number
            }