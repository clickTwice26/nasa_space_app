// Beautiful Loading Animations System
(function() {
    'use strict';

    // Show beautiful loading animation
    window.showLoading = function(element, message = 'Loading') {
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
    };

    // Hide loading animation
    window.hideLoading = function(element) {
        if (!element) return;
        
        const overlay = element.querySelector('.beautiful-loading');
        if (overlay) {
            overlay.classList.remove('show');
            setTimeout(() => {
                overlay.remove();
            }, 300);
        }
    };

    // Enhanced API call with loading animation
    window.apiCallWithLoading = async function(element, url, options = {}, loadingMessage = 'Loading') {
        const overlay = showLoading(element, loadingMessage);
        
        try {
            // Minimum loading time for better UX (1 second)
            const [response] = await Promise.all([
                fetch(url, {
                    headers: {
                        'Content-Type': 'application/json',
                        ...options.headers
                    },
                    ...options
                }),
                new Promise(resolve => setTimeout(resolve, 1000))
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
    };

    // Show notification with beautiful animation
    window.showNotification = function(message, type = 'info', duration = 3000) {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        
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
            notification.classList.add('show');
        }, 10);
        
        // Auto remove
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => {
                notification.remove();
            }, 300);
        }, duration);
    };

    // Button loading state
    window.setButtonLoading = function(button, loading = true) {
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
    };

    // Initialize loading system
    document.addEventListener('DOMContentLoaded', function() {
        console.log('🎨 Beautiful Loading System initialized');
        
        // Apply consistent card styles to existing cards
        const cards = document.querySelectorAll('.card, .insight-card, .prediction-card, .crop-card, .forecast-day, .service-card, .metric-card');
        cards.forEach(card => {
            if (!card.style.position) {
                card.style.position = 'relative';
            }
        });
    });

})();