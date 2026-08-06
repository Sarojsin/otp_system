# OTP Verification System — Detailed Workflow

This document explains the complete workflow of the OTP Verification System, from user interaction on the frontend to backend processing and external service communication. It is intended for new developers who need to understand how every part of the system connects.

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Architecture](#architecture)
3. [File-by-File Breakdown](#file-by-file-breakdown)
4. [Complete User Workflows](#complete-user-workflows)
   - [Workflow 1: Send OTP via Email](#workflow-1-send-otp-via-email)
   - [Workflow 2: Send OTP via SMS (Phone)](#workflow-2-send-otp-via-sms-phone)
   - [Workflow 3: Verify OTP](#workflow-3-verify-otp)
5. [Backend API Endpoints](#backend-api-endpoints)
6. [Data Flow Diagrams](#data-flow-diagrams)
7. [Key Functions Reference](#key-functions-reference)
8. [Configuration & Environment](#configuration--environment)
9. [Error Handling](#error-handling)
10. [Running the Application](#running-the-application)

---

## Project Overview

The OTP Verification System is a web application that provides one-time password authentication via two channels:

- **Email** — Uses Gmail's SMTP server (via `aiosmtplib`) to send a 6-digit OTP.
- **SMS** — Uses Twilio's Messaging API to send a 6-digit OTP to a phone number.

The system consists of:

| Layer | Technology | File(s) |
|-------|-----------|---------|
| Frontend | HTML, CSS, JavaScript | `index.html`, `style.css`, `script.js` |
| Backend | Python, FastAPI | `main.py`, `email_otp.py`, `phone_otp.py`, `utils.py` |
| Configuration | Environment variables | `.env` |
| Dependencies | pip packages | `requirements.txt` |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER'S BROWSER                          │
│  index.html  →  style.css  →  script.js                       │
│  (UI rendered)   (styling)   (event handlers + API calls)     │
└──────────────────────────┬──────────────────────────────────────┘
                           │  HTTP requests (fetch API)
                           │  POST /send-email-otp
                           │  POST /send-phone-otp
                           │  POST /verify-otp
                           │  GET  /health
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    FASTAPI BACKEND (main.py)                    │
│                                                                │
│  ┌──────────────┐  ┌───────────────┐  ┌────────────────────┐ │
│  │ EmailOTPSender│  │ PhoneOTPSender│  │ utils.py           │ │
│  │ (email_otp.py)│  │ (phone_otp.py)│  │ - generate_otp()   │ │
│  │               │  │               │  │ - store_otp()      │ │
│  │ - send_otp()  │  │ - send_otp()  │  │ - get_otp()        │ │
│  │ - SMTP send   │  │ - Twilio SMS  │  │ - verify_otp()     │ │
│  └──────────────┘  └───────────────┘  │ - clear_otp()      │ │
│                                        └────────────────────┘ │
└──────────────────────────┬──────────────────────────────────────┘
                           │
              ┌────────────┴────────────┐
              ▼                         ▼
     ┌────────────────┐      ┌────────────────┐
     │  Gmail SMTP    │      │  Twilio API    │
     │  (smtp.gmail)  │      │  (SMS gateway) │
     └────────────────┘      └────────────────┘
```

---

## File-by-File Breakdown

### `main.py` — Application Entry Point & API Router

This is the core FastAPI application. It:

1. **Imports dependencies**: `FastAPI`, `CORSMiddleware`, Pydantic models, `uvicorn`, and the custom modules (`email_otp`, `phone_otp`, `utils`).
2. **Defines Pydantic request models**:
   - `EmailRequest` — has one field: `email` (validated as `EmailStr`).
   - `PhoneRequest` — has one field: `phone` (string).
   - `VerifyOTPRequest` — has two fields: `identifier` (email or phone string) and `otp` (string).
3. **Creates the FastAPI app instance** with title `"OTP Verification System"`.
4. **Adds CORS middleware** allowing requests from `localhost:3000`, `127.0.0.1:3000`, `localhost:5500`, `localhost:8000`, and `*` (all origins).
5. **Instantiates sender objects**: `email_sender = EmailOTPSender()` and `phone_sender = PhoneOTPSender()`.
6. **Defines API endpoints** (see [Backend API Endpoints](#backend-api-endpoints)).
7. **Runs the server** on `localhost:8000` with auto-reload when executed directly.

**Function call sequence when the app starts:**
1. Python executes `main.py` top-to-bottom.
2. `from email_otp import EmailOTPSender` — loads the `EmailOTPSender` class (which calls `load_dotenv()` at module level).
3. `from phone_otp import PhoneOTPSender` — loads the `PhoneOTPSender` class (which also calls `load_dotenv()` at module level).
4. `from utils import verify_otp, clear_otp` — loads utility functions.
5. `email_sender = EmailOTPSender()` — creates an instance; reads `.env` variables into `self.smtp_host`, `self.smtp_port`, `self.smtp_username`, `self.smtp_password`, `self.from_email`.
6. `phone_sender = PhoneOTPSender()` — creates an instance; reads `.env` variables into `self.account_sid`, `self.auth_token`, `self.from_number`.
7. `uvicorn.run("main:app", host="localhost", port=8000, reload=True)` — starts the ASGI server.

---

### `email_otp.py` — Email OTP Sender

This module defines the `EmailOTPSender` class.

**On initialization (`__init__`):**
- Reads SMTP configuration from environment variables:
  - `SMTP_HOST` (default: `smtp.gmail.com`)
  - `SMTP_PORT` (default: `587`)
  - `SMTP_USERNAME`
  - `SMTP_PASSWORD`
  - `FROM_EMAIL` (default: `noreply@example.com`)

**On sending OTP (`send_otp(email)`):**
1. Calls `generate_otp()` from `utils.py` — produces a random 6-digit string.
2. Calls `store_otp(email, otp)` from `utils.py` — saves the OTP in the in-memory `otp_storage` dict with a 5-minute expiry.
3. Constructs an `EmailMessage` object with:
   - `From`: `self.from_email`
   - `To`: the recipient `email`
   - `Subject`: `"Your OTP Code"`
   - `Body`: a formatted message containing the OTP and a 5-minute expiry notice.
4. **If SMTP credentials are present** (`SMTP_USERNAME` and `SMTP_PASSWORD` are both set):
   - Creates an `aiosmtplib.SMTP` connection to `self.smtp_host` on `self.smtp_port`.
   - Uses `start_tls=True` for encryption (no SSL on connect, upgrades via STARTTLS).
   - Logs in with `self.smtp_username` and `self.smtp_password`.
   - Sends the email via `smtp.send_message(msg)`.
   - Returns `{"success": True, "message": "OTP sent successfully to email", "email": email}`.
5. **If SMTP credentials are missing** (development/demo mode):
   - Prints the OTP to the console.
   - Returns `{"success": True, "message": "OTP generated (demo mode - check console)", "email": email, "otp": otp}`.
6. **On exception**: catches any error, prints it, and returns `{"success": False, "message": "Failed to send OTP: <error>", "email": email}`.

---

### `phone_otp.py` — Phone/SMS OTP Sender

This module defines the `PhoneOTPSender` class.

**On initialization (`__init__`):**
- Reads Twilio configuration from environment variables:
  - `TWILIO_ACCOUNT_SID`
  - `TWILIO_AUTH_TOKEN`
  - `TWILIO_PHONE_NUMBER`

**On sending OTP (`send_otp(phone_number)`):**
1. **Validates that the recipient is not the same as the sender**:
   - Strips spaces and dashes from both `phone_number` and `self.from_number`.
   - If they match, returns `{"success": False, "message": "Twilio Error: 'To' and 'From' number cannot be the same...", "phone": phone_number}`.
2. Calls `generate_otp()` from `utils.py` — produces a random 6-digit string.
3. Calls `store_otp(phone_number, otp)` from `utils.py` — saves the OTP in the in-memory `otp_storage` dict with a 5-minute expiry.
4. **If Twilio credentials are present** (`TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_PHONE_NUMBER` are all set):
   - Creates a `twilio.rest.Client` with the account SID and auth token.
   - Calls `client.messages.create()` with:
     - `body`: `"Your OTP code is: {otp}. Valid for 5 minutes."`
     - `from_`: `self.from_number`
     - `to`: `phone_number`
   - Returns `{"success": True, "message": "OTP sent successfully via SMS", "phone": phone_number, "message_id": message.sid}`.
5. **If Twilio credentials are missing** (development/demo mode):
   - Prints the OTP to the console.
   - Returns `{"success": True, "message": "OTP generated (demo mode - check console)", "phone": phone_number, "otp": otp}`.
6. **On `TwilioRestException`**: catches Twilio-specific errors and maps error codes to human-readable messages:
   - `21606` — From number is not a valid Twilio number or verified Caller ID.
   - `21659` — Geo-permission issue (cannot send to destination country).
   - `21211` — The recipient phone number is invalid.
   - `21266` — To and From numbers cannot be the same.
   - Any other Twilio error — returns the raw error message.
7. **On generic exception**: catches any other error and returns a failure response.

---

### `utils.py` — Shared Utility Functions

This module provides the core OTP logic used by both `email_otp.py` and `phone_otp.py`.

**Module-level state:**
- `otp_storage: Dict[str, Dict]` — an in-memory dictionary that maps identifiers (email or phone) to OTP data. This is ephemeral; it resets when the server restarts. In production, this should be replaced with Redis or a database.

**Functions:**

#### `generate_otp(length=6) -> str`
- Generates a random numeric OTP of the specified length (default 6).
- Uses `random.choice("0123456789")` called `length` times.
- Returns the OTP as a string (e.g., `"482917"`).

#### `store_otp(identifier: str, otp: str, expiry_minutes=5) -> None`
- Calculates an expiry timestamp: `time.time() + (expiry_minutes * 60)`.
- Stores the OTP data in `otp_storage[identifier]` as a dict:
  ```python
  {
      "otp": otp,           # the generated OTP string
      "expiry": expiry_time, # Unix timestamp when it expires
      "attempts": 0,         # number of failed verification attempts
      "verified": False      # whether the OTP has been successfully verified
  }
  ```

#### `get_otp(identifier: str) -> Optional[Dict]`
- Checks if `identifier` exists in `otp_storage`.
- If not found, returns `None`.
- If found, checks whether the current time has exceeded `otp_data['expiry']`.
  - If expired, deletes the entry from `otp_storage` and returns `None`.
  - If still valid, returns the full OTP data dict.

#### `verify_otp(identifier: str, user_otp: str, max_attempts=3) -> bool`
1. Calls `get_otp(identifier)` to retrieve stored OTP data.
2. If no data is returned (identifier not found or expired), returns `False`.
3. If `otp_data['attempts'] >= max_attempts` (3), deletes the OTP from storage and returns `False` (locks out further attempts).
4. Compares `otp_data['otp']` with `user_otp`:
   - If they match: sets `otp_data['verified'] = True` and returns `True`.
   - If they don't match: increments `otp_data['attempts']` by 1 and returns `False`.

#### `clear_otp(identifier: str) -> None`
- Deletes the OTP entry for `identifier` from `otp_storage` if it exists.
- Called after a successful verification to prevent reuse of the OTP.

---

### `index.html` — Frontend UI Structure

The HTML file defines the user interface with three main sections:

1. **Email OTP Card** — contains:
   - An `<input type="email" id="email">` for the email address.
   - A `<button id="sendEmailOtp">` that triggers email OTP sending.
   - A `<div id="emailResult">` for displaying success/error messages.

2. **SMS OTP Card** — contains:
   - An `<input type="tel" id="phone">` for the phone number.
   - A `<button id="sendPhoneOtp">` that triggers SMS OTP sending.
   - A `<div id="phoneResult">` for displaying success/error messages.

3. **Verify OTP Card** — contains:
   - An `<input type="text" id="identifier">` for the email or phone used to receive the OTP.
   - An `<input type="text" id="otp" maxlength="6">` for the 6-digit OTP code.
   - A `<button id="verifyOtp">` that triggers OTP verification.
   - A `<div id="verifyResult">` for displaying success/error messages.

4. **Info Box** — displays a 4-step "How it works" guide and a note about the 5-minute expiry and 3-attempt limit.

5. **Footer** — copyright and technology stack info.

The page loads Font Awesome icons from a CDN and includes `script.js` at the bottom.

---

### `style.css` — Frontend Styling

The CSS file provides:
- A gradient background (`#667eea` to `#764ba2`).
- A centered white container with rounded corners and a box shadow (glassmorphism effect).
- A dark header with a gradient.
- A responsive CSS Grid layout (`auto-fit, minmax(350px, 1fr)`) for the cards.
- Three button styles: `.btn-email` (blue gradient), `.btn-phone` (green gradient), `.btn-verify` (purple gradient).
- Three result message styles: `.result.success` (green), `.result.error` (red), `.result.info` (cyan).
- A pulse animation for the OTP input field when an OTP is sent.
- Responsive design: on screens narrower than 768px, the grid collapses to a single column.

---

### `script.js` — Frontend Logic & Event Handlers

This is the most interactive file. It handles all user interactions and communicates with the backend via `fetch()`.

**Initialization (runs on `DOMContentLoaded`):**
1. Calls `checkBackendHealth()` — sends a `GET` request to `http://localhost:8000/health`. If the backend is unreachable, it displays a warning message in both `emailResult` and `phoneResult`.
2. If running on `localhost` or `127.0.0.1`, auto-fills demo values:
   - `emailInput.value = 'test@example.com'`
   - `phoneInput.value = '+1234567890'`

**DOM Element References (cached at script load):**
- `emailInput`, `phoneInput`, `identifierInput`, `otpInput` — input fields.
- `sendEmailBtn`, `sendPhoneBtn`, `verifyOtpBtn` — buttons.
- `emailResult`, `phoneResult`, `verifyResult` — message display divs.

---

## Complete User Workflows

### Workflow 1: Send OTP via Email

This is the sequence of events when a user requests an OTP to their email address.

```
USER ACTION                          SYSTEM RESPONSE
============                         ===============
1. User types email into #email field
2. User clicks "Send Email OTP" button
   │
   ▼
script.js: sendEmailBtn click handler
   │
   ├─ Reads emailInput.value.trim()
   ├─ Checks if email is empty → shows error, stops
   ├─ Validates email format with regex /^[^\s@]+@[^\s@]+\.[^\s@]+$/
   │   → if invalid, shows error, stops
   ├─ Changes button to "Sending..." spinner, disables it
   │
   ▼
script.js: makeRequest() called
   │
   ├─ HTTP POST to http://localhost:8000/send-email-otp
   ├─ Request body: { "email": "user@example.com" }
   ├─ Content-Type: application/json
   │
   ▼
main.py: /send-email-otp endpoint
   │
   ├─ FastAPI parses request body into EmailRequest(email="user@example.com")
   ├─ Calls: email_sender.send_otp(request.email)
   │       │
   │       ▼
   │     email_otp.py: EmailOTPSender.send_otp("user@example.com")
   │       │
   │       ├─ otp = generate_otp()          → e.g., "482917"
   │       ├─ store_otp("user@example.com", "482917")
   │       │       │
   │       │       ▼
   │       │     utils.py: otp_storage["user@example.com"] = {
   │       │         "otp": "482917",
   │       │         "expiry": time.time() + 300,  // 5 min from now
   │       │         "attempts": 0,
   │       │         "verified": False
   │       │     }
   │       │
   │       ├─ Creates EmailMessage with subject "Your OTP Code"
   │       ├─ If SMTP credentials present:
   │       │   ├─ Connects to smtp.gmail.com:587 via aiosmtplib.SMTP
   │       │   ├─ Upgrades to TLS with start_tls=True
   │       │   ├─ Logs in with SMTP_USERNAME / SMTP_PASSWORD
   │       │   ├─ Sends the email message
   │       │   └─ Returns {"success": True, "message": "OTP sent successfully to email", "email": "user@example.com"}
   │       └─ If SMTP credentials missing (demo mode):
   │           ├─ Prints "Development mode - OTP for user@example.com: 482917" to console
   │           └─ Returns {"success": True, "message": "OTP generated (demo mode - check console)", "email": "user@example.com", "otp": "482917"}
   │
   ▼
main.py: receives result from email_sender.send_otp()
   │
   ├─ If result["success"] is False → raises HTTPException(400, detail=result["message"])
   └─ If result["success"] is True → returns result as JSON response
   │
   ▼
script.js: receives JSON response
   │
   ├─ If result.success is True:
   │   ├─ Shows green success message: "✅ OTP sent successfully to email. Check your email for the OTP."
   │   ├─ Auto-fills identifierInput.value with the email address
   │   └─ Adds "pulse" CSS class to otpInput (visual animation to draw attention)
   └─ If result.success is False:
       └─ Shows red error message with the failure reason
   │
   ▼
script.js: finally block
   ├─ Resets button text to "Send Email OTP" (with paper-plane icon)
   └─ Re-enables the button
```

---

### Workflow 2: Send OTP via SMS (Phone)

This is the sequence of events when a user requests an OTP to their phone number.

```
USER ACTION                          SYSTEM RESPONSE
============                         ===============
1. User types phone number into #phone field
2. User clicks "Send SMS OTP" button
   │
   ▼
script.js: sendPhoneBtn click handler
   │
   ├─ Reads phoneInput.value.trim()
   ├─ Checks if phone is empty → shows error, stops
   ├─ Changes button to "Sending..." spinner, disables it
   │
   ▼
script.js: makeRequest() called
   │
   ├─ HTTP POST to http://localhost:8000/send-phone-otp
   ├─ Request body: { "phone": "+1234567890" }
   │
   ▼
main.py: /send-phone-otp endpoint
   │
   ├─ FastAPI parses request body into PhoneRequest(phone="+1234567890")
   ├─ Validates phone format: phone.replace("+","").replace(" ","").isdigit()
   │   → if not all digits, raises HTTPException(400, "Invalid phone number format")
   ├─ Calls: phone_sender.send_otp(request.phone)
   │       │
   │       ▼
   │     phone_otp.py: PhoneOTPSender.send_otp("+1234567890")
   │       │
   │       ├─ Cleans numbers (strips spaces and dashes)
   │       ├─ Checks if cleaned_to == cleaned_from (same number check)
   │       │   → if same, returns {"success": False, "message": "Twilio Error: 'To' and 'From' number cannot be the same..."}
   │       ├─ otp = generate_otp()          → e.g., "739201"
   │       ├─ store_otp("+1234567890", "739201")
   │       │       │
   │       │       ▼
   │       │     utils.py: otp_storage["+1234567890"] = {
   │       │         "otp": "739201",
   │       │         "expiry": time.time() + 300,
   │       │         "attempts": 0,
   │       │         "verified": False
   │       │     }
   │       │
   │       ├─ If Twilio credentials present:
   │       │   ├─ Creates twilio.rest.Client(account_sid, auth_token)
   │       │   ├─ Calls client.messages.create(
   │       │   │       body="Your OTP code is: 739201. Valid for 5 minutes.",
   │       │   │       from_="+9779802881981",
   │       │   │       to="+1234567890"
   │       │   │   )
   │       │   └─ Returns {"success": True, "message": "OTP sent successfully via SMS", "phone": "+1234567890", "message_id": "<twilio_sid>"}
   │       └─ If Twilio credentials missing (demo mode):
   │           ├─ Prints "Development mode - OTP for +1234567890: 739201" to console
   │           └─ Returns {"success": True, "message": "OTP generated (demo mode - check console)", "phone": "+1234567890", "otp": "739201"}
   │
   ▼
main.py: receives result from phone_sender.send_otp()
   │
   ├─ If result["success"] is False → raises HTTPException(400, detail=result["message"])
   └─ If result["success"] is True → returns result as JSON response
   │
   ▼
script.js: receives JSON response
   │
   ├─ If result.success is True:
   │   ├─ Shows green success message: "✅ OTP sent successfully via SMS. Check your phone for the SMS."
   │   ├─ Auto-fills identifierInput.value with the phone number
   │   └─ Adds "pulse" CSS class to otpInput
   └─ If result.success is False:
       └─ Shows red error message with the failure reason
   │
   ▼
script.js: finally block
   ├─ Resets button text to "Send SMS OTP" (with SMS icon)
   └─ Re-enables the button
```

---

### Workflow 3: Verify OTP

This is the sequence of events when a user submits an OTP for verification.

```
USER ACTION                          SYSTEM RESPONSE
============                         ===============
1. User types the identifier (email or phone) into #identifier field
2. User types the 6-digit OTP into #otp field
3. User clicks "Verify OTP" button
   │
   ▼
script.js: verifyOtpBtn click handler
   │
   ├─ Reads identifierInput.value.trim()
   ├─ Reads otpInput.value.trim()
   ├─ Checks if identifier is empty → shows error, stops
   ├─ Checks if otp is empty or not exactly 6 digits → shows error, stops
   ├─ Changes button to "Verifying..." spinner, disables it
   │
   ▼
script.js: makeRequest() called
   │
   ├─ HTTP POST to http://localhost:8000/verify-otp
   ├─ Request body: { "identifier": "user@example.com", "otp": "482917" }
   │
   ▼
main.py: /verify-otp endpoint
   │
   ├─ FastAPI parses request body into VerifyOTPRequest(identifier="user@example.com", otp="482917")
   ├─ Calls: verify_otp("user@example.com", "482917")
   │       │
   │       ▼
   │     utils.py: verify_otp("user@example.com", "482917")
   │       │
   │       ├─ Calls get_otp("user@example.com")
   │       │   ├─ Looks up otp_storage["user@example.com"]
   │       │   ├─ Checks if entry exists → if not, returns None
   │       │   ├─ Checks if time.time() > otp_data['expiry'] → if expired, deletes entry and returns None
   │       │   └─ If valid, returns the otp_data dict
   │       │
   │       ├─ If get_otp() returned None → return False (no OTP found or expired)
   │       │
   │       ├─ If otp_data['attempts'] >= 3 → delete entry, return False (max attempts exceeded)
   │       │
   │       ├─ If otp_data['otp'] == "482917" (match):
   │       │   ├─ Sets otp_data['verified'] = True
   │       │   └─ Returns True
   │       │
   │       └─ If OTP does not match:
   │           ├─ Increments otp_data['attempts'] by 1
   │           └─ Returns False
   │
   ▼
main.py: receives boolean from verify_otp()
   │
   ├─ If is_valid is True:
   │   ├─ Calls clear_otp("user@example.com") → deletes entry from otp_storage
   │   └─ Returns JSON: {"success": True, "message": "OTP verified successfully", "identifier": "user@example.com"}
   │
   └─ If is_valid is False:
       └─ Returns JSON: {"success": False, "message": "Invalid OTP or OTP expired", "identifier": "user@example.com"}
   │
   ▼
script.js: receives JSON response
   │
   ├─ If result.success is True:
   │   ├─ Shows green success message: "✅ OTP verified successfully"
   │   ├─ Clears the otpInput field (otpInput.value = '')
   │   └─ Triggers confettiEffect() — creates 50 animated colored circles that fall down the screen
   └─ If result.success is False:
       └─ Shows red error message: "❌ Invalid OTP or OTP expired"
   │
   ▼
script.js: finally block
   ├─ Resets button text to "Verify OTP" (with check icon)
   └─ Re-enables the button
```

---

## Backend API Endpoints

| Method | Endpoint | Purpose | Request Body | Response |
|--------|----------|---------|-------------|----------|
| `GET` | `/` | Root endpoint — confirms the API is running | None | `{"message": "OTP Verification System API"}` |
| `POST` | `/send-email-otp` | Send a 6-digit OTP to an email address | `{"email": "user@example.com"}` | `{"success": true, "message": "...", "email": "..."}` or error |
| `POST` | `/send-phone-otp` | Send a 6-digit OTP via SMS to a phone number | `{"phone": "+1234567890"}` | `{"success": true, "message": "...", "phone": "...", "message_id": "..."}` or error |
| `POST` | `/verify-otp` | Verify the OTP entered by the user | `{"identifier": "user@example.com", "otp": "482917"}` | `{"success": true/false, "message": "...", "identifier": "..."}` |
| `GET` | `/health` | Health check — confirms the backend is running | None | `{"status": "healthy", "service": "OTP API"}` |

---

## Data Flow Diagrams

### Email OTP Data Flow

```
User enters email → clicks "Send Email OTP"
        │
        ▼
script.js: sendEmailBtn.click()
        │
        ├─ Validates email (empty check + regex)
        │
        ▼
fetch POST → http://localhost:8000/send-email-otp
        │  Body: { "email": "user@example.com" }
        ▼
main.py: /send-email-otp endpoint
        │
        ├─ FastAPI validates body → EmailRequest(email="user@example.com")
        │
        ▼
email_otp.py: EmailOTPSender.send_otp("user@example.com")
        │
        ├─ utils.generate_otp() → "482917"
        ├─ utils.store_otp("user@example.com", "482917")
        │       → otp_storage["user@example.com"] = {otp, expiry, attempts:0, verified:False}
        │
        ├─ [If SMTP configured]
        │   aiosmtplib.SMTP → login → send_message → returns success
        │
        └─ [If SMTP not configured]
            Prints OTP to console → returns success (demo mode)
        │
        ▼
main.py: returns JSON response to frontend
        │
        ▼
script.js: displays success message, auto-fills identifier field, pulses OTP input
```

### OTP Verification Data Flow

```
User enters identifier + OTP → clicks "Verify OTP"
        │
        ▼
script.js: verifyOtpBtn.click()
        │
        ├─ Validates identifier (not empty) and OTP (exactly 6 digits)
        │
        ▼
fetch POST → http://localhost:8000/verify-otp
        │  Body: { "identifier": "user@example.com", "otp": "482917" }
        ▼
main.py: /verify-otp endpoint
        │
        ▼
utils.verify_otp("user@example.com", "482917")
        │
        ├─ utils.get_otp("user@example.com")
        │   ├─ Not in storage → return None → verify_otp returns False
        │   ├─ Expired → delete from storage → return None → verify_otp returns False
        │   └─ Valid → return otp_data dict
        │
        ├─ If otp_data is None → return False
        │
        ├─ If attempts >= 3 → delete from storage → return False
        │
        ├─ If otp matches → set verified=True → return True
        │
        └─ If otp doesn't match → attempts += 1 → return False
        │
        ▼
main.py:
  ├─ If True → clear_otp(identifier) → return success JSON
  └─ If False → return failure JSON
        │
        ▼
script.js: displays result, triggers confetti on success
```

---

## Key Functions Reference

### Backend Functions

| Function | File | Called By | Purpose |
|----------|------|-----------|---------|
| `generate_otp(length=6)` | `utils.py:8` | `email_otp.py`, `phone_otp.py` | Generates a random numeric OTP string |
| `store_otp(identifier, otp, expiry_minutes=5)` | `utils.py:13` | `email_otp.py`, `phone_otp.py` | Saves OTP to in-memory dict with expiry timestamp |
| `get_otp(identifier)` | `utils.py:23` | `utils.py:verify_otp` (internal) | Retrieves OTP data if not expired; auto-deletes expired entries |
| `verify_otp(identifier, user_otp, max_attempts=3)` | `utils.py:36` | `main.py:69` | Checks if the user-provided OTP matches the stored one; enforces attempt limits |
| `clear_otp(identifier)` | `utils.py:54` | `main.py:73` | Deletes the OTP entry after successful verification |
| `EmailOTPSender.send_otp(email)` | `email_otp.py:18` | `main.py:45` | Generates, stores, and emails an OTP via Gmail SMTP |
| `PhoneOTPSender.send_otp(phone_number)` | `phone_otp.py:16` | `main.py:59` | Generates, stores, and sends an OTP via Twilio SMS |

### Frontend Functions

| Function | File | Called By | Purpose |
|----------|------|-----------|---------|
| `showMessage(element, message, type)` | `script.js:17` | All event handlers | Displays a styled message (success/error/info) in a result div |
| `makeRequest(url, method, data)` | `script.js:31` | All three OTP handlers | Sends an HTTP request to the backend and returns parsed JSON |
| `confettiEffect()` | `script.js:207` | `verifyOtpBtn` handler (on success) | Creates 50 animated confetti particles for visual celebration |
| `checkBackendHealth()` | `script.js:239` | `DOMContentLoaded` | Pings `/health` endpoint to verify backend connectivity |

---

## Configuration & Environment

The `.env` file in the project root stores all secrets and configuration. It is loaded by `python-dotenv` at the module level in both `email_otp.py` and `phone_otp.py`.

### Required Variables

| Variable | Used By | Description |
|----------|---------|-------------|
| `SMTP_HOST` | `email_otp.py` | SMTP server hostname (default: `smtp.gmail.com`) |
| `SMTP_PORT` | `email_otp.py` | SMTP server port (default: `587`) |
| `SMTP_USERNAME` | `email_otp.py` | Gmail address used to send OTPs |
| `SMTP_PASSWORD` | `email_otp.py` | Gmail App Password (not your regular password) |
| `FROM_EMAIL` | `email_otp.py` | The "From" address in sent emails (default: `noreply@example.com`) |
| `TWILIO_ACCOUNT_SID` | `phone_otp.py` | Twilio account identifier |
| `TWILIO_AUTH_TOKEN` | `phone_otp.py` | Twilio authentication token |
| `TWILIO_PHONE_NUMBER` | `phone_otp.py` | The Twilio phone number used as the sender |

### Important Notes

- **Gmail**: You must enable 2-Step Verification on the Gmail account and generate an **App Password** (not your regular password). Use the App Password in `SMTP_PASSWORD`.
- **Twilio**: The `TWILIO_PHONE_NUMBER` must be a number purchased from Twilio (not a trial number) to send SMS to countries like Nepal. Trial accounts can only send to verified Caller IDs.
- **Cost**: Sending SMS to Nepal costs approximately $0.30 per message on Twilio. Email OTPs via Gmail are free.
- **Security**: The `.env` file is listed in `.gitignore` and should never be committed to version control.

---

## Error Handling

### Backend Error Handling

| Scenario | Where Handled | Response |
|----------|--------------|----------|
| Invalid email format | `main.py:43` — Pydantic `EmailStr` validation | HTTP 422 (FastAPI default validation error) |
| Invalid phone format (non-digits) | `main.py:56` — manual `.isdigit()` check | HTTP 400, `"Invalid phone number format"` |
| Email send failure | `email_otp.py:77` — generic `except Exception` | HTTP 400, `"Failed to send OTP: <error>"` |
| SMS send failure (Twilio error) | `phone_otp.py:62` — `TwilioRestException` with code-specific messages | HTTP 400, `"Twilio Error: <specific message>"` |
| SMS send failure (generic) | `phone_otp.py:79` — generic `except Exception` | HTTP 400, `"Failed to send OTP: <error>"` |
| OTP expired or not found | `utils.py:40` — `get_otp()` returns `None` | `{"success": false, "message": "Invalid OTP or OTP expired"}` |
| Max attempts exceeded (3) | `utils.py:43` — `attempts >= max_attempts` | `{"success": false, "message": "Invalid OTP or OTP expired"}` (OTP is also deleted) |
| Wrong OTP entered | `utils.py:51` — OTP mismatch, attempts incremented | `{"success": false, "message": "Invalid OTP or OTP expired"}` |

### Frontend Error Handling

| Scenario | Where Handled | User Feedback |
|----------|--------------|---------------|
| Empty email field | `script.js:62` | Red message: "Please enter an email address" |
| Invalid email format | `script.js:70` | Red message: "Please enter a valid email address" |
| Empty phone field | `script.js:105` | Red message: "Please enter a phone number" |
| Empty identifier field | `script.js:142` | Red message: "Please enter email or phone number" |
| OTP not 6 digits | `script.js:148` | Red message: "Please enter a valid 6-digit OTP" |
| Backend unreachable | `script.js:239` | Red message: "Backend server is not reachable" |
| API returns error | `script.js:48` (makeRequest catch) | Red message with the error detail from the backend |

---

## Running the Application

### Prerequisites
- Python 3.10+ (tested on Python 3.13)
- Gmail account with 2-Step Verification enabled (for email OTP)
- Twilio account with a purchased phone number (for SMS OTP)

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Configure Environment
Create a `.env` file in the project root with your SMTP and Twilio credentials (see [Configuration & Environment](#configuration--environment)).

### Step 3: Start the Backend
```bash
python main.py
```
The FastAPI server starts on `http://localhost:8000`. The auto-reload feature (`reload=True`) restarts the server when any source file changes.

### Step 4: Start the Frontend
In a separate terminal:
```bash
python -m http.server 3000
```
Open `http://localhost:3000` in your browser.

### Step 5: Test
1. Enter an email address and click "Send Email OTP" — check your inbox for the code.
2. Enter a phone number and click "Send SMS OTP" — check your phone for the SMS.
3. Enter the received 6-digit code in the verification section and click "Verify OTP".

---

## Known Issues

- **Twilio SMS to Nepal**: Carrier-level blocking can occur when sending from a US Twilio number to Nepali carriers (NTC, Ncell). Using a purchased (not trial) Twilio number and enabling Nepal in SMS Geo-Permissions helps, but delivery is not guaranteed.
- **In-memory OTP storage**: The `otp_storage` dict in `utils.py` is volatile. Server restarts delete all pending OTPs. For production, replace with Redis or a database.
- **Number OTP verification issue**: There is a known unresolved issue with phone number OTP verification (see `issues_to_solve.md`).
