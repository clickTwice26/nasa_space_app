/**
 * Risk Dashboard Specific JavaScript
 * Handles the full-featured risk analysis dashboard
 */

class RiskDashboard {
    constructor() {
        this.currentAnalysis = null;
        this.isAnalyzing = false;
        this.init();
    }

    init() {
        console.log('🌾 Risk Dashboard initialized');
        this.setupEventListeners();
        this.setDefaultDates();
        this.loadInitialExample();
    }

    setupEventListeners() {
        // Form submission
        const form = document.getElementById('riskAnalysisForm');
        if (form) {
            form.addEventListener('submit', (e) => this.handleFormSubmit(e));
        }

        // Current location button
        const locationBtn = document.getElementById('useCurrentLocation');
        if (locationBtn) {
            locationBtn.addEventListener('click', () => this.useCurrentLocation());
        }

        // Example buttons
        document.querySelectorAll('.example-btn').forEach(btn => {
            btn.addEventListener('click', () => this.loadExample(btn));
        });

        // Retry button
        const retryBtn = document.getElementById('retryAnalysis');
        if (retryBtn) {
            retryBtn.addEventListener('click', () => this.retryLastAnalysis());
        }

        // Export and share buttons
        this.setupActionButtons();
    }

    setupActionButtons() {
        const exportBtn = document.getElementById('exportReport');
        const shareBtn = document.getElementById('shareReport');
        const saveBtn = document.getElementById('saveToProfile');

        if (exportBtn) {
            exportBtn.addEventListener('click', () => this.exportReport());
        }

        if (shareBtn) {
            shareBtn.addEventListener('click', () => this.shareReport());
        }

        if (saveBtn) {
            saveBtn.addEventListener('click', () => this.saveToProfile());
        }
    }

    setDefaultDates() {
        const endDate = new Date();
        const startDate = new Date(endDate.getTime() - 7 * 24 * 60 * 60 * 1000);
        
        document.getElementById('endDate').value = endDate.toISOString().split('T')[0];
        document.getElementById('startDate').value = startDate.toISOString().split('T')[0];
    }

    loadInitialExample() {
        // Auto-load the Bangladesh rice example after a short delay
        setTimeout(() => {
            const exampleBtn = document.querySelector('.example-btn[data-crop="rice"]');
            if (exampleBtn) {
                this.loadExample(exampleBtn);
            }
        }, 1000);
    }

    loadExample(button) {
        const lat = button.dataset.lat;
        const lon = button.dataset.lon;
        const crop = button.dataset.crop;
        const location = button.dataset.location;
        
        // Update form fields
        document.getElementById('latitude').value = lat;
        document.getElementById('longitude').value = lon;
        document.getElementById('crop').value = crop;
        
        // Trigger analysis
        this.analyzeRisk(lat, lon, crop, location);
    }

    handleFormSubmit(event) {
        event.preventDefault();
        
        const formData = new FormData(event.target);
        const lat = formData.get('latitude');
        const lon = formData.get('longitude');
        const crop = formData.get('crop');
        const startDate = formData.get('startDate');
        const endDate = formData.get('endDate');
        
        // Validate inputs
        if (!this.validateInputs(lat, lon, crop, startDate, endDate)) {
            return;
        }
        
        this.analyzeRisk(lat, lon, crop, null, startDate, endDate);
    }

    validateInputs(lat, lon, crop, startDate, endDate) {
        if (!lat || !lon || !crop || !startDate || !endDate) {
            this.showError('Please fill in all required fields');
            return false;
        }
        
        const latitude = parseFloat(lat);
        const longitude = parseFloat(lon);
        
        if (isNaN(latitude) || latitude < -90 || latitude > 90) {
            this.showError('Latitude must be between -90 and 90');
            return false;
        }
        
        if (isNaN(longitude) || longitude < -180 || longitude > 180) {
            this.showError('Longitude must be between -180 and 180');
            return false;
        }
        
        const start = new Date(startDate);
        const end = new Date(endDate);
        
        if (start > end) {
            this.showError('Start date must be before end date');
            return false;
        }
        
        const daysDiff = (end - start) / (1000 * 60 * 60 * 24);
        if (daysDiff > 30) {
            this.showError('Analysis period cannot exceed 30 days');
            return false;
        }
        
        return true;
    }

