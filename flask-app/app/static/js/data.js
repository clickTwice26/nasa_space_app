// Data Explorer page JavaScript

let currentPage = 1;
let currentFilters = {};

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