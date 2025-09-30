// NASA Space App JavaScript
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 NASA Space App initialized');
    
    // Check API health on page load
    checkAPIHealth();
});

async function checkAPIHealth() {
    try {
        console.log('Checking API health...');
        const response = await fetch('/api/health');
        const data = await response.json();
        
        console.log('API Health:', data);
        
        // Update status display if element exists
        const statusDisplay = document.getElementById('api-status');
        if (statusDisplay) {
            statusDisplay.innerHTML = `
                <div class="status-success">
                    <strong>✅ API Status:</strong> ${data.status} - ${data.message}
                    <br><small>Version: ${data.version}</small>
                </div>
            `;
            statusDisplay.className = 'status-display status-success';
        }
        
        return data;
    } catch (error) {
        console.error('API Health check failed:', error);
        
        const statusDisplay = document.getElementById('api-status');
        if (statusDisplay) {
            statusDisplay.innerHTML = `
                <div class="status-error">
                    <strong>❌ API Status:</strong> Connection failed
                    <br><small>Error: ${error.message}</small>
                </div>
            `;
            statusDisplay.className = 'status-display status-error';
        }
        
        return null;
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