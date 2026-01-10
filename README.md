# OTP Verification System

A secure authentication system providing One-Time Password (OTP) verification via Email (Gmail SMTP) and SMS (Twilio).

## Features
- **Email OTP**: Sends codes using Gmail's SMTP server with STARTTLS.
- **SMS OTP**: Sends codes using Twilio's Messaging API.
- **FastAPI Backend**: High-performance API for sending and verifying OTPs.
- **Glassmorphism UI**: Modern, responsive frontend for user interaction.

## Prerequisites
- Python 3.10+ (Tested on Python 3.13)
- Gmail account with 2-Step Verification enabled
- Twilio account with a purchased phone number

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Sarojsin/otp_system.git
   cd otp_system
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/scripts/activate  # On Windows: .\venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

Create a `.env` file in the root directory with the following:

```env
# SMTP Configuration (Gmail)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-google-app-password
FROM_EMAIL=your-email@gmail.com

# Twilio Configuration
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=your_twilio_purchased_number
```

> [!IMPORTANT]
> - **Gmail**: You must use a **Google App Password**, not your regular password.
> - **Twilio**: You must use a number **purchased from Twilio** to send SMS to international numbers like Nepal.

## Running the Application

### 1. Start the Backend (FastAPI)
```bash
python main.py
```
The API will be available at [http://localhost:8000](http://localhost:8000).

### 2. Start the Frontend
You can use any light server, for example:
```bash
python -m http.server 3000
```
Then open [http://localhost:3000](http://localhost:3000) in your browser.

## Known Issues
- **Twilio SMS (Nepal)**: If you receive a "Geo-Permissions" error despite allowing Nepal in the console, ensure you are using a purchased Twilio number and have enabled SMS permissions in the Twilio Messaging Geo-Permissions settings.