    async analyzeRisk(lat, lon, crop, locationName = null, startDate = null, endDate = null) {
        if (this.isAnalyzing) {
            return;
        }
        
        this.isAnalyzing = true;
        this.showLoading();
        
        try {
            // Use provided dates or defaults
            const endDateObj = startDate ? new Date(endDate) : new Date();
            const startDateObj = startDate ? new Date(startDate) : new Date(endDateObj.getTime() - 7 * 24 * 60 * 60 * 1000);
            
            const startStr = this.formatDate(startDateObj);
            const endStr = this.formatDate(endDateObj);
            
            const url = `/api/risk-alerts?lat=${lat}&lon=${lon}&crop=${crop}&start=${startStr}&end=${endStr}`;
            
            console.log(`Analyzing risk: ${url}`);
            
            const response = await fetch(url);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            
            if (data.success) {
                this.currentAnalysis = {
                    ...data,
                    locationName: locationName || `${lat}°, ${lon}°`,
                    analysisTime: new Date().toISOString()
                };
                this.displayResults(this.currentAnalysis);
            } else {
                throw new Error(data.error || 'Analysis failed');
            }
            
        } catch (error) {
            console.error('Risk analysis error:', error);
            this.showError(`Analysis failed: ${error.message}`);
        } finally {
            this.isAnalyzing = false;
            this.hideLoading();
        }
    }

    displayResults(data) {
        this.hideError();
        
        // Update crop name and location
        document.getElementById('resultCropName').textContent = `${data.crop} Analysis`;
        document.getElementById('resultLocationInfo').textContent = 
            `📍 ${data.locationName} • 📅 ${data.period.start} to ${data.period.end}`;
        
        // Update risk badge
        this.updateRiskBadge(data.risk_level);
        
        // Update summary
        this.updateSummary(data.summary);
        
        // Update risk gauge
        this.updateRiskGauge(data.risk_level);
        
        // Update alerts
        this.updateAlerts(data.alerts);
        
        // Update recommendations
        this.updateRecommendations(data.recommendations);
        
        // Update data sources
        this.updateDataSources(data.data_availability);
        
        // Show results
        document.getElementById('analysisResults').classList.remove('hidden');
        
        // Scroll to results
        document.getElementById('analysisResults').scrollIntoView({ 
            behavior: 'smooth', 
            block: 'start' 
        });
        
        console.log('✅ Risk analysis results displayed');
    }

    updateRiskBadge(level) {
        const badge = document.getElementById('resultRiskBadge');
        if (!badge) return;
        
        const configs = {
            low: { emoji: '✅', label: 'Low Risk', classes: 'bg-green-100 text-green-800' },
            medium: { emoji: '⚠️', label: 'Medium Risk', classes: 'bg-yellow-100 text-yellow-800' },
            high: { emoji: '🚨', label: 'High Risk', classes: 'bg-red-100 text-red-800' }
        };
        
        const config = configs[level] || configs.medium;
        badge.textContent = `${config.emoji} ${config.label}`;
        badge.className = `px-3 py-1 text-sm font-semibold rounded-full ${config.classes}`;
    }

    updateSummary(summary) {
        const summaryElement = document.getElementById('resultSummary');
        if (summaryElement && summary) {
            summaryElement.innerHTML = `
                <div class="flex items-start gap-3">
                    <i class="fas fa-info-circle text-terra-primary-600 mt-1"></i>
                    <p class="text-terra-primary-800 leading-relaxed">${summary}</p>
                </div>
            `;
        }
    }

