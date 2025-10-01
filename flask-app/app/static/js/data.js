// Data Explorer page JavaScript

let currentPage = 1;
let currentFilters = {};
let weatherData = null;

// NASA POWER Weather Data Functions
async function fetchWeatherData() {
    const lat = document.getElementById('weather-lat').value;
    const lon = document.getElementById('weather-lon').value;
    const startDate = document.getElementById('weather-start').value;
    const endDate = document.getElementById('weather-end').value;
    
    if (!lat || !lon || !startDate || !endDate) {
        showError('Please fill in all location and date fields', 'weather-data-container');
        return;
    }
    
    // Convert dates to YYYYMMDD format
    const start = startDate.replace(/-/g, '');
    const end = endDate.replace(/-/g, '');
    
    const container = document.getElementById('weather-data-container');
    container.innerHTML = `
        <div class="text-center py-8">
            <div class="spinner-border text-terra-green mx-auto mb-3"></div>
            <p class="text-gray-600">Fetching NASA POWER weather data...</p>
        </div>
    `;
    
    try {
        const response = await fetch(`/api/power-data?lat=${lat}&lon=${lon}&start=${start}&end=${end}`);
        const data = await response.json();
        
        if (data.success) {
            weatherData = data;
            displayWeatherData(data);
            displayWeatherStats(data);
            showSuccess(`Loaded ${data.data.length} days of weather data`, 'weather-data-container');
        } else {
            throw new Error(data.error || 'Failed to fetch weather data');
        }
    } catch (error) {
        showError(`Failed to fetch weather data: ${error.message}`, 'weather-data-container');
        container.innerHTML = `
            <div class="text-center py-8 text-red-600">
                <i data-lucide="alert-circle" class="w-12 h-12 mx-auto mb-2"></i>
                <p>Error: ${error.message}</p>
                <button onclick="fetchWeatherData()" class="mt-3 btn-terra-primary text-sm">
                    Try Again
                </button>
            </div>
        `;
    }
}

function displayWeatherData(data) {
    const container = document.getElementById('weather-data-container');
    
    if (!data.data || data.data.length === 0) {
        container.innerHTML = `
            <div class="text-center py-8 text-gray-500">
                <i data-lucide="cloud-off" class="w-12 h-12 mx-auto mb-2"></i>
                <p>No weather data available for the selected period</p>
            </div>
        `;
        return;
    }
    
    const weatherCards = data.data.map(day => {
        const temp = day.temperature !== null ? `${day.temperature.toFixed(1)}°C` : 'N/A';
        const precip = day.precipitation !== null ? `${day.precipitation.toFixed(1)}mm` : 'N/A';
        const tempColor = getTempColor(day.temperature);
        const precipColor = getPrecipColor(day.precipitation);
        
        return `
            <div class="bg-white rounded-lg border border-gray-200 p-4 hover:shadow-md transition-shadow">
                <div class="flex items-center justify-between mb-3">
                    <div>
                        <h4 class="font-medium text-gray-900">${formatDate(day.date)}</h4>
                        <p class="text-xs text-gray-500">${day.date_raw}</p>
                    </div>
                    <div class="text-right">
                        <div class="flex items-center space-x-2">
                            <i data-lucide="thermometer" class="w-4 h-4 ${tempColor}"></i>
                            <span class="font-semibold ${tempColor}">${temp}</span>
                        </div>
                    </div>
                </div>
                <div class="flex items-center justify-between">
                    <div class="flex items-center space-x-2">
                        <i data-lucide="cloud-rain" class="w-4 h-4 ${precipColor}"></i>
                        <span class="text-sm ${precipColor}">${precip}</span>
                    </div>
                    <div class="text-xs text-gray-400">
                        ${getWeatherCondition(day.temperature, day.precipitation)}
                    </div>
                </div>
            </div>
        `;
    }).join('');
    
    container.innerHTML = `
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            ${weatherCards}
        </div>
        <div class="mt-4 p-4 bg-blue-50 rounded-lg border border-blue-200">
            <div class="flex items-start space-x-3">
                <i data-lucide="info" class="w-5 h-5 text-blue-600 mt-0.5"></i>
                <div>
                    <h4 class="font-medium text-blue-900 mb-1">Data Source</h4>
                    <p class="text-sm text-blue-700">
                        ${data.metadata.source} - Location: ${data.metadata.coordinate.latitude.toFixed(4)}, ${data.metadata.coordinate.longitude.toFixed(4)}
                    </p>
                    <p class="text-xs text-blue-600 mt-1">
                        ${data.metadata.data_period.total_days} days of data from ${data.metadata.data_period.start} to ${data.metadata.data_period.end}
                    </p>
                </div>
            </div>
        </div>
    `;
}

