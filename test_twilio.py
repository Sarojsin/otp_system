import os
from phone_otp import PhoneOTPSender
from dotenv import load_dotenv

load_dotenv()

def test_same_number():
    print("Testing same 'To' and 'From' number...")
    sender = PhoneOTPSender()
    from_num = os.getenv('TWILIO_PHONE_NUMBER')
    
    if not from_num:
        print("Error: TWILIO_PHONE_NUMBER not set in .env")
        return

    result = sender.send_otp(from_num)
    print(f"Result: {result}")
    
    if result['success'] == False and "cannot be the same" in result['message']:
        print("SUCCESS: Validation caught same-number error.")
    else:
        print("FAILURE: Validation did not catch same-number error.")

if __name__ == "__main__":
    test_same_number()
