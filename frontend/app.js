/* =============================================================================
   SecureAuth - Main Application JavaScript
   Handles authentication forms, API calls, and UI interactions
   ============================================================================= */

// API Configuration
const API_BASE_URL = 'http://localhost:8000/api/v1';

// DOM Elements
const tabButtons = document.querySelectorAll('.tab-btn');
const loginForm = document.getElementById('login-form');
const registerForm = document.getElementById('register-form');
const toastContainer = document.getElementById('toast-container');

// ============================================================================
// Tab Switching
// ============================================================================

tabButtons.forEach(btn => {
    btn.addEventListener('click', () => {
        const tab = btn.dataset.tab;
        
        // Update active states
        tabButtons.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        
        // Switch forms
        if (tab === 'login') {
            loginForm.classList.add('active');
            registerForm.classList.remove('active');
        } else {
            loginForm.classList.remove('active');
            registerForm.classList.add('active');
        }
    });
});

// ============================================================================
// Password Visibility Toggle
// ============================================================================

document.querySelectorAll('.password-toggle').forEach(toggle => {
    toggle.addEventListener('click', () => {
        const input = toggle.parentElement.querySelector('input');
        const eyeOpen = toggle.querySelector('.eye-open');
        const eyeClosed = toggle.querySelector('.eye-closed');
        
        if (input.type === 'password') {
            input.type = 'text';
            eyeOpen.classList.add('hidden');
            eyeClosed.classList.remove('hidden');
        } else {
            input.type = 'password';
            eyeOpen.classList.remove('hidden');
            eyeClosed.classList.add('hidden');
        }
    });
});

// ============================================================================
// Password Strength Checker
// ============================================================================

const registerPassword = document.getElementById('register-password');
const strengthFill = document.getElementById('strength-fill');
const strengthText = document.getElementById('strength-text');

if (registerPassword) {
    registerPassword.addEventListener('input', (e) => {
        const password = e.target.value;
        const strength = checkPasswordStrength(password);
        
        strengthFill.className = 'strength-fill';
        
        if (password.length === 0) {
            strengthFill.style.width = '0%';
            strengthText.textContent = 'Password strength';
        } else if (strength < 2) {
            strengthFill.classList.add('weak');
            strengthText.textContent = 'Weak password';
        } else if (strength < 4) {
            strengthFill.classList.add('medium');
            strengthText.textContent = 'Medium strength';
        } else {
            strengthFill.classList.add('strong');
            strengthText.textContent = 'Strong password';
        }
    });
}

function checkPasswordStrength(password) {
    let strength = 0;
    
    if (password.length >= 8) strength++;
    if (password.length >= 12) strength++;
    if (/[a-z]/.test(password) && /[A-Z]/.test(password)) strength++;
    if (/\d/.test(password)) strength++;
    if (/[^a-zA-Z\d]/.test(password)) strength++;
    
    return strength;
}

// ============================================================================
// Toast Notifications
// ============================================================================

function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    const iconSvg = type === 'success' 
        ? `<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>`
        : `<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="15" x2="9" y1="9" y2="15"></line><line x1="9" x2="15" y1="9" y2="15"></line></svg>`;
    
    toast.innerHTML = `
        <span class="toast-icon ${type}">${iconSvg}</span>
        <span class="toast-message">${message}</span>
        <button class="toast-close">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" x2="6" y1="6" y2="18"></line><line x1="6" x2="18" y1="6" y2="18"></line></svg>
        </button>
    `;
    
    toastContainer.appendChild(toast);
    
    // Close button handler
    toast.querySelector('.toast-close').addEventListener('click', () => {
        removeToast(toast);
    });
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        removeToast(toast);
    }, 5000);
}

function removeToast(toast) {
    toast.classList.add('removing');
    setTimeout(() => {
        toast.remove();
    }, 300);
}

// ============================================================================
// Button Loading State
// ============================================================================

function setButtonLoading(button, loading) {
    const btnText = button.querySelector('.btn-text');
    const btnLoader = button.querySelector('.btn-loader');
    
    if (loading) {
        btnText.classList.add('hidden');
        btnLoader.classList.remove('hidden');
        button.disabled = true;
    } else {
        btnText.classList.remove('hidden');
        btnLoader.classList.add('hidden');
        button.disabled = false;
    }
}

// ============================================================================
// Token Management
// ============================================================================

function saveToken(token) {
    localStorage.setItem('access_token', token);
}

function getToken() {
    return localStorage.getItem('access_token');
}

function removeToken() {
    localStorage.removeItem('access_token');
}

function isAuthenticated() {
    return !!getToken();
}

// ============================================================================
// API Calls
// ============================================================================

async function apiRequest(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
    
    const defaultHeaders = {
        'Content-Type': 'application/json',
    };
    
    // Add auth header if token exists
    const token = getToken();
    if (token) {
        defaultHeaders['Authorization'] = `Bearer ${token}`;
    }
    
    const config = {
        ...options,
        headers: {
            ...defaultHeaders,
            ...options.headers,
        },
    };
    
    const response = await fetch(url, config);
    
    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'An error occurred');
    }
    
    return response.json();
}

// ============================================================================
// Login Handler
// ============================================================================

if (loginForm) {
    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const submitBtn = loginForm.querySelector('button[type="submit"]');
        const username = document.getElementById('login-username').value;
        const password = document.getElementById('login-password').value;
        
        setButtonLoading(submitBtn, true);
        
        try {
            // OAuth2 password flow requires form data
            const formData = new URLSearchParams();
            formData.append('username', username);
            formData.append('password', password);
            
            const response = await fetch(`${API_BASE_URL}/auth/token`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: formData,
            });
            
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Login failed');
            }
            
            const data = await response.json();
            saveToken(data.access_token);
            
            showToast('Login successful! Redirecting...', 'success');
            
            // Redirect to dashboard
            setTimeout(() => {
                window.location.href = '/dashboard';
            }, 1000);
            
        } catch (error) {
            showToast(error.message, 'error');
        } finally {
            setButtonLoading(submitBtn, false);
        }
    });
}

// ============================================================================
// Register Handler
// ============================================================================

if (registerForm) {
    registerForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const submitBtn = registerForm.querySelector('button[type="submit"]');
        const username = document.getElementById('register-username').value;
        const email = document.getElementById('register-email').value;
        const fullName = document.getElementById('register-fullname').value;
        const password = document.getElementById('register-password').value;
        
        setButtonLoading(submitBtn, true);
        
        try {
            await apiRequest('/users/register', {
                method: 'POST',
                body: JSON.stringify({
                    username,
                    email,
                    full_name: fullName,
                    password,
                }),
            });
            
            showToast('Account created successfully! Please sign in.', 'success');
            
            // Switch to login tab
            setTimeout(() => {
                document.querySelector('[data-tab="login"]').click();
                registerForm.reset();
                strengthFill.className = 'strength-fill';
                strengthFill.style.width = '0%';
                strengthText.textContent = 'Password strength';
            }, 1000);
            
        } catch (error) {
            showToast(error.message, 'error');
        } finally {
            setButtonLoading(submitBtn, false);
        }
    });
}

// ============================================================================
// Auth Check on Page Load
// ============================================================================

// Redirect to dashboard if already authenticated (on login page)
const currentPath = window.location.pathname;
if (currentPath === '/' || currentPath.endsWith('index.html') || currentPath === '') {
    if (isAuthenticated()) {
        window.location.href = '/dashboard';
    }
}
