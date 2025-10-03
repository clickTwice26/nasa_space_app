// NASA Space App JavaScript with Beautiful Loading Animations
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 NASA Space App initialized');
    
    // Initialize loading animations
    initializeLoadingAnimations();
    
    // Check API health on page load
    checkAPIHealth();
});

// Loading Animation System
function initializeLoadingAnimations() {
    // Create loading overlay template
    const style = document.createElement('style');
    style.textContent = `
        .beautiful-loading {
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(15px);
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            z-index: 1000;
            opacity: 0;
            visibility: hidden;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            border-radius: inherit;
        }
        
        .beautiful-loading.show {
            opacity: 1;
            visibility: visible;
        }
        
        .loading-animation {
            position: relative;
            width: 60px;
            height: 60px;
            margin-bottom: 1rem;
        }
        
        .loading-rings {
            position: absolute;
            width: 100%;
            height: 100%;
        }
        
        .loading-ring {
            position: absolute;
            border: 3px solid transparent;
            border-radius: 50%;
            animation: rotateRing 2s linear infinite;
        }
        
        .loading-ring:nth-child(1) {
            width: 60px;
            height: 60px;
            border-top-color: #3b82f6;
            animation-duration: 1.5s;
        }
        
        .loading-ring:nth-child(2) {
            width: 46px;
            height: 46px;
            top: 7px;
            left: 7px;
            border-right-color: #10b981;
            animation-duration: 2s;
            animation-direction: reverse;
        }
        
        .loading-ring:nth-child(3) {
            width: 32px;
            height: 32px;
            top: 14px;
            left: 14px;
            border-bottom-color: #f59e0b;
            animation-duration: 1s;
        }
        
        @keyframes rotateRing {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .loading-text {
            color: #6b7280;
            font-size: 0.875rem;
            font-weight: 500;
            text-align: center;
            animation: pulse 2s ease-in-out infinite;
        }
        
        .loading-dots::after {
            content: '';
            animation: dots 1.5s steps(3, end) infinite;
        }
        
        @keyframes dots {
            0%, 20% { content: ''; }
            40% { content: '.'; }
            60% { content: '..'; }
            80%, 100% { content: '...'; }
        }
    `;
    document.head.appendChild(style);
}

// Show beautiful loading animation
function showLoading(element, message = 'Loading') {
    if (!element) return;
    
    // Remove existing loading overlay
    const existingOverlay = element.querySelector('.beautiful-loading');
    if (existingOverlay) {
        existingOverlay.remove();
    }
    
    // Create new loading overlay
    const overlay = document.createElement('div');
    overlay.className = 'beautiful-loading';
    overlay.innerHTML = `
        <div class="loading-animation">
            <div class="loading-rings">
                <div class="loading-ring"></div>
                <div class="loading-ring"></div>
                <div class="loading-ring"></div>
            </div>
        </div>
        <div class="loading-text loading-dots">${message}</div>
    `;
    
    // Add overlay to element
    element.style.position = 'relative';
    element.appendChild(overlay);
    
    // Trigger animation
    setTimeout(() => {
        overlay.classList.add('show');
    }, 10);
    
    return overlay;
}

// Hide loading animation
function hideLoading(element) {
    if (!element) return;
    
    const overlay = element.querySelector('.beautiful-loading');
    if (overlay) {
        overlay.classList.remove('show');
        setTimeout(() => {
            overlay.remove();
        }, 300);
    }
}

// Enhanced API call with loading animation
async function apiCallWithLoading(element, url, options = {}, loadingMessage = 'Loading') {
    const overlay = showLoading(element, loadingMessage);
    
    try {
        // Minimum loading time for better UX
        const [response] = await Promise.all([
            fetch(url, {
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                },
                ...options
            }),
            new Promise(resolve => setTimeout(resolve, 1000)) // 1 second minimum
        ]);
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.message || `HTTP error! status: ${response.status}`);
        }
        
        return data;
    } catch (error) {
        console.error('API call failed:', error);
        throw error;
    } finally {
        hideLoading(element);
    }
}

