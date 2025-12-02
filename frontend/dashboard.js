/* =============================================================================
   SecureAuth - Dashboard JavaScript
   Handles dashboard functionality, user data display, and logout
   ============================================================================= */

// ============================================================================
// Auth Check
// ============================================================================

if (!isAuthenticated()) {
    window.location.href = '/';
}

// ============================================================================
// DOM Elements
// ============================================================================

const userMenuBtn = document.getElementById('user-menu-btn');
const userDropdown = document.getElementById('user-dropdown');
const logoutBtn = document.getElementById('logout-btn');
const copyTokenBtn = document.getElementById('copy-token-btn');

// ============================================================================
// User Menu Toggle
// ============================================================================

if (userMenuBtn) {
    userMenuBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        userDropdown.classList.toggle('open');
    });
    
    // Close dropdown when clicking outside
    document.addEventListener('click', () => {
        userDropdown.classList.remove('open');
    });
    
    userDropdown.addEventListener('click', (e) => {
        e.stopPropagation();
    });
}

// ============================================================================
// Logout Handler
// ============================================================================

if (logoutBtn) {
    logoutBtn.addEventListener('click', () => {
        removeToken();
        showToast('Logged out successfully', 'success');
        setTimeout(() => {
            window.location.href = '/';
        }, 500);
    });
}

// ============================================================================
// Copy Token Handler
// ============================================================================

if (copyTokenBtn) {
    copyTokenBtn.addEventListener('click', async () => {
        const token = getToken();
        if (token) {
            try {
                await navigator.clipboard.writeText(token);
                showToast('Token copied to clipboard', 'success');
            } catch (err) {
                showToast('Failed to copy token', 'error');
            }
        }
    });
}

// ============================================================================
// Load User Data
// ============================================================================

async function loadUserData() {
    try {
        const user = await apiRequest('/users/me');
        
        // Update UI elements
        updateElement('user-name', user.username);
        updateElement('user-avatar', getInitials(user.full_name || user.username));
        updateElement('welcome-name', user.full_name || user.username);
        updateElement('dropdown-email', user.email);
        
        // Profile info
        updateElement('profile-username', user.username);
        updateElement('profile-email', user.email);
        updateElement('profile-fullname', user.full_name || '-');
        updateElement('profile-id', `#${user.id}`);
        
        // Stats
        updateElement('account-status', user.is_active ? 'Active' : 'Inactive');
        updateElement('user-role', user.roles && user.roles.length > 0 ? capitalizeFirst(user.roles[0]) : 'User');
        updateElement('member-since', formatDate(user.created_at));
        
        // Token display
        const token = getToken();
        updateElement('token-display', token ? `${token.substring(0, 50)}...` : 'No token');
        
    } catch (error) {
        console.error('Failed to load user data:', error);
        
        // If unauthorized, redirect to login
        if (error.message.includes('validate credentials') || error.message.includes('401')) {
            removeToken();
            window.location.href = '/';
        } else {
            showToast('Failed to load user data', 'error');
        }
    }
}

// ============================================================================
// Helper Functions
// ============================================================================

function updateElement(id, value) {
    const element = document.getElementById(id);
    if (element) {
        element.textContent = value;
    }
}

function getInitials(name) {
    if (!name) return 'U';
    const parts = name.split(' ');
    if (parts.length >= 2) {
        return (parts[0][0] + parts[1][0]).toUpperCase();
    }
    return name.substring(0, 2).toUpperCase();
}

function capitalizeFirst(str) {
    if (!str) return '';
    return str.charAt(0).toUpperCase() + str.slice(1);
}

function formatDate(dateString) {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric'
    });
}

// ============================================================================
// Initialize Dashboard
// ============================================================================

loadUserData();
