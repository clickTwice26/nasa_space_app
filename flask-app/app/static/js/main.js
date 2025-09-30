// NASA Space App JavaScript
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 NASA Space App initialized');
    
    // Check API health on page load
    checkAPIHealth();
});

async function checkAPIHealth() {
    try {
        const response = await fetch('/api/health');
        const data = await response.json();
        console.log('API Health:', data);
    } catch (error) {
        console.error('API Health check failed:', error);
    }
}

// Function to fetch NASA data
async function fetchNASAData() {
    try {
        const response = await fetch('/api/data');
        const data = await response.json();
        console.log('NASA Data:', data);
        return data;
    } catch (error) {
        console.error('Failed to fetch NASA data:', error);
        return null;
    }
}