// Button loading state
function setButtonLoading(button, loading = true) {
    if (!button) return;
    
    if (loading) {
        button.disabled = true;
        button.classList.add('loading');
        button.dataset.originalText = button.innerHTML;
        
        const icon = button.querySelector('i');
        if (icon) {
            icon.style.animation = 'spin 1s linear infinite';
        }
    } else {
        button.disabled = false;
        button.classList.remove('loading');
        
        if (button.dataset.originalText) {
            button.innerHTML = button.dataset.originalText;
            delete button.dataset.originalText;
        }
        
        const icon = button.querySelector('i');
        if (icon) {
            icon.style.animation = '';
        }
    }
}


async function checkAPIHealth() {
    const statusElement = document.getElementById('api-status');
    
    try {
        console.log('Checking API health...');
        
        if (statusElement) {
            showLoading(statusElement, 'Checking API status');
        }
        
        const data = await apiCallWithLoading(
            statusElement, 
            '/api/health', 
            {}, 
            'Checking API status'
        );
        
        console.log('API Health:', data);
        
        // Update status display if element exists
        if (statusElement) {
            statusElement.innerHTML = `
                <div class="status-success">
                    <strong>✅ API Status:</strong> ${data.status} - ${data.message}
                    <br><small>Version: ${data.version}</small>
                </div>
            `;
            statusElement.className = 'status-display status-success';
        }
        
        return data;
    } catch (error) {
        console.error('API Health check failed:', error);
        
        if (statusElement) {
            statusElement.innerHTML = `
                <div class="status-error">
                    <strong>❌ API Status:</strong> Connection failed
                    <br><small>Error: ${error.message}</small>
                </div>
            `;
            statusElement.className = 'status-display status-error';
        }
        
        return null;
    }
}

// Enhanced Utility Functions
async function fetchData(url, options = {}) {
    try {
        const response = await fetch(url, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.message || `HTTP error! status: ${response.status}`);
        }
        
        return data;
    } catch (error) {
        console.error('Fetch error:', error);
        throw error;
    }
}

// Show notification with beautiful animation
function showNotification(message, type = 'info', duration = 3000) {
    const notification = document.createElement('div');
    notification.className = `fixed top-4 right-4 z-50 max-w-sm w-full bg-white border-l-4 rounded-xl shadow-lg p-4 transform translate-x-full transition-transform duration-300 ${
        type === 'success' ? 'border-green-500' : 
        type === 'error' ? 'border-red-500' : 'border-blue-500'
    }`;
    
    const icons = {
        success: '✅',
        error: '❌',
        info: 'ℹ️',
        warning: '⚠️'
    };
    
    notification.innerHTML = `
        <div class="flex items-center">
            <span class="text-xl mr-3">${icons[type] || icons.info}</span>
            <p class="text-sm text-gray-800 flex-1">${message}</p>
        </div>
    `;
    
    document.body.appendChild(notification);
    
    // Slide in
    setTimeout(() => {
        notification.style.transform = 'translateX(0)';
    }, 10);
    
    // Auto remove
    setTimeout(() => {
        notification.style.transform = 'translateX(full)';
        setTimeout(() => {
            notification.remove();
        }, 300);
    }, duration);
}

// Format coordinates
function formatCoordinates(lat, lon) {
    return `${parseFloat(lat).toFixed(4)}, ${parseFloat(lon).toFixed(4)}`;
}

// Smooth scroll to element
function smoothScrollTo(element) {
    if (element) {
        element.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
        });
    }
}

// Utility Functions
async function fetchData(url, options = {}) {
    try {
        const response = await fetch(url, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error(`Fetch failed for ${url}:`, error);
        throw error;
    }
}

function showError(message, elementId = 'error-display') {
    const errorElement = document.getElementById(elementId);
    if (errorElement) {
        errorElement.innerHTML = `
            <div class="status-error">
                <strong>❌ Error:</strong> ${message}
            </div>
        `;
        errorElement.className = 'status-display status-error';
    } else {
        alert(`Error: ${message}`);
    }
}

function showSuccess(message, elementId = 'success-display') {
    const successElement = document.getElementById(elementId);
    if (successElement) {
        successElement.innerHTML = `
            <div class="status-success">
                <strong>✅ Success:</strong> ${message}
            </div>
        `;
        successElement.className = 'status-display status-success';
    }
}

function formatDate(dateString) {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

function formatDateTime(dateString) {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}