    updateRiskGauge(level) {
        const gaugeContainer = document.getElementById('resultRiskGauge');
        if (!gaugeContainer) return;
        
        const riskValue = this.getRiskValue(level);
        const riskConfig = this.getRiskConfig(level);
        
        gaugeContainer.innerHTML = `
            <svg class="w-full h-full transform -rotate-90" viewBox="0 0 36 36">
                <path d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" 
                      fill="none" stroke="#e5e7eb" stroke-width="4"/>
                <path d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" 
                      fill="none" stroke="${riskConfig.strokeColor}" stroke-width="4" 
                      stroke-dasharray="${riskValue}, 100"
                      class="transition-all duration-1000 ease-out"/>
            </svg>
            <div class="absolute inset-0 flex items-center justify-center">
                <div class="text-center">
                    <div class="text-2xl">${riskConfig.emoji}</div>
                    <div class="text-xs font-bold ${riskConfig.textColorRaw} mt-1">${riskValue}%</div>
                </div>
            </div>
        `;
    }

    updateAlerts(alerts) {
        const alertsContainer = document.getElementById('resultAlerts');
        const alertCount = document.getElementById('alertCount');
        
        if (!alertsContainer) return;
        
        if (!alerts || alerts.length === 0) {
            alertsContainer.innerHTML = `
                <div class="bg-green-50 border border-green-200 rounded-lg p-4">
                    <div class="flex items-center gap-2 text-green-700">
                        <i class="fas fa-check-circle"></i>
                        <span class="font-medium">No immediate risks detected</span>
                    </div>
                    <p class="text-sm text-green-600 mt-1">Conditions appear favorable for your crop</p>
                </div>
            `;
            if (alertCount) alertCount.textContent = '0';
            return;
        }
        
        if (alertCount) alertCount.textContent = alerts.length.toString();
        
        alertsContainer.innerHTML = alerts.map(alert => {
            const alertType = this.categorizeAlert(alert);
            return `
                <div class="bg-${alertType.color}-50 border border-${alertType.color}-200 rounded-lg p-4">
                    <div class="flex items-start gap-3">
                        <i class="${alertType.icon} text-${alertType.color}-600 mt-0.5"></i>
                        <div class="flex-1">
                            <p class="text-sm text-${alertType.color}-800 font-medium leading-relaxed">${alert}</p>
                        </div>
                    </div>
                </div>
            `;
        }).join('');
    }

    updateRecommendations(recommendations) {
        const container = document.getElementById('resultRecommendations');
        if (!container) return;
        
        if (!recommendations || recommendations.length === 0) {
            container.innerHTML = `
                <div class="bg-terra-primary-50 border border-terra-primary-200 rounded-lg p-4">
                    <div class="flex items-center gap-2 text-terra-primary-700">
                        <i class="fas fa-thumbs-up"></i>
                        <span class="font-medium">Continue current practices</span>
                    </div>
                    <p class="text-sm text-terra-primary-600 mt-1">No specific actions needed at this time</p>
                </div>
            `;
            return;
        }
        
        container.innerHTML = recommendations.map(rec => `
            <div class="bg-terra-primary-50 border border-terra-primary-200 rounded-lg p-4">
                <div class="flex items-start gap-3">
                    <i class="fas fa-lightbulb text-terra-primary-600 mt-0.5"></i>
                    <p class="text-sm text-terra-primary-800 leading-relaxed">${rec}</p>
                </div>
            </div>
        `).join('');
    }

    updateDataSources(availability) {
        const container = document.getElementById('resultDataSources');
        if (!container || !availability) return;
        
        const sources = {
            'power_api': { name: 'NASA POWER', icon: '🛰️', description: 'Weather data' },
            'gpm_api': { name: 'GPM IMERG', icon: '🌧️', description: 'Precipitation data' },
            'modis_api': { name: 'MODIS', icon: '🌱', description: 'Vegetation health' },
            'worldview_api': { name: 'Worldview', icon: '🌍', description: 'Satellite imagery' }
        };
        
        container.innerHTML = Object.entries(sources).map(([key, source]) => {
            const isAvailable = availability[key];
            const statusClass = isAvailable ? 'border-green-200 bg-green-50' : 'border-red-200 bg-red-50';
            const statusIcon = isAvailable ? '✅' : '❌';
            const statusText = isAvailable ? 'Available' : 'Unavailable';
            const statusColor = isAvailable ? 'text-green-700' : 'text-red-700';
            
            return `
                <div class="${statusClass} border rounded-lg p-4 text-center">
                    <div class="text-2xl mb-2">${source.icon}</div>
                    <h4 class="font-medium text-gray-900 text-sm">${source.name}</h4>
                    <p class="text-xs text-gray-600 mb-2">${source.description}</p>
                    <div class="flex items-center justify-center gap-1 text-xs ${statusColor}">
                        <span>${statusIcon}</span>
                        <span>${statusText}</span>
                    </div>
                </div>
            `;
        }).join('');
    }

