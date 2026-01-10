// API Configuration
const API_BASE_URL = 'http://localhost:8000';

// DOM Elements
const emailInput = document.getElementById('email');
const phoneInput = document.getElementById('phone');
const identifierInput = document.getElementById('identifier');
const otpInput = document.getElementById('otp');
const sendEmailBtn = document.getElementById('sendEmailOtp');
const sendPhoneBtn = document.getElementById('sendPhoneOtp');
const verifyOtpBtn = document.getElementById('verifyOtp');
const emailResult = document.getElementById('emailResult');
const phoneResult = document.getElementById('phoneResult');
const verifyResult = document.getElementById('verifyResult');

// Helper function to display messages
function showMessage(element, message, type = 'info') {
    element.textContent = message;
    element.className = `result ${type}`;
    element.style.display = 'block';
    
    // Auto-hide success messages after 5 seconds
    if (type === 'success') {
        setTimeout(() => {
            element.style.display = 'none';
        }, 5000);
    }
}

// Helper function for API calls
async function makeRequest(url, method = 'POST', data = null) {
    try {
        const options = {
            method,
            headers: {
                'Content-Type': 'application/json',
            },
        };
        
        if (data) {
            options.body = JSON.stringify(data);
        }
        
        const response = await fetch(url, options);
        const result = await response.json();
        
        if (!response.ok) {
            throw new Error(result.detail || result.message || 'Request failed');
        }
        
        return result;
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

// Send Email OTP
sendEmailBtn.addEventListener('click', async () => {
    const email = emailInput.value.trim();
    
    if (!email) {
        showMessage(emailResult, 'Please enter an email address', 'error');
        emailInput.focus();
        return;
    }
    
    // Basic email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
        showMessage(emailResult, 'Please enter a valid email address', 'error');
        return;
    }
    
    // Update button state
    sendEmailBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Sending...';
    sendEmailBtn.disabled = true;
    
    try {
        const result = await makeRequest(`${API_BASE_URL}/send-email-otp`, 'POST', { email });
        
        if (result.success) {
            showMessage(emailResult, `✅ ${result.message}. Check your email for the OTP.`, 'success');
            // Auto-fill identifier field
            identifierInput.value = email;
            // Add pulse animation
            otpInput.classList.add('pulse');
            setTimeout(() => otpInput.classList.remove('pulse'), 500);
        } else {
            showMessage(emailResult, `❌ ${result.message}`, 'error');
        }
    } catch (error) {
        showMessage(emailResult, `❌ Failed to send OTP: ${error.message}`, 'error');
    } finally {
        // Reset button state
        sendEmailBtn.innerHTML = '<i class="fas fa-paper-plane"></i> Send Email OTP';
        sendEmailBtn.disabled = false;
    }
});

// Send Phone OTP
sendPhoneBtn.addEventListener('click', async () => {
    const phone = phoneInput.value.trim();
    
    if (!phone) {
        showMessage(phoneResult, 'Please enter a phone number', 'error');
        phoneInput.focus();
        return;
    }
    
    // Update button state
    sendPhoneBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Sending...';
    sendPhoneBtn.disabled = true;
    
    try {
        const result = await makeRequest(`${API_BASE_URL}/send-phone-otp`, 'POST', { phone });
        
        if (result.success) {
            showMessage(phoneResult, `✅ ${result.message}. Check your phone for the SMS.`, 'success');
            // Auto-fill identifier field
            identifierInput.value = phone;
            // Add pulse animation
            otpInput.classList.add('pulse');
            setTimeout(() => otpInput.classList.remove('pulse'), 500);
        } else {
            showMessage(phoneResult, `❌ ${result.message}`, 'error');
        }
    } catch (error) {
        showMessage(phoneResult, `❌ Failed to send OTP: ${error.message}`, 'error');
    } finally {
        // Reset button state
        sendPhoneBtn.innerHTML = '<i class="fas fa-sms"></i> Send SMS OTP';
        sendPhoneBtn.disabled = false;
    }
});

// Verify OTP
verifyOtpBtn.addEventListener('click', async () => {
    const identifier = identifierInput.value.trim();
    const otp = otpInput.value.trim();
    
    if (!identifier) {
        showMessage(verifyResult, 'Please enter email or phone number', 'error');
        identifierInput.focus();
        return;
    }
    
    if (!otp || otp.length !== 6) {
        showMessage(verifyResult, 'Please enter a valid 6-digit OTP', 'error');
        otpInput.focus();
        return;
    }
    
    // Update button state
    verifyOtpBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Verifying...';
    verifyOtpBtn.disabled = true;
    
    try {
        const result = await makeRequest(`${API_BASE_URL}/verify-otp`, 'POST', {
            identifier,
            otp
        });
        
        if (result.success) {
            showMessage(verifyResult, `✅ ${result.message}`, 'success');
            // Clear OTP field on success
            otpInput.value = '';
            
            // Show celebration effect
            confettiEffect();
        } else {
            showMessage(verifyResult, `❌ ${result.message}`, 'error');
        }
    } catch (error) {
        showMessage(verifyResult, `❌ Verification failed: ${error.message}`, 'error');
    } finally {
        // Reset button state
        verifyOtpBtn.innerHTML = '<i class="fas fa-check"></i> Verify OTP';
        verifyOtpBtn.disabled = false;
    }
});

// Enter key support
[emailInput, phoneInput, identifierInput, otpInput].forEach(input => {
    input.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            if (input === emailInput) sendEmailBtn.click();
            if (input === phoneInput) sendPhoneBtn.click();
            if (input === identifierInput || input === otpInput) verifyOtpBtn.click();
        }
    });
});

