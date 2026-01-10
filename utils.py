import random
import time
from typing import Dict, Optional

# In-memory storage for OTPs (use Redis or database in production)
otp_storage: Dict[str, Dict] = {}

def generate_otp(length: int = 6) -> str:
    """Generate a random OTP of specified length"""
    digits = "0123456789"
    return ''.join(random.choice(digits) for _ in range(length))

def store_otp(identifier: str, otp: str, expiry_minutes: int = 5) -> None:
    """Store OTP with expiry time"""
    expiry_time = time.time() + (expiry_minutes * 60)
    otp_storage[identifier] = {
        'otp': otp,
        'expiry': expiry_time,
        'attempts': 0,
        'verified': False
    }

def get_otp(identifier: str) -> Optional[Dict]:
    """Retrieve OTP if not expired"""
    if identifier not in otp_storage:
        return None
    
    otp_data = otp_storage[identifier]
    if time.time() > otp_data['expiry']:
        # Remove expired OTP
        del otp_storage[identifier]
        return None
    
    return otp_data

def verify_otp(identifier: str, user_otp: str, max_attempts: int = 3) -> bool:
    """Verify OTP with attempt limiting"""
    otp_data = get_otp(identifier)
    
    if not otp_data:
        return False
    
    if otp_data['attempts'] >= max_attempts:
        del otp_storage[identifier]
        return False
    
    if otp_data['otp'] == user_otp:
        otp_data['verified'] = True
        return True
    
    otp_data['attempts'] += 1
    return False

def clear_otp(identifier: str) -> None:
    """Remove OTP from storage"""
    if identifier in otp_storage:
        del otp_storage[identifier]