    getRiskConfig(level) {
        const configs = {
            low: {
                emoji: '✅',
                strokeColor: '#10b981',
                textColorRaw: 'text-green-600'
            },
            medium: {
                emoji: '⚠️',
                strokeColor: '#f59e0b',
                textColorRaw: 'text-yellow-600'
            },
            high: {
                emoji: '🚨',
                strokeColor: '#ef4444',
                textColorRaw: 'text-red-600'
            }
        };
        
        return configs[level] || configs.medium;
    }

    getRiskValue(level) {
        const values = { low: 25, medium: 60, high: 90 };
        return values[level] || 50;
    }

    categorizeAlert(alert) {
        const alertText = alert.toLowerCase();
        
        if (alertText.includes('flood') || alertText.includes('heavy rain')) {
            return { color: 'blue', icon: 'fas fa-water' };
        } else if (alertText.includes('drought') || alertText.includes('water')) {
            return { color: 'orange', icon: 'fas fa-fire' };
        } else if (alertText.includes('heat') || alertText.includes('temperature')) {
            return { color: 'red', icon: 'fas fa-thermometer-three-quarters' };
        } else if (alertText.includes('cold') || alertText.includes('frost')) {
            return { color: 'blue', icon: 'fas fa-snowflake' };
        } else if (alertText.includes('vegetation') || alertText.includes('crop')) {
            return { color: 'green', icon: 'fas fa-seedling' };
        } else {
            return { color: 'yellow', icon: 'fas fa-exclamation-triangle' };
        }
    }

    async useCurrentLocation() {
        if (!navigator.geolocation) {
            this.showError('Geolocation is not supported by this browser');
            return;
        }
        
        const locationBtn = document.getElementById('useCurrentLocation');
        const originalText = locationBtn.innerHTML;
        
        locationBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Getting location...';
        locationBtn.disabled = true;
        
        try {
            const position = await new Promise((resolve, reject) => {
                navigator.geolocation.getCurrentPosition(resolve, reject, {
                    enableHighAccuracy: true,
                    timeout: 10000,
                    maximumAge: 60000
                });
            });
            
            const lat = position.coords.latitude.toFixed(4);
            const lon = position.coords.longitude.toFixed(4);
            
            document.getElementById('latitude').value = lat;
            document.getElementById('longitude').value = lon;
            
            // Show success message
            this.showToast(`Location updated: ${lat}°, ${lon}°`, 'success');
            
        } catch (error) {
            console.error('Geolocation error:', error);
            this.showError('Unable to get your location. Please enter coordinates manually.');
        } finally {
            locationBtn.innerHTML = originalText;
            locationBtn.disabled = false;
        }
    }

    formatDate(date) {
        return date.getFullYear().toString() + 
               (date.getMonth() + 1).toString().padStart(2, '0') + 
               date.getDate().toString().padStart(2, '0');
    }

    showLoading() {
        document.getElementById('analysisLoading')?.classList.remove('hidden');
        document.getElementById('analysisResults')?.classList.add('hidden');
        document.getElementById('analysisError')?.classList.add('hidden');
        
        // Disable form
        const form = document.getElementById('riskAnalysisForm');
        if (form) {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Analyzing...';
            }
        }
    }

    hideLoading() {
        document.getElementById('analysisLoading')?.classList.add('hidden');
        
        // Re-enable form
        const form = document.getElementById('riskAnalysisForm');
        if (form) {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.innerHTML = '<i class="fas fa-analytics"></i> <span>Analyze Crop Risk</span>';
            }
        }
    }

    showError(message) {
        document.getElementById('analysisError')?.classList.remove('hidden');
        document.getElementById('analysisResults')?.classList.add('hidden');
        
        const errorMessage = document.getElementById('analysisErrorMessage');
        if (errorMessage) {
            errorMessage.textContent = message;
        }
    }

    hideError() {
        document.getElementById('analysisError')?.classList.add('hidden');
    }

    showToast(message, type = 'info') {
        // Create toast notification
        const toast = document.createElement('div');
        const bgColor = type === 'success' ? 'bg-green-500' : type === 'error' ? 'bg-red-500' : 'bg-blue-500';
        
        toast.className = `fixed top-4 right-4 ${bgColor} text-white px-6 py-3 rounded-lg shadow-lg z-50 transform translate-x-full transition-transform duration-300`;
        toast.textContent = message;
        
        document.body.appendChild(toast);
        
        // Animate in
        setTimeout(() => {
            toast.classList.remove('translate-x-full');
        }, 100);
        
        // Animate out and remove
        setTimeout(() => {
            toast.classList.add('translate-x-full');
            setTimeout(() => {
                document.body.removeChild(toast);
            }, 300);
        }, 3000);
    }

    retryLastAnalysis() {
        const form = document.getElementById('riskAnalysisForm');
        if (form) {
            form.dispatchEvent(new Event('submit'));
        }
    }

    exportReport() {
        if (!this.currentAnalysis) {
            this.showToast('No analysis data to export', 'error');
            return;
        }
        
        const reportData = {
            analysis: this.currentAnalysis,
            exportTime: new Date().toISOString(),
            exportedBy: 'TerraPulse Risk Engine'
        };
        
        const blob = new Blob([JSON.stringify(reportData, null, 2)], {
            type: 'application/json'
        });
        
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `terrapulse-risk-report-${this.formatDate(new Date())}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        this.showToast('Report exported successfully', 'success');
    }

    shareReport() {
        if (!this.currentAnalysis) {
            this.showToast('No analysis data to share', 'error');
            return;
        }
        
        const shareText = `🌾 Crop Risk Analysis: ${this.currentAnalysis.crop}\n` +
                         `📍 ${this.currentAnalysis.locationName}\n` +
                         `🚨 Risk Level: ${this.currentAnalysis.risk_level.toUpperCase()}\n` +
                         `📊 ${this.currentAnalysis.alerts.length} alerts detected\n\n` +
                         `${this.currentAnalysis.summary}\n\n` +
                         `Powered by TerraPulse & NASA satellite data`;
        
        if (navigator.share) {
            navigator.share({
                title: 'TerraPulse Risk Analysis',
                text: shareText,
                url: window.location.href
            }).then(() => {
                this.showToast('Report shared successfully', 'success');
            }).catch(err => {
                console.log('Share failed:', err);
                this.fallbackShare(shareText);
            });
        } else {
            this.fallbackShare(shareText);
        }
    }

    fallbackShare(text) {
        navigator.clipboard.writeText(text).then(() => {
            this.showToast('Report copied to clipboard', 'success');
        }).catch(() => {
            this.showToast('Unable to share report', 'error');
        });
    }

    saveToProfile() {
        if (!this.currentAnalysis) {
            this.showToast('No analysis data to save', 'error');
            return;
        }
        
        // This would integrate with the user profile system
        // For now, save to localStorage as a demo
        const savedAnalyses = JSON.parse(localStorage.getItem('terrapu‌lse_saved_analyses') || '[]');
        savedAnalyses.unshift({
            ...this.currentAnalysis,
            savedAt: new Date().toISOString(),
            id: Date.now().toString()
        });
        
        // Keep only the last 10 analyses
        savedAnalyses.splice(10);
        
        localStorage.setItem('terrapulse_saved_analyses', JSON.stringify(savedAnalyses));
        
        this.showToast('Analysis saved to your profile', 'success');
    }
}

// Initialize Risk Dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    if (document.getElementById('riskAnalysisForm')) {
        window.riskDashboard = new RiskDashboard();
    }
});

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = RiskDashboard;
}