// Input validation
otpInput.addEventListener('input', function() {
    // Only allow numbers
    this.value = this.value.replace(/[^0-9]/g, '');
    
    // Limit to 6 digits
    if (this.value.length > 6) {
        this.value = this.value.slice(0, 6);
    }
});

// Simple confetti effect for successful verification
function confettiEffect() {
    const colors = ['#3498db', '#2ecc71', '#9b59b6', '#e74c3c', '#f1c40f'];
    const container = document.querySelector('.container');
    
    for (let i = 0; i < 50; i++) {
        const confetti = document.createElement('div');
        confetti.style.position = 'absolute';
        confetti.style.width = '10px';
        confetti.style.height = '10px';
        confetti.style.backgroundColor = colors[Math.floor(Math.random() * colors.length)];
        confetti.style.borderRadius = '50%';
        confetti.style.left = Math.random() * 100 + 'vw';
        confetti.style.top = '-20px';
        confetti.style.opacity = '0.8';
        confetti.style.zIndex = '9999';
        
        document.body.appendChild(confetti);
        
        // Animation
        const animation = confetti.animate([
            { transform: 'translateY(0) rotate(0deg)', opacity: 1 },
            { transform: `translateY(${window.innerHeight}px) rotate(${Math.random() * 360}deg)`, opacity: 0 }
        ], {
            duration: 2000 + Math.random() * 2000,
            easing: 'cubic-bezier(0.215, 0.61, 0.355, 1)'
        });
        
        animation.onfinish = () => confetti.remove();
    }
}

// Check backend health on load
async function checkBackendHealth() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        if (response.ok) {
            console.log('✅ Backend is connected and healthy');
        }
    } catch (error) {
        console.warn('⚠️ Backend is not reachable. Please make sure the server is running on port 8000');
        showMessage(emailResult, '⚠️ Backend server is not reachable. Please start the server first.', 'error');
        showMessage(phoneResult, '⚠️ Backend server is not reachable. Please start the server first.', 'error');
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    checkBackendHealth();
    
    // Add demo values for testing
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
        emailInput.value = 'test@example.com';
        phoneInput.value = '+1234567890';
        console.log('Demo values loaded for testing');
    }
});