function displayWeatherStats(data) {
    const statsContainer = document.getElementById('weather-stats');
    
    if (!data.data || data.data.length === 0) {
        statsContainer.classList.add('hidden');
        return;
    }
    
    // Calculate statistics
    const temperatures = data.data.filter(d => d.temperature !== null).map(d => d.temperature);
    const precipitations = data.data.filter(d => d.precipitation !== null).map(d => d.precipitation);
    
    const avgTemp = temperatures.length > 0 ? temperatures.reduce((a, b) => a + b) / temperatures.length : 0;
    const maxTemp = temperatures.length > 0 ? Math.max(...temperatures) : 0;
    const minTemp = temperatures.length > 0 ? Math.min(...temperatures) : 0;
    const totalPrecip = precipitations.length > 0 ? precipitations.reduce((a, b) => a + b) : 0;
    
    statsContainer.innerHTML = `
        <div class="bg-gradient-to-br from-orange-50 to-red-50 p-4 rounded-lg border border-orange-200">
            <div class="flex items-center space-x-2 mb-2">
                <i data-lucide="thermometer" class="w-5 h-5 text-orange-600"></i>
                <span class="text-sm font-medium text-orange-900">Avg Temperature</span>
            </div>
            <p class="text-2xl font-bold text-orange-700">${avgTemp.toFixed(1)}°C</p>
        </div>
        <div class="bg-gradient-to-br from-red-50 to-pink-50 p-4 rounded-lg border border-red-200">
            <div class="flex items-center space-x-2 mb-2">
                <i data-lucide="trending-up" class="w-5 h-5 text-red-600"></i>
                <span class="text-sm font-medium text-red-900">Max Temperature</span>
            </div>
            <p class="text-2xl font-bold text-red-700">${maxTemp.toFixed(1)}°C</p>
        </div>
        <div class="bg-gradient-to-br from-blue-50 to-cyan-50 p-4 rounded-lg border border-blue-200">
            <div class="flex items-center space-x-2 mb-2">
                <i data-lucide="trending-down" class="w-5 h-5 text-blue-600"></i>
                <span class="text-sm font-medium text-blue-900">Min Temperature</span>
            </div>
            <p class="text-2xl font-bold text-blue-700">${minTemp.toFixed(1)}°C</p>
        </div>
        <div class="bg-gradient-to-br from-cyan-50 to-teal-50 p-4 rounded-lg border border-cyan-200">
            <div class="flex items-center space-x-2 mb-2">
                <i data-lucide="cloud-rain" class="w-5 h-5 text-cyan-600"></i>
                <span class="text-sm font-medium text-cyan-900">Total Rainfall</span>
            </div>
            <p class="text-2xl font-bold text-cyan-700">${totalPrecip.toFixed(1)}mm</p>
        </div>
    `;
    
    statsContainer.classList.remove('hidden');
}

function getTempColor(temp) {
    if (temp === null) return 'text-gray-400';
    if (temp >= 35) return 'text-red-600';
    if (temp >= 30) return 'text-orange-600';
    if (temp >= 25) return 'text-yellow-600';
    if (temp >= 20) return 'text-green-600';
    return 'text-blue-600';
}

function getPrecipColor(precip) {
    if (precip === null || precip === 0) return 'text-gray-400';
    if (precip >= 20) return 'text-blue-600';
    if (precip >= 10) return 'text-cyan-600';
    if (precip >= 5) return 'text-teal-600';
    return 'text-green-600';
}

function getWeatherCondition(temp, precip) {
    if (temp === null && precip === null) return 'No data';
    if (precip > 20) return 'Heavy rain';
    if (precip > 10) return 'Moderate rain';
    if (precip > 0) return 'Light rain';
    if (temp >= 35) return 'Very hot';
    if (temp >= 30) return 'Hot';
    if (temp >= 25) return 'Warm';
    if (temp >= 20) return 'Mild';
    return 'Cool';
}

function refreshWeatherData() {
    if (weatherData) {
        displayWeatherData(weatherData);
        displayWeatherStats(weatherData);
        showSuccess('Weather data refreshed', 'weather-data-container');
    } else {
        fetchWeatherData();
    }
}

// Original data functions continue...

async function loadDataStats() {
    try {
        const stats = await fetchData('/api/stats');
        displayDataStats(stats);
    } catch (error) {
        showError(`Failed to load statistics: ${error.message}`, 'data-status');
    }
}

