/**
 * TerraPulse Agricultural Risk Engine Frontend
 * Integrates NASA satellite data for intelligent crop risk analysis
 */

class RiskEngine {
    constructor() {
        this.apiBaseUrl = '/api';
        this.currentRiskData = null;
        this.refreshInterval = null;
        this.init();
    }

    init() {
        console.log('🌾 Risk Engine initialized');
        this.setupEventListeners();
        this.loadInitialRiskData();
        
        // Auto-refresh every 30 minutes
        this.startAutoRefresh();
    }

    setupEventListeners() {
        // Refresh button
        const refreshBtn = document.getElementById('refreshRiskBtn');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => this.refreshRiskData());
        }

        // Risk analysis form (if on risk dashboard)
        const riskForm = document.getElementById('riskAnalysisForm');
        if (riskForm) {
            riskForm.addEventListener('submit', (e) => this.handleRiskFormSubmit(e));
        }

        // Location update listener
        document.addEventListener('locationUpdated', (e) => {
            this.loadRiskDataForLocation(e.detail.lat, e.detail.lon);
        });
    }

    async loadInitialRiskData() {
        try {
            // Get user's location from profile or use default
            const userLocation = await this.getUserLocation();
            const userCrop = await this.getUserCrop();
            
            if (userLocation.lat && userLocation.lon && userCrop) {
                await this.loadRiskDataForLocation(userLocation.lat, userLocation.lon, userCrop);
            } else {
                this.showLocationPrompt();
            }
        } catch (error) {
            console.error('Failed to load initial risk data:', error);
            this.showError('Unable to load risk data. Please check your location settings.');
        }
    }

    async getUserLocation() {
        try {
            const response = await fetch('/api/user/profile');
            if (response.ok) {
                const profile = await response.json();
                return {
                    lat: profile.latitude || 23.7644, // Default to Dhaka
                    lon: profile.longitude || 90.3897
                };
            }
        } catch (error) {
            console.log('Using default location');
        }
        
        // Default location (Dhaka, Bangladesh)
        return { lat: 23.7644, lon: 90.3897 };
    }

    async getUserCrop() {
        try {
            const response = await fetch('/api/user/profile');
            if (response.ok) {
                const profile = await response.json();
                return profile.primary_crop?.toLowerCase() || 'rice';
            }
        } catch (error) {
            console.log('Using default crop');
        }
        
        return 'rice'; // Default crop
    }

    async loadRiskDataForLocation(lat, lon, crop = 'rice') {
        this.showLoading();
        
        try {
            // Get date range (last 7 days)
            const endDate = new Date();
            const startDate = new Date(endDate.getTime() - 7 * 24 * 60 * 60 * 1000);
            
            const startStr = this.formatDate(startDate);
            const endStr = this.formatDate(endDate);
            
            const url = `${this.apiBaseUrl}/risk-alerts?lat=${lat}&lon=${lon}&crop=${crop}&start=${startStr}&end=${endStr}`;
            
            console.log(`Fetching risk data: ${url}`);
            
            const response = await fetch(url);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const riskData = await response.json();
            
            if (riskData.success) {
                this.currentRiskData = riskData;
                this.displayRiskData(riskData);
                this.updateRiskWidgets(riskData);
            } else {
                throw new Error(riskData.error || 'Risk analysis failed');
            }
            
        } catch (error) {
            console.error('Risk data fetch failed:', error);
            this.showError(`Failed to fetch risk data: ${error.message}`);
        } finally {
            this.hideLoading();
        }
    }

    displayRiskData(data) {
        this.hideError();
        
        // Update risk level display
        this.updateRiskLevel(data.risk_level);
        
        // Update summary
        this.updateRiskSummary(data.summary);
        
        // Update alerts
        this.updateRiskAlerts(data.alerts);
        
        // Update risk gauge
        this.updateRiskGauge(data.risk_level);
        
        // Show results
        document.getElementById('riskResults')?.classList.remove('hidden');
        
        console.log('✅ Risk data displayed successfully');
    }

    updateRiskLevel(level) {
        const riskLevelText = document.getElementById('riskLevelText');
        const riskBadge = document.getElementById('riskBadge');
        
        if (riskLevelText && riskBadge) {
            const riskConfig = this.getRiskConfig(level);
            
            riskLevelText.textContent = riskConfig.emoji;
            riskLevelText.className = `text-4xl font-bold ${riskConfig.textColor}`;
            
            riskBadge.textContent = `${riskConfig.emoji} ${riskConfig.label}`;
            riskBadge.className = `px-3 py-1 text-sm font-semibold rounded-full ${riskConfig.bgColor} ${riskConfig.textColor}`;
        }
    }

    updateRiskSummary(summary) {
        const summaryElement = document.getElementById('riskSummary');
        if (summaryElement && summary) {
            summaryElement.innerHTML = `
                <div class="flex items-start gap-2">
                    <i class="fas fa-info-circle text-terra-primary-500 mt-0.5"></i>
                    <p class="text-sm text-gray-700 leading-relaxed">${summary}</p>
                </div>
            `;
        }
    }

    updateRiskAlerts(alerts) {
        const alertsContainer = document.getElementById('riskAlerts');
        if (!alertsContainer || !alerts || alerts.length === 0) {
            if (alertsContainer) {
                alertsContainer.innerHTML = `
                    <div class="bg-green-50 border border-green-200 rounded-lg p-3">
                        <div class="flex items-center gap-2 text-green-700">
                            <i class="fas fa-check-circle"></i>
                            <span class="text-sm font-medium">No immediate risks detected</span>
                        </div>
                    </div>
                `;
            }
            return;
        }
        
        // Show top 3 alerts in dashboard
        const topAlerts = alerts.slice(0, 3);
        
        alertsContainer.innerHTML = topAlerts.map(alert => {
            const alertType = this.categorizeAlert(alert);
            return `
                <div class="bg-${alertType.color}-50 border border-${alertType.color}-200 rounded-lg p-3">
                    <div class="flex items-start gap-2">
                        <i class="${alertType.icon} text-${alertType.color}-600 mt-0.5"></i>
                        <span class="text-sm text-${alertType.color}-700 leading-relaxed">${alert}</span>
                    </div>
                </div>
            `;
        }).join('');
        
        // Add "view more" link if there are additional alerts
        if (alerts.length > 3) {
            alertsContainer.innerHTML += `
                <div class="text-center">
                    <a href="/risk-dashboard" class="text-sm text-terra-primary-600 hover:text-terra-primary-700 font-medium">
                        +${alerts.length - 3} more alerts - View Full Report
                    </a>
                </div>
            `;
        }
    }

    updateRiskGauge(riskLevel) {
        const gaugeContainer = document.getElementById('riskGauge');
        if (!gaugeContainer) return;
        
        const riskValue = this.getRiskValue(riskLevel);
        const riskConfig = this.getRiskConfig(riskLevel);
        
        gaugeContainer.innerHTML = `
            <svg class="w-full h-full transform -rotate-90" viewBox="0 0 36 36">
                <path d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" 
                      fill="none" stroke="#e5e7eb" stroke-width="3"/>
                <path d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" 
                      fill="none" stroke="${riskConfig.strokeColor}" stroke-width="3" 
                      stroke-dasharray="${riskValue}, 100"
                      class="transition-all duration-1000 ease-out"/>
            </svg>
            <div class="absolute inset-0 flex items-center justify-center">
                <span class="text-xs font-bold ${riskConfig.textColorRaw}">${riskValue}%</span>
            </div>
        `;
    }

    updateRiskWidgets(data) {
        // Update other dashboard widgets based on risk data
        this.updateWeatherWidget(data);
        this.updateDataSourceStatus(data.data_availability);
    }

    updateWeatherWidget(data) {
        // Update weather information in the main dashboard card if available
        const weatherInfo = data.weather_summary;
        if (weatherInfo) {
            // Update weather display elements
            // This would integrate with existing weather display logic
        }
    }

    updateDataSourceStatus(availability) {
        // Create or update data source status indicator
        let statusContainer = document.getElementById('dataSourceStatus');
        
        if (!statusContainer) {
            // Create status container if it doesn't exist
            const riskCard = document.getElementById('riskEngineCard');
            if (riskCard) {
                statusContainer = document.createElement('div');
                statusContainer.id = 'dataSourceStatus';
                statusContainer.className = 'mt-4 pt-4 border-t border-gray-200';
                riskCard.appendChild(statusContainer);
            }
        }
        
        if (statusContainer && availability) {
            const sources = {
                'power_api': '🛰️ NASA POWER',
                'gpm_api': '🌧️ GPM IMERG',
                'modis_api': '🌱 MODIS',
                'worldview_api': '📡 Worldview'
            };
            
            const sourceElements = Object.entries(sources).map(([key, label]) => {
                const isAvailable = availability[key];
                const statusIcon = isAvailable ? '✅' : '❌';
                const statusColor = isAvailable ? 'text-green-600' : 'text-red-500';
                
                return `<span class="text-xs ${statusColor}">${statusIcon} ${label}</span>`;
            }).join('');
            
            statusContainer.innerHTML = `
                <div class="flex justify-between items-center text-xs text-gray-500">
                    <span>Data Sources:</span>
                    <div class="flex gap-2">
                        ${sourceElements}
                    </div>
                </div>
            `;
        }
    }

    getRiskConfig(level) {
        const configs = {
            low: {
                label: 'Low Risk',
                emoji: '✅',
                bgColor: 'bg-green-100',
                textColor: 'text-green-800',
                textColorRaw: 'text-green-600',
                strokeColor: '#10b981'
            },
            medium: {
                label: 'Medium Risk',
                emoji: '⚠️',
                bgColor: 'bg-yellow-100',
                textColor: 'text-yellow-800',
                textColorRaw: 'text-yellow-600',
                strokeColor: '#f59e0b'
            },
            high: {
                label: 'High Risk',
                emoji: '🚨',
                bgColor: 'bg-red-100',
                textColor: 'text-red-800',
                textColorRaw: 'text-red-600',
                strokeColor: '#ef4444'
            }
        };
        
        return configs[level] || configs.medium;
    }

    getRiskValue(level) {
        const values = {
            low: 25,
            medium: 60,
            high: 90
        };
        
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

    showLoading() {
        document.getElementById('riskLoading')?.classList.remove('hidden');
        document.getElementById('riskResults')?.classList.add('hidden');
        document.getElementById('riskError')?.classList.add('hidden');
    }

    hideLoading() {
        document.getElementById('riskLoading')?.classList.add('hidden');
    }

    showError(message) {
        const errorElement = document.getElementById('riskError');
        const errorMessageElement = document.getElementById('riskErrorMessage');
        
        if (errorElement && errorMessageElement) {
            errorMessageElement.textContent = message;
            errorElement.classList.remove('hidden');
        }
        
        document.getElementById('riskResults')?.classList.add('hidden');
    }

    hideError() {
        document.getElementById('riskError')?.classList.add('hidden');
    }

    showLocationPrompt() {
        const riskCard = document.getElementById('riskEngineCard');
        if (riskCard) {
            riskCard.innerHTML = `
                <div class="text-center py-8">
                    <i class="fas fa-map-marker-alt text-4xl text-gray-400 mb-4"></i>
                    <h4 class="text-lg font-semibold text-gray-700 mb-2">Location Required</h4>
                    <p class="text-sm text-gray-600 mb-4">Please set your location to get personalized crop risk analysis</p>
                    <a href="/settings" class="inline-flex items-center gap-2 px-4 py-2 bg-terra-primary-500 text-white rounded-lg hover:bg-terra-primary-600 transition-colors">
                        <i class="fas fa-cog"></i>
                        Update Location
                    </a>
                </div>
            `;
        }
    }

    formatDate(date) {
        return date.getFullYear().toString() + 
               (date.getMonth() + 1).toString().padStart(2, '0') + 
               date.getDate().toString().padStart(2, '0');
    }

    async refreshRiskData() {
        const userLocation = await this.getUserLocation();
        const userCrop = await this.getUserCrop();
        await this.loadRiskDataForLocation(userLocation.lat, userLocation.lon, userCrop);
    }

    startAutoRefresh() {
        // Refresh every 30 minutes
        this.refreshInterval = setInterval(() => {
            this.refreshRiskData();
        }, 30 * 60 * 1000);
    }

    stopAutoRefresh() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
            this.refreshInterval = null;
        }
    }

    // Public API for other components
    getCurrentRiskData() {
        return this.currentRiskData;
    }

    async analyzeCustomLocation(lat, lon, crop, startDate, endDate) {
        const startStr = this.formatDate(new Date(startDate));
        const endStr = this.formatDate(new Date(endDate));
        
        const url = `${this.apiBaseUrl}/risk-alerts?lat=${lat}&lon=${lon}&crop=${crop}&start=${startStr}&end=${endStr}`;
        
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        return await response.json();
    }

    handleRiskFormSubmit(event) {
        event.preventDefault();
        
        const formData = new FormData(event.target);
        const lat = parseFloat(formData.get('latitude'));
        const lon = parseFloat(formData.get('longitude'));
        const crop = formData.get('crop');
        const startDate = formData.get('startDate');
        const endDate = formData.get('endDate');
        
        this.analyzeCustomLocation(lat, lon, crop, startDate, endDate)
            .then(data => {
                if (data.success) {
                    this.displayFullRiskReport(data);
                } else {
                    throw new Error(data.error);
                }
            })
            .catch(error => {
                console.error('Risk analysis failed:', error);
                this.showError(error.message);
            });
    }

    displayFullRiskReport(data) {
        // Implementation for full risk report display
        // This would be used on the dedicated risk dashboard page
        console.log('Displaying full risk report:', data);
        
        // Dispatch event for other components
        document.dispatchEvent(new CustomEvent('riskReportUpdated', {
            detail: { riskData: data }
        }));
    }
}

// Initialize Risk Engine when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Only initialize if we're on a page with risk components
    if (document.getElementById('riskEngineCard') || document.getElementById('riskAnalysisForm')) {
        window.riskEngine = new RiskEngine();
    }
});

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = RiskEngine;
}