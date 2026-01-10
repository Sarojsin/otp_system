# Setup and Run Guide

Follow these steps to get the OTP Verification System running on your local machine.

## 1. Environment Setup

### Create a Virtual Environment
```powershell
python -m venv venv
```

### Activate the Virtual Environment
- **Windows (PowerShell)**: `.\venv\Scripts\Activate.ps1`
- **Windows (CMD)**: `.\venv\Scripts\activate.bat`
- **Linux/macOS**: `source venv/bin/activate`

### Install Dependencies
```bash
pip install -r requirements.txt
```
*Note: If you are on Python 3.13, some core packages have been updated for compatibility.*

---

## 2. Configuration (`.env`)

Create a `.env` file in the root directory:

```env
# Gmail SMTP
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=your-email@gmail.com

# Twilio SMS
TWILIO_ACCOUNT_SID=your_sid
TWILIO_AUTH_TOKEN=your_token
TWILIO_PHONE_NUMBER=your_twilio_number
```

### Important Notes:
- **Gmail**: Use an **App Password** created in Google Security settings.
- **Twilio**: Use a **purchased Twilio number** to send SMS to countries like Nepal.

---

## 3. Running the App

### Start the Backend
```bash
python main.py
```
*The backend runs on http://localhost:8000*

### Start the Frontend
In a new terminal window:
```bash
python -m http.server 3000
```
*Access the UI at http://localhost:3000*