function displayDataStats(stats) {
    const statsDiv = document.getElementById('data-stats');
    
    const statsHTML = `
        <div class="stats-grid">
            <div class="stat-card">
                <h3>Total Records</h3>
                <p class="stat-number">${stats.total_records}</p>
            </div>
            <div class="stat-card">
                <h3>Record Types</h3>
                <ul class="stat-list">
                    ${stats.record_types.map(rt => `<li>${rt.type}: ${rt.count}</li>`).join('')}
                </ul>
            </div>
            <div class="stat-card">
                <h3>Missions with Data</h3>
                <p class="stat-number">${stats.missions_with_data.length}</p>
            </div>
        </div>
    `;
    
    statsDiv.innerHTML = statsHTML;
}

async function loadAllData(page = 1) {
    currentPage = page;
    currentFilters = {};
    
    try {
        const data = await fetchData(`/api/data?page=${page}&per_page=20`);
        displayDataRecords(data);
        displayPagination(data.pagination);
    } catch (error) {
        showError(`Failed to load data: ${error.message}`, 'data-status');
    }
}

async function loadFilteredData(page = 1) {
    currentPage = page;
    
    const recordType = document.getElementById('record-type').value;
    const missionId = document.getElementById('mission-filter').value;
    
    let url = `/api/data?page=${page}&per_page=20`;
    
    if (recordType) {
        url = `/api/data/type/${recordType}?page=${page}&per_page=20`;
        currentFilters.type = recordType;
    } else if (missionId) {
        url = `/api/data/mission/${missionId}?page=${page}&per_page=20`;
        currentFilters.mission = missionId;
    } else {
        return loadAllData(page);
    }
    
    try {
        const data = await fetchData(url);
        displayDataRecords(data);
        displayPagination(data.pagination);
        showSuccess(`Loaded ${data.pagination.total} filtered records`, 'data-status');
    } catch (error) {
        showError(`Failed to load filtered data: ${error.message}`, 'data-status');
    }
}

function displayDataRecords(data) {
    const dataList = document.getElementById('data-list');
    
    if (!data.data || data.data.length === 0) {
        dataList.innerHTML = '<p>No data records found</p>';
        return;
    }
    
    const recordsHTML = data.data.map(record => `
        <div class="data-item">
            <h4>${record.record_type} - Record #${record.id}</h4>
            <p><strong>Mission ID:</strong> ${record.mission_id}</p>
            <p><strong>Data Source:</strong> ${record.data_source || 'N/A'}</p>
            <p><strong>Timestamp:</strong> ${formatDateTime(record.timestamp)}</p>
            ${record.latitude && record.longitude ? 
                `<p><strong>Location:</strong> ${record.latitude.toFixed(4)}, ${record.longitude.toFixed(4)}</p>` : 
                ''}
            ${record.altitude ? `<p><strong>Altitude:</strong> ${record.altitude} m</p>` : ''}
            ${record.file_path ? `<p><strong>File:</strong> ${record.file_path}</p>` : ''}
            ${record.data_values ? 
                `<details>
                    <summary>Data Values</summary>
                    <pre>${JSON.stringify(record.data_values, null, 2)}</pre>
                </details>` : 
                ''}
            <div class="data-meta">
                Created: ${formatDateTime(record.created_at)}
                ${record.file_size ? ` | Size: ${formatFileSize(record.file_size)}` : ''}
            </div>
        </div>
    `).join('');
    
    dataList.innerHTML = recordsHTML;
}

function displayPagination(pagination) {
    const paginationDiv = document.getElementById('pagination');
    
    if (pagination.pages <= 1) {
        paginationDiv.innerHTML = '';
        return;
    }
    
    let paginationHTML = '';
    
    // Previous button
    if (pagination.has_prev) {
        paginationHTML += `<button onclick="goToPage(${pagination.page - 1})">← Previous</button>`;
    }
    
    // Page info
    paginationHTML += `
        <span class="page-info">
            Page ${pagination.page} of ${pagination.pages} 
            (${pagination.total} total records)
        </span>
    `;
    
    // Next button
    if (pagination.has_next) {
        paginationHTML += `<button onclick="goToPage(${pagination.page + 1})">Next →</button>`;
    }
    
    paginationDiv.innerHTML = paginationHTML;
}

function goToPage(page) {
    if (Object.keys(currentFilters).length > 0) {
        loadFilteredData(page);
    } else {
        loadAllData(page);
    }
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Check URL parameters on page load
document.addEventListener('DOMContentLoaded', function() {
    // Add status display element if it doesn't exist
    if (!document.getElementById('data-status')) {
        const statusDiv = document.createElement('div');
        statusDiv.id = 'data-status';
        statusDiv.className = 'status-display';
        document.querySelector('.container').appendChild(statusDiv);
    }
    
    // Check for mission parameter in URL
    const urlParams = new URLSearchParams(window.location.search);
    const missionParam = urlParams.get('mission');
    
    if (missionParam) {
        document.getElementById('mission-filter').value = missionParam;
        loadFilteredData();